from datetime import timedelta
from sqlalchemy import select, func
from app.models import Report, ReportEvent, AuditEvent, RateBucket, Status, now, User, QuizQuestion
from app import retention, seed


def test_retention_removes_expired_content_and_keeps_recent(db, monkeypatch):
    old = Report(protocol='old-case', access_secret_hash='0'*64, reporter_type='anonimo', category='bullying', description='Caso fictício expirado.', created_at=now()-timedelta(days=31))
    old.events.append(ReportEvent(status=Status.recebida))
    recent = Report(protocol='new-case', access_secret_hash='1'*64, reporter_type='anonimo', category='bullying', description='Caso fictício recente.')
    db.add_all([old, recent, AuditEvent(action='expirada', created_at=now()-timedelta(days=31)), RateBucket(key='expired', count=1, expires_at=now()-timedelta(minutes=1))])
    db.commit()
    monkeypatch.setattr(retention, 'SessionLocal', lambda: db)
    assert retention.purge() == 1
    assert db.scalar(select(func.count()).select_from(Report)) == 1
    assert db.scalar(select(func.count()).select_from(ReportEvent)) == 0
    assert db.scalar(select(func.count()).select_from(AuditEvent)) == 0
    assert db.scalar(select(func.count()).select_from(RateBucket)) == 0


def test_seed_idempotent_and_no_default_password(db, monkeypatch):
    monkeypatch.setattr(seed, 'SessionLocal', lambda: db)
    monkeypatch.setenv('DEMO_STAFF_PASSWORD', 'SenhaFicticiaExclusiva!42')
    monkeypatch.setenv('DEMO_MANAGER_PASSWORD', 'OutraSenhaFicticia!43')
    seed.seed()
    seed.seed()
    assert db.scalar(select(func.count()).select_from(Report)) == 50
    assert db.scalar(select(func.count()).select_from(User)) == 4
    assert db.scalar(select(func.count()).select_from(QuizQuestion)) == 6
