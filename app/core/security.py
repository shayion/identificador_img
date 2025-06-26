# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select # <-- NOVO: Importa Session e select do SQLModel

from app.models.user import UserInDB # Importa o modelo SQLModel UserInDB
from app.database import get_session # <-- NOVO: Importa a dependência de sessão do DB

# ATENÇÃO: Essas informações deveriam vir de variáveis de ambiente (.env) em produção!
SECRET_KEY = "sua_chave_secreta_super_segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# REMOVIDO: fake_users_db não será mais usado aqui, pois usaremos o DB real.
# fake_users_db = { ... }

# REMOVIDO: fake_refresh_tokens_db não será mais usado aqui, pois será armazenado em UserInDB.
# fake_refresh_tokens_db = {}


# ATUALIZADO: Função para obter usuário do banco de dados real
# Recebe uma sessão de banco de dados como parâmetro
def get_user_from_db(db: Session, username: str) -> Optional[UserInDB]:
    statement = select(UserInDB).where(UserInDB.username == username)
    user = db.exec(statement).first()
    return user

# ATUALIZADO: authenticate_user agora usa a sessão do DB
def authenticate_user(db: Session, username: str, password: str):
    user = get_user_from_db(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ATUALIZADO: create_refresh_token agora salva o hash no UserInDB
def create_refresh_token(db: Session, data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS) # Duração maior
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # NOVO: Salva o hash do refresh token no campo refresh_token_hash do usuário
    username = data["sub"]
    user = get_user_from_db(db, username)
    if user:
        user.refresh_token_hash = get_password_hash(encoded_jwt)
        db.add(user) # Adiciona o usuário modificado à sessão
        db.commit() # Salva as mudanças no DB
        db.refresh(user) # Atualiza o objeto user com os dados do DB
    else:
        # Isso não deveria acontecer se o usuário acabou de logar
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Usuário não encontrado para salvar refresh token.")

    return encoded_jwt

# ATUALIZADO: get_current_user agora usa a sessão do DB
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session) # <-- NOVO: Injeta a sessão do DB
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_from_db(db, username) # <-- Passa a sessão para a função
    if user is None:
        raise credentials_exception
    return user

# ATUALIZADO: get_current_user_from_refresh_token agora usa a sessão do DB
async def get_current_user_from_refresh_token(
    refresh_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session) # <-- NOVO: Injeta a sessão do DB
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar o refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Verifica se o refresh token é válido (hash armazenado bate com o token)
    user = get_user_from_db(db, username) # <-- Passa a sessão para a função
    if not user or not user.refresh_token_hash or not verify_password(refresh_token, user.refresh_token_hash):
        raise credentials_exception

    return user