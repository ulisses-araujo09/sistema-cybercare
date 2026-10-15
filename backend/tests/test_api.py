from datetime import timedelta
import jwt
from sqlalchemy import select
from app.models import Report, ReportEvent, AuditEvent, Role, Status, now
from app.security import secret_hash
from app.config import get_settings

PAYLOAD = {'category': 'cyberbullying', 'reporter_type': 'testemunha', 'description': 'Relato fictício: colegas inventados compartilham uma imagem humilhante.', 'fictitious_confirmation': True}


def create(client):
    response = client.post('/api/reports', json=PAYLOAD)
    assert response.status_code == 201
    return response.json()


def test_vertical_flow_and_private_data(client, db, auth):
    receipt = create(client)
    report = db.scalar(select(Report))
    assert report.access_secret_hash == secret_hash(receipt['secret'])
    assert receipt['secret'] not in report.access_secret_hash
    assert len(receipt['protocol']) >= 24
    assert client.post('/api/reports/lookup', json={'protocol': receipt['protocol']}).status_code == 422
    assert client.post('/api/reports/lookup', json={'protocol': receipt['protocol'], 'secret': 'wrong-secret-key'}).status_code == 404
    lookup = {'protocol': receipt['protocol'], 'secret': receipt['secret']}
    result = client.post('/api/reports/lookup', json=lookup).json()
    assert result['status'] == 'recebida'
    assert 'description' not in result and 'identification_optional' not in result
    staff = auth('socioemocional')
    cases = client.get('/api/staff/reports', headers=staff).json()
    detail = client.get(f'/api/staff/reports/{report.id}', headers=staff).json()
    assert detail['description'] == PAYLOAD['description']
    assert 'access_secret_hash' not in detail
    response = client.patch(f'/api/staff/reports/{report.id}/status', headers=staff,
                            json={'status': 'em_analise', 'note_private_optional': 'Nota exclusivamente interna.'})
    assert response.status_code == 200
    result = client.post('/api/reports/lookup', json=lookup).json()
    assert result['status'] == 'em_analise' and len(result['events']) == 2
    assert 'Nota exclusivamente interna' not in str(result)
    assert cases['total'] == 1
    assert PAYLOAD['description'] not in str([a.action for a in db.scalars(select(AuditEvent)).all()])


def test_rbac_and_authentication(client, auth, db):
    create(client)
    report = db.scalar(select(Report))
    manager = auth('gestao')
    staff = auth('socioemocional')
    for path in ['/api/staff/reports', f'/api/staff/reports/{report.id}', '/api/management/metrics']:
        assert client.get(path).status_code == 401
    assert client.get('/api/staff/reports', headers=manager).status_code == 403
    assert client.get(f'/api/staff/reports/{report.id}', headers=manager).status_code == 403
    assert client.patch(f'/api/staff/reports/{report.id}/status', headers=manager, json={'status': 'em_analise'}).status_code == 403
    assert client.get('/api/management/metrics', headers=staff).status_code == 403
    assert client.post('/api/auth/login', json={'email': 'gestao@test.local', 'password': 'errada'}).status_code == 401
    assert client.get('/api/auth/me', headers={'Authorization': 'Bearer invalid'}).status_code == 401
    assert client.post('/api/auth/logout', headers=manager).status_code == 200
    assert client.get('/api/auth/me', headers=manager).status_code == 401


def test_metrics_suppression(client, auth, db):
    for i in range(6):
        report = Report(protocol=f'test-{i}', access_secret_hash='x' * 64, category='bullying' if i < 5 else 'racismo',
                        reporter_type='anonimo', description='Texto fictício muito sensível para teste.')
        db.add(report)
    db.commit()
    result = client.get('/api/management/metrics', headers=auth('gestao')).json()
    assert result['total']['range'] == '5–9'
    assert all(v['suppressed'] for v in result['categories'])
    assert 'description' not in str(result) and 'protocol' not in str(result)
    filtered = client.get('/api/management/metrics?category=racismo', headers=auth('gestao')).json()
    assert filtered['total']['suppressed'] and filtered['total']['lower'] is None
    assert client.get('/api/management/metrics?start=2026-10-20&end=2026-10-01', headers=auth('gestao')).status_code == 422


def test_rate_limits_and_validation(client):
    for _ in range(5): create(client)
    assert client.post('/api/reports', json=PAYLOAD).status_code == 429
    for _ in range(10):
        assert client.post('/api/reports/lookup', json={'protocol': 'invalido', 'secret': 'invalid-key-value'}).status_code == 404
    assert client.post('/api/reports/lookup', json={'protocol': 'invalido', 'secret': 'invalid-key-value'}).status_code == 429
    assert client.post('/api/reports', json={**PAYLOAD, 'description': 'curto'}).status_code == 422
    assert client.post('/api/reports', json={**PAYLOAD, 'fictitious_confirmation': False}).status_code == 422
    result = client.post('/api/reports', json={**PAYLOAD, 'description': 'a' * 5001})
    assert result.status_code == 422 and 'a' * 50 not in result.text
    assert client.post('/api/reports', content='x' * 33000).status_code == 413


def test_quiz_validation_and_answer_hidden(client):
    response = client.get('/api/quiz/questions')
    assert response.status_code == 200
    assert 'correct_index' not in response.text and 'explanation' not in response.text
    assert client.post('/api/quiz/questions/q1/answer', json={'option_index': 1}).json()['correct']
    assert not client.post('/api/quiz/questions/q1/answer', json={'option_index': 0}).json()['correct']
    assert client.post('/api/quiz/questions/q1/answer', json={'option_index': 8}).status_code == 422


def test_status_order_expiry_and_headers(client, db, auth):
    receipt = create(client)
    report = db.scalar(select(Report))
    staff = auth('socioemocional')
    assert client.patch(f'/api/staff/reports/{report.id}/status', headers=staff, json={'status': 'encaminhada'}).status_code == 409
    report.created_at = now() - timedelta(days=31)
    db.commit()
    assert client.post('/api/reports/lookup', json={'protocol': receipt['protocol'], 'secret': receipt['secret']}).status_code == 404
    assert client.get('/api/staff/reports', headers=staff).json()['total'] == 0
    assert client.get('/api/health').headers['cache-control'] == 'no-store'
    denied = client.options('/api/reports', headers={'Origin': 'https://estranho.example', 'Access-Control-Request-Method': 'POST'})
    assert 'access-control-allow-origin' not in denied.headers


def test_token_expired_and_inactive(client, db, auth):
    headers = auth('socioemocional')
    from app.models import User
    user = db.get(User, 'socioemocional')
    token = jwt.encode({'sub': user.id, 'jti': 'expired', 'exp': now() - timedelta(minutes=1), 'iss': 'cybercare', 'aud': 'cybercare-escola'}, get_settings().jwt_secret, algorithm='HS256')
    assert client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'}).status_code == 401
    user.active = False
    db.commit()
    assert client.get('/api/auth/me', headers=headers).status_code == 401
