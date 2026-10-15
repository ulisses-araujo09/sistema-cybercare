from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import urlsplit, parse_qs


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'sqlite:///./cybercare.db'
    jwt_secret: str = ''
    environment: str = 'local'
    demo_mode: bool = True
    seed_demo: bool = False
    cors_origins: str = 'http://localhost:5173,http://127.0.0.1:5173'
    privacy_threshold: int = 5
    retention_days: int = 30
    support_name: str = ''
    support_contact: str = ''

    def validate_runtime(self):
        if len(self.jwt_secret) < 32:
            raise RuntimeError('Configure JWT_SECRET com pelo menos 32 caracteres.')
        if not self.demo_mode:
            raise RuntimeError('Este MVP permite somente demonstrações fictícias.')
        if self.privacy_threshold < 5 or self.retention_days < 1:
            raise RuntimeError('Limiar mínimo 5 e retenção positiva são obrigatórios.')
        if self.environment != 'local' and not self.database_url.startswith(('postgresql', 'postgres')):
            raise RuntimeError('Use PostgreSQL no ambiente hospedado.')
        if self.environment != 'local' and parse_qs(urlsplit(self.database_url).query).get('sslmode', [''])[0] not in {'require', 'verify-ca', 'verify-full'}:
            raise RuntimeError('Use uma conexão PostgreSQL com TLS: sslmode=require ou verificação de certificado.')
        origins = self.cors_origins.split(',')
        if '*' in origins or (self.environment != 'local' and any(not o.startswith('https://') for o in origins)):
            raise RuntimeError('Configure origens explícitas e HTTPS na hospedagem.')


@lru_cache
def get_settings():
    return Settings()
