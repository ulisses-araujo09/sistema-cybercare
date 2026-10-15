"""Executar diariamente: python -m app.retention. Exclui conteúdo expirado e metadados temporários."""
from datetime import timedelta
from sqlalchemy import select, delete
from .db import SessionLocal
from .models import Report, AuditEvent, RateBucket, RevokedToken, now
from .config import get_settings


def purge():
    with SessionLocal() as db:
        cutoff = now() - timedelta(days=get_settings().retention_days)
        reports = db.scalars(select(Report).where(Report.created_at < cutoff)).all()
        for report in reports:
            db.delete(report)
        db.execute(delete(AuditEvent).where(AuditEvent.created_at < cutoff))
        db.execute(delete(RateBucket).where(RateBucket.expires_at < now()))
        db.execute(delete(RevokedToken).where(RevokedToken.expires_at < now()))
        db.commit()
        return len(reports)


if __name__ == '__main__':
    print(f'Retenção aplicada: {purge()} registros fictícios expirados removidos.')
