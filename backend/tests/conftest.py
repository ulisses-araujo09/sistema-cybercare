import os
import secrets
os.environ['JWT_SECRET'] = secrets.token_urlsafe(48)
os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['DEMO_MODE'] = 'true'
os.environ['MAINTENANCE_ENABLED'] = 'false'
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.db import Base, get_db
from app.main import app
from app.models import User, Role, QuizQuestion
from app.security import hasher


@pytest.fixture
def db():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, expire_on_commit=False)
    with factory() as session:
        for role in Role:
            session.add(User(id=role.value, email=f'{role.value}@test.local', role=role, password_hash=hasher.hash('SenhaTesteFicticia!42')))
        session.add(QuizQuestion(id='q1', question='Como apoiar?', options_json=['Humilhar', 'Acolher'], correct_index=1, explanation='Acolher com respeito.'))
        session.commit()
        yield session
    engine.dispose()


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def auth(client):
    def headers(role):
        result = client.post('/api/auth/login', json={'email': f'{role}@test.local', 'password': 'SenhaTesteFicticia!42'})
        assert result.status_code == 200
        return {'Authorization': f"Bearer {result.json()['access_token']}"}
    return headers
