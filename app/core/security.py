# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Importa o modelo UserInDB para a estrutura do fake_users_db
from app.models.user import UserInDB

# ATENÇÃO: Essas informações deveriam vir de variáveis de ambiente (.env) em produção!
SECRET_KEY = "sua_chave_secreta_super_segura" # Mude isso em produção!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Contexto de senha
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Simulação de banco de dados de usuários (usando UserInDB para tipagem interna)
# Se você tiver mais campos em UserInDB, certifique-se de que os usuários no fake_users_db os tenham.
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrador",
        "email": "admin@email.com",
        "hashed_password": "$pbkdf2-sha256$29000$hTDmnBOC8J6TUkppjdGacw$7bqLZ9U5LHXTORmYltHf49J0pZZgtcNG2jTE2bziBLE",  # senha: admin123
        "disabled": False,
    }
}

# Função para obter usuário do "banco de dados"
def get_user_from_db(username: str): # Removido 'db' pois fake_users_db está aqui
    # Retorna uma CÓPIA do usuário para evitar modificações diretas no dicionário global
    # E para garantir que a saída seja consistente com UserInDB
    user_data = fake_users_db.get(username)
    if user_data:
        return UserInDB(**user_data) # Converte o dict em um modelo Pydantic
    return None

def authenticate_user(username: str, password: str):
    user = get_user_from_db(username) # Usa a função local
    if not user or not verify_password(password, user.hashed_password): # Acessa via .hashed_password
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
    user = get_user_from_db(username) # Usa a função local
    if user is None:
        raise credentials_exception
    return user