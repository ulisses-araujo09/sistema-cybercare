import secrets
from contextlib import asynccontextmanager
from datetime import date, datetime, time, timedelta, timezone
import hmac
from fastapi import FastAPI, Depends, HTTPException, Request, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .config import get_settings
from .db import get_db
from .models import User, Report, ReportEvent, AuditEvent, QuizQuestion, RevokedToken, Role, Category, Status, now
from .schemas import ReportCreate, Lookup, Login, StatusUpdate, Answer
from .security import secret_hash, verify_password, dummy_hash, issue_token, current_user, require_role, rate_limit, decode_token, bearer


@asynccontextmanager
async def lifespan(app):
    get_settings().validate_runtime()
    yield


app = FastAPI(title='CyberCare — API demonstrativa', version='1.0.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=get_settings().cors_origins.split(','),
                   allow_methods=['GET', 'POST', 'PATCH'], allow_headers=['Authorization', 'Content-Type'])


@app.middleware('http')
async def privacy_headers(request, call_next):
    length = request.headers.get('content-length')
    if length and (not length.isdigit() or int(length) > 32768):
        return JSONResponse({'detail': 'Requisição muito grande.'}, status_code=413)
    # Limite inclusive para corpos enviados sem Content-Length.
    chunks = bytearray()
    async for chunk in request.stream():
        chunks.extend(chunk)
        if len(chunks) > 32768:
            return JSONResponse({'detail': 'Requisição muito grande.'}, status_code=413)
    request._body = bytes(chunks)
    response = await call_next(request)
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # Não refletir o conteúdo sensível recebido em erros ou logs.
    return JSONResponse({'detail': 'Confira os campos, os limites de texto e a confirmação de dados fictícios.'}, status_code=422)


@app.exception_handler(SQLAlchemyError)
async def database_error(request, exc):
    return JSONResponse({'detail': 'Não foi possível acessar os registros. Tente novamente em instantes.'}, status_code=503)


def audit(db, user, action, target=None):
    db.add(AuditEvent(actor_id=user.id, action=action, target_id=target))


def public_report(report):
    return {'protocol': report.protocol, 'status': report.status, 'created_at': report.created_at,
            'updated_at': report.updated_at, 'events': [{'status': e.status, 'created_at': e.created_at} for e in report.events]}


def private_report(report):
    return {**public_report(report), 'id': report.id, 'category': report.category, 'reporter_type': report.reporter_type,
            'description': report.description, 'location_optional': report.location_optional,
            'identification_optional': report.identification_optional,
            'events': [{'status': e.status, 'created_at': e.created_at, 'note_private_optional': e.note_private_optional} for e in report.events]}


def fresh_reports():
    return select(Report).where(Report.created_at >= now() - timedelta(days=get_settings().retention_days))


@app.get('/api/health')
def health(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {'status': 'ok', 'demo': True}


@app.get('/api/config')
def config():
    settings = get_settings()
    return {'demo': True, 'support_name': settings.support_name, 'support_contact': settings.support_contact,
            'retention_days': settings.retention_days}


@app.post('/api/reports', status_code=201)
def create_report(payload: ReportCreate, request: Request, db: Session = Depends(get_db)):
    rate_limit(db, request, 'create', 5)
    secret = secrets.token_urlsafe(32)
    report = Report(protocol='CYB-' + secrets.token_hex(12).upper(), access_secret_hash=secret_hash(secret),
                    reporter_type=payload.reporter_type, category=payload.category,
                    description=payload.description, location_optional=payload.location_optional or None,
                    identification_optional=payload.identification_optional or None)
    report.events.append(ReportEvent(status=Status.recebida))
    db.add(report)
    db.commit()
    return {'protocol': report.protocol, 'secret': secret, 'status': report.status}


@app.post('/api/reports/lookup')
def lookup(payload: Lookup, request: Request, db: Session = Depends(get_db)):
    rate_limit(db, request, 'lookup', 10)
    report = db.scalar(fresh_reports().where(Report.protocol == payload.protocol.upper()))
    expected = report.access_secret_hash if report else '0' * 64
    valid = hmac.compare_digest(expected, secret_hash(payload.secret))
    if not report or not valid:
        raise HTTPException(404, 'Protocolo ou chave inválidos, ou registro expirado.')
    return public_report(report)


@app.post('/api/auth/login')
def login(payload: Login, request: Request, db: Session = Depends(get_db)):
    rate_limit(db, request, 'login', 10)
    rate_limit(db, request, 'account', 5, payload.email.lower())
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    valid = verify_password(user.password_hash if user else dummy_hash, payload.password)
    if not user or not user.active or not valid:
        raise HTTPException(401, 'E-mail ou senha inválidos.')
    audit(db, user, 'login')
    db.commit()
    return {'access_token': issue_token(user), 'token_type': 'bearer', 'role': user.role, 'expires_in': 1200}


@app.get('/api/auth/me')
def me(user=Depends(current_user)):
    return {'role': user.role, 'email': user.email}


@app.post('/api/auth/logout')
def logout(user=Depends(current_user), credentials=Depends(bearer), db: Session = Depends(get_db)):
    claims = decode_token(credentials.credentials)
    db.add(RevokedToken(id=claims['jti'], expires_at=datetime.fromtimestamp(claims['exp'], timezone.utc)))
    audit(db, user, 'logout')
    db.commit()
    return {'message': 'Sessão encerrada.'}


@app.get('/api/staff/reports')
def staff_reports(page: int = Query(1, ge=1), status: Status | None = None,
                  user=Depends(require_role(Role.socioemocional)), db: Session = Depends(get_db)):
    query = fresh_reports()
    if status:
        query = query.where(Report.status == status)
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    reports = db.scalars(query.order_by(Report.created_at.desc()).offset((page - 1) * 20).limit(20)).all()
    audit(db, user, 'listar_casos')
    db.commit()
    return {'total': total, 'page': page, 'items': [{'id': r.id, 'protocol': r.protocol, 'status': r.status,
                                                 'category': r.category, 'created_at': r.created_at} for r in reports]}


def get_report(db, report_id):
    report = db.scalar(fresh_reports().where(Report.id == report_id))
    if not report:
        raise HTTPException(404, 'Registro não encontrado ou expirado.')
    return report


@app.get('/api/staff/reports/{report_id}')
def staff_detail(report_id: str, user=Depends(require_role(Role.socioemocional)), db: Session = Depends(get_db)):
    report = get_report(db, report_id)
    audit(db, user, 'consultar_caso', report.id)
    db.commit()
    return private_report(report)


@app.patch('/api/staff/reports/{report_id}/status')
def change_status(report_id: str, payload: StatusUpdate, user=Depends(require_role(Role.socioemocional)), db: Session = Depends(get_db)):
    report = db.scalar(fresh_reports().where(Report.id == report_id).with_for_update())
    if not report:
        raise HTTPException(404, 'Registro não encontrado ou expirado.')
    order = list(Status)
    if order.index(payload.status) != order.index(report.status) + 1:
        raise HTTPException(409, 'Selecione a próxima etapa do acompanhamento.')
    report.status = payload.status
    report.updated_at = now()
    report.events.append(ReportEvent(status=payload.status, note_private_optional=payload.note_private_optional,
                                     actor_id_optional=user.id))
    audit(db, user, 'atualizar_status', report.id)
    db.commit()
    return private_report(report)


@app.get('/api/management/metrics')
def metrics(start: date | None = None, end: date | None = None, category: Category | None = None,
            user=Depends(require_role(Role.gestao)), db: Session = Depends(get_db)):
    if start and end and start > end:
        raise HTTPException(422, 'A data inicial deve anteceder a final.')
    query = select(Report.category, Report.status).where(Report.created_at >= now() - timedelta(days=get_settings().retention_days))
    if start:
        query = query.where(Report.created_at >= datetime.combine(start, time.min, timezone.utc))
    if end:
        query = query.where(Report.created_at < datetime.combine(end + timedelta(days=1), time.min, timezone.utc))
    if category:
        query = query.where(Report.category == category)
    subset = query.subquery()
    total = db.scalar(select(func.count()).select_from(subset))
    threshold = get_settings().privacy_threshold
    # Arredondamento por faixas e supressão complementar: não expor total exato nem permitir
    # deduzir grupos pequenos subtraindo totais ou combinando filtros.
    def band(count):
        if count < threshold:
            return {'range': f'Menos de {threshold}', 'lower': None, 'suppressed': True}
        low = (count // threshold) * threshold
        return {'range': f'{low}–{low + threshold - 1}', 'lower': low, 'suppressed': False}
    def breakdown(values, attr):
        column = getattr(subset.c, attr)
        grouped = dict(db.execute(select(column, func.count()).group_by(column)).all())
        counts = {v.value: grouped.get(v, 0) for v in values}
        if any(0 < n < threshold for n in counts.values()):
            return [{'label': v.value, **{'range': 'Suprimido', 'lower': None, 'suppressed': True}} for v in values]
        return [{'label': v.value, **band(counts[v.value])} for v in values]
    audit(db, user, 'consultar_metricas')
    db.commit()
    return {'demo': True, 'threshold': threshold, 'total': band(total),
            'categories': breakdown(Category, 'category'), 'statuses': breakdown(Status, 'status'),
            'privacy_note': f'Faixas de {threshold} registros e supressão de grupos pequenos; filtros não representam estatísticas reais.'}


@app.get('/api/quiz/questions')
def questions(db: Session = Depends(get_db)):
    return [{'id': q.id, 'question': q.question, 'options': q.options_json} for q in db.scalars(
        select(QuizQuestion).where(QuizQuestion.active).order_by(QuizQuestion.id)).all()]


@app.post('/api/quiz/questions/{question_id}/answer')
def answer(question_id: str, payload: Answer, request: Request, db: Session = Depends(get_db)):
    rate_limit(db, request, 'quiz', 60)
    question = db.get(QuizQuestion, question_id)
    if not question or not question.active:
        raise HTTPException(404, 'Pergunta não encontrada.')
    if payload.option_index >= len(question.options_json):
        raise HTTPException(422, 'Escolha uma alternativa válida.')
    return {'correct': payload.option_index == question.correct_index, 'explanation': question.explanation}
