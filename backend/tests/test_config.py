import pytest
from app.config import Settings


def test_production_requires_postgres_tls_and_restricted_cors():
    values = dict(_env_file=None, jwt_secret='x'*48, environment='production',
                  database_url='postgresql://user:secret@demo.neon.tech/cybercare?sslmode=require',
                  cors_origins='https://cybercare.up.railway.app')
    Settings(**values).validate_runtime()
    for override in [dict(database_url='sqlite:///demo.db'),
                     dict(database_url='postgresql://user:secret@demo.neon.tech/cybercare'),
                     dict(cors_origins='*'), dict(cors_origins='http://example.com'),
                     dict(jwt_secret='short'), dict(demo_mode=False)]:
        with pytest.raises(RuntimeError):
            Settings(**{**values, **override}).validate_runtime()
