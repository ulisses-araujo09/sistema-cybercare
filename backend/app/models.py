import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


def now():
    return datetime.now(timezone.utc)


def identifier():
    return str(uuid.uuid4())


class Role(str, Enum):
    socioemocional = 'socioemocional'
    gestao = 'gestao'


class Category(str, Enum):
    bullying = 'bullying'
    cyberbullying = 'cyberbullying'
    racismo = 'racismo'
    ameaca = 'ameaca'
    outros = 'outros'


class Status(str, Enum):
    recebida = 'recebida'
    em_analise = 'em_analise'
    encaminhada = 'encaminhada'
    atendimento_realizado = 'atendimento_realizado'


class Reporter(str, Enum):
    anonimo = 'anonimo'
    vitima = 'vitima'
    testemunha = 'testemunha'


class User(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[Role] = mapped_column(SQLEnum(Role, native_enum=False))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Report(Base):
    __tablename__ = 'reports'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    protocol: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    access_secret_hash: Mapped[str] = mapped_column(String(64))
    reporter_type: Mapped[Reporter] = mapped_column(SQLEnum(Reporter, native_enum=False))
    identification_optional: Mapped[str | None] = mapped_column(String(120), nullable=True)
    category: Mapped[Category] = mapped_column(SQLEnum(Category, native_enum=False))
    location_optional: Mapped[str | None] = mapped_column(String(160), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[Status] = mapped_column(SQLEnum(Status, native_enum=False), default=Status.recebida)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    events: Mapped[list['ReportEvent']] = relationship(cascade='all, delete-orphan', order_by='ReportEvent.created_at')


class ReportEvent(Base):
    __tablename__ = 'report_events'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    report_id: Mapped[str] = mapped_column(ForeignKey('reports.id', ondelete='CASCADE'), index=True)
    status: Mapped[Status] = mapped_column(SQLEnum(Status, native_enum=False))
    note_private_optional: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor_id_optional: Mapped[str | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class QuizQuestion(Base):
    __tablename__ = 'quiz_questions'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    question: Mapped[str] = mapped_column(Text)
    options_json: Mapped[list] = mapped_column(JSON)
    correct_index: Mapped[int]
    explanation: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class AuditEvent(Base):
    __tablename__ = 'audit_events'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    action: Mapped[str] = mapped_column(String(60))
    target_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class RateBucket(Base):
    __tablename__ = 'rate_buckets'
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    count: Mapped[int]
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class RevokedToken(Base):
    __tablename__ = 'revoked_tokens'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
