# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.models.token import Token
from app.models.user import UserCreate, User, UserInDB

# Importa as funções de segurança e o fake_users_db do security.py
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    fake_users_db,
    get_user_from_db,
    create_refresh_token, # Importado para ser usado no login
    get_current_user_from_refresh_token
)
from app.api.v1.deps import get_current_user # Importado para proteger o logout

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username}) # <-- NOVO: Cria o refresh token

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token} # <-- NOVO: Retorna o refresh token

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_new_user(user_in: UserCreate):
    # Verifica se o username já existe
    if get_user_from_db(user_in.username):
        raise HTTPException(status_code=400, detail="Nome de usuário já registrado")

    # Hasheia a senha
    hashed_password = get_password_hash(user_in.password)

    # Converte o UserCreate para UserInDB para armazenar
    user_data = user_in.model_dump(exclude_unset=True) # use .model_dump() para Pydantic v2+
    user_data["hashed_password"] = hashed_password
    user_data["disabled"] = False # Garante que o novo usuário não está desabilitado

    # Cria uma instância de UserInDB para garantir a estrutura
    new_user_in_db = UserInDB(**user_data)

    # Adiciona ao fake_users_db (diretamente no dicionário)
    fake_users_db[new_user_in_db.username] = new_user_in_db.model_dump() # Armazena como dict

    # Retorna o modelo User (sem a senha hash)
    return User(**new_user_in_db.model_dump(exclude={'hashed_password'}))

@router.post("/logout")
async def logout_user(current_user: UserInDB = Depends(get_current_user)):
    """
    Realiza o logout do usuário.
    Com JWT, o "logout" é primariamente uma ação do lado do cliente (descartar o token).
    Este endpoint pode ser expandido para revogar tokens de atualização ou invalidar tokens em uma blacklist.
    """
    # Em um sistema real, aqui você invalidaria o refresh token associado a este usuário
    # Por exemplo: fake_refresh_tokens_db.pop(current_user.username, None)
    return {"message": f"Usuário {current_user.username} deslogado com sucesso (descarte o token no cliente)."}

@router.post("/refresh", response_model=Token)
async def refresh_access_token(user_from_refresh: UserInDB = Depends(get_current_user_from_refresh_token)):
    """
    Obtém um novo access token usando um refresh token válido.
    """
    new_access_token = create_access_token(data={"sub": user_from_refresh.username})
    # O refresh token existente (que foi usado na requisição) pode ser re-emitido ou mantido,
    # dependendo da sua estratégia de rotação de refresh tokens.
    # Por simplicidade, retornamos o mesmo refresh token que foi usado,
    # mas o ideal seria gerar um NOVO refresh token aqui e invalidar o antigo.
    return {"access_token": new_access_token, "token_type": "bearer", "refresh_token": user_from_refresh.token}