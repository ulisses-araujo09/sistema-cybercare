"""Preparação local; cria segredos aleatórios somente em arquivos ignorados."""
from pathlib import Path
import secrets
from dotenv import dotenv_values


def prepare():
    env = Path('.env')
    if not env.exists():
        values = dotenv_values('.env.example')
        values['JWT_SECRET'] = secrets.token_urlsafe(48)
        values['DEMO_STAFF_PASSWORD'] = secrets.token_urlsafe(18)
        values['DEMO_MANAGER_PASSWORD'] = secrets.token_urlsafe(18)
        env.write_text('\n'.join(f'{k}={v or ""}' for k, v in values.items()) + '\n', encoding='utf-8')
    values = dotenv_values(env)
    for name in ('DEMO_STAFF_PASSWORD', 'DEMO_MANAGER_PASSWORD'):
        if not values.get(name):
            raise RuntimeError(f'Configure {name} no arquivo .env antes de preparar a demonstração.')
    Path('../demo-acessos.txt').write_text(
        'CYBERCARE — ACESSOS LOCAIS DE DEMONSTRAÇÃO\nNão publicar nem enviar ao repositório.\n\n'
        f'Socioemocional: socioemocional@demo.cybercare.local\nSenha: {values["DEMO_STAFF_PASSWORD"]}\n\n'
        f'Gestão: gestao@demo.cybercare.local\nSenha: {values["DEMO_MANAGER_PASSWORD"]}\n', encoding='utf-8')
    print('Ambiente local preparado. Consulte demo-acessos.txt para as contas fictícias.')


if __name__ == '__main__':
    prepare()
