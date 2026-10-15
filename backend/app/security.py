import hashlib
import hmac
import secrets
from datetime import timedelta
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .config import get_settings
from .db import get_db
from .models import RateBucket, RevokedToken, User, now

hasher = PasswordHasher()
dummy_hash = hasher.hash(secrets.token_urlsafe(32))
bearer = HTTPBearer(auto_error=False)


def secret_hash(secret: str):
    return hashlib.sha256(secret.encode()).hexdigest()


def verify_password(hashed, password):
    try:
        return hasher.verify(hashed, password)
    except VerificationError:
        return False


def issue_token(user):
    stamp = now()
    return jwt.encode({'sub': user.id, 'jti': secrets.token_hex(16), 'iat': stamp,
                       'exp': stamp + timedelta(minutes=20), 'iss': 'cybercare', 'aud': 'cybercare-escola'},
                      get_settings().jwt_secret, algorithm='HS256')


def decode_token(token):
    try:
        return jwt.decode(token, get_settings().jwt_secret, algorithms=['HS256'],
                          issuer='cybercare', audience='cybercare-escola', options={'require': ['exp', 'sub', 'jti']})
    except jwt.InvalidTokenError:
        raise HTTPException(401, 'Sessão inválida ou expirada. Entre novamente.')


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)):
    if not credentials:
        raise HTTPException(401, 'Entre com sua conta escolar.')
    claims = decode_token(credentials.credentials)
    user = db.get(User, claims['sub'])
    if not user or not user.active or db.get(RevokedToken, claims['jti']):
        raise HTTPException(401, 'Sessão inválida ou expirada. Entre novamente.')
    return user


def require_role(role):
    def authorize(user=Depends(current_user)):
        if user.role != role:
            raise HTTPException(403, 'Seu perfil não tem permissão para este recurso.')
        return user
    return authorize


def rate_limit(db, request: Request, scope: str, limit: int, identifier: str = ''):
    # IP usado somente transitoriamente: persiste HMAC rotativo por janela, nunca IP bruto.
    # Não confiar em X-Forwarded-For sem proxy configurado pelo operador.
    timestamp = int(now().timestamp())
    window = timestamp // 60
    source = identifier or (request.client.host if request.client else 'unknown')
    key = hmac.new(get_settings().jwt_secret.encode(), f'{scope}:{source}:{window}'.encode(), hashlib.sha256).hexdigest()
    expiry = now() + timedelta(minutes=2)
    updated = db.execute(update(RateBucket).where(RateBucket.key == key).values(count=RateBucket.count + 1))
    if not updated.rowcount:
        try:
            with db.begin_nested():
                db.add(RateBucket(key=key, count=1, expires_at=expiry))
                db.flush()
        except IntegrityError:
            db.execute(update(RateBucket).where(RateBucket.key == key).values(count=RateBucket.count + 1))
    db.commit()
    if db.scalar(select(RateBucket.count).where(RateBucket.key == key)) > limit:
        raise HTTPException(429, 'Muitas tentativas. Aguarde um minuto e tente novamente.', headers={'Retry-After': '60'})
