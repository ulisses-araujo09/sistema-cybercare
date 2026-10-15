"""Carga explícita, idempotente e exclusivamente fictícia. Senhas via ambiente."""
import os
from sqlalchemy import select
from .db import SessionLocal
from .models import User, Report, ReportEvent, QuizQuestion, Role, Category, Reporter, Status
from .security import hasher, secret_hash
from .config import get_settings
import secrets
from dotenv import load_dotenv

QUESTIONS = [
    ('Ao presenciar humilhações repetidas contra um colega, o que fazer?',
     ['Compartilhar para que todos vejam', 'Apoiar a pessoa e procurar um adulto de confiança', 'Incentivar as provocações'], 1,
     'Apoie sem se expor a riscos. Procure um adulto de confiança e evite ampliar a humilhação.'),
    ('Compartilhar imagens humilhantes de alguém sem autorização pode causar danos?',
     ['Sim, inclusive à privacidade e ao bem-estar', 'Não, na internet tudo é permitido'], 0,
     'O compartilhamento pode causar danos. Não repasse imagens humilhantes e busque orientação.'),
    ('Uma pessoa que sofre bullying tem culpa pelo que acontece?', ['Sim', 'Não'], 1,
     'A responsabilidade pela agressão é de quem a pratica. Toda pessoa merece respeito e acolhimento.'),
    ('Qual atitude contribui para uma convivência antirracista?',
     ['Tratar ofensas racistas como brincadeira', 'Respeitar identidades e buscar ajuda diante de discriminação'], 1,
     'Respeitar as diferenças e enfrentar a discriminação de forma segura fortalece uma cultura de paz.'),
    ('Como agir diante de ataques na internet?',
     ['Retribuir as ameaças', 'Pedir ajuda e orientação sobre preservação segura de evidências', 'Divulgar dados da pessoa'], 1,
     'Evite responder com agressões. Procure apoio e orientação para bloquear, denunciar na plataforma e preservar evidências com segurança.')
]


def seed():
    load_dotenv()
    get_settings().validate_runtime()
    with SessionLocal() as db:
        for role, variable in [(Role.socioemocional, 'DEMO_STAFF_PASSWORD'), (Role.gestao, 'DEMO_MANAGER_PASSWORD')]:
            email = f'{role.value}@demo.cybercare.local'
            if not db.scalar(select(User).where(User.email == email)):
                password = os.environ.get(variable, '')
                if len(password) < 12:
                    raise RuntimeError(f'Configure {variable} com pelo menos 12 caracteres. Nenhuma senha padrão é fornecida.')
                db.add(User(email=email, role=role, password_hash=hasher.hash(password)))
        for index, (question, options, correct, explanation) in enumerate(QUESTIONS):
            if not db.get(QuizQuestion, f'demo-quiz-{index+1}'):
                db.add(QuizQuestion(id=f'demo-quiz-{index+1}', question=question, options_json=options,
                                    correct_index=correct, explanation=explanation))
        for category in Category:
            for index in range(10):
                protocol = f'CYB-DEMO-{category.value.upper()}-{index:03}'
                if not db.scalar(select(Report).where(Report.protocol == protocol)):
                    status = Status.recebida if index < 5 else Status.em_analise
                    report = Report(protocol=protocol, access_secret_hash=secret_hash(secrets.token_urlsafe(32)),
                                    reporter_type=Reporter.anonimo, category=category,
                                    description='CASO FICTÍCIO PARA DEMONSTRAÇÃO: personagem inventado relata provocações repetidas em uma atividade escolar simulada.',
                                    location_optional='Espaço fictício', status=status)
                    report.events.append(ReportEvent(status=Status.recebida))
                    if status == Status.em_analise:
                        report.events.append(ReportEvent(status=status))
                    db.add(report)
        db.commit()
    print('Carga fictícia concluída. Use as senhas configuradas no ambiente. Não há chaves consultáveis para casos do seed.')


if __name__ == '__main__':
    seed()
