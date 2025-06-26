# Arquivo: identificador_img/auth/auth.py

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# ATENÇÃO AQUI: Importação de user.py
# Se user.py está em identificador_img/models/user.py e auth.py está em identificador_img/auth/auth.py
# A importação deve ser relativa à raiz do projeto (onde o main.py está)
from models.user import get_user, fake_users_db

# Configuração
SECRET_KEY = "sua_chave_secreta_super_segura" # Mude isso para uma chave mais forte em produção!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Dependência do FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Contexto de senha
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = get_user(fake_users_db, username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) # Usando a constante definida
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Função para obter o usuário atual a partir do token (Adicionando, pois você vai precisar dela para proteger rotas)
async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    user = get_user(fake_users_db, username) # Supondo que get_user pode buscar o user por username
    if user is None:
        raise credentials_exception
    return user