"""Inicialização Railway: validar ambiente, migrar, carregar demo explicitamente e servir."""
import os
from alembic import command
from alembic.config import Config
import uvicorn
from .config import get_settings


def main():
    settings = get_settings()
    settings.validate_runtime()
    command.upgrade(Config('alembic.ini'), 'head')
    if settings.seed_demo:
        from .seed import seed
        seed()
    uvicorn.run('app.main:app', host='0.0.0.0', port=int(os.environ.get('PORT', '8000')),
                access_log=False, proxy_headers=False)


if __name__ == '__main__':
    main()
