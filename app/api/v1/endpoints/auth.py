# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.models.token import Token # Importa Token de app.models.token
from app.models.user import UserCreate, User, UserInDB # Importa os modelos de usuário

# Importa as funções de segurança e o fake_users_db do security.py
from app.core.security import authenticate_user, create_access_token, get_password_hash, fake_users_db, get_user_from_db

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    access_token = create_access_token(data={"sub": user.username}) # Acessa via user.username
    return {"access_token": access_token, "token_type": "bearer"}

# ==========================================================
# NOVO ENDPOINT DE TESTE - REMOVER DEPOIS QUE FUNCIONAR
@router.get("/test-auth-route")
def test_auth_route():
    return {"message": "Rota de teste em auth.py funcionando!"}
# ==========================================================

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_new_user(user_in: UserCreate):
    # TESTE RECARREGAMENTO
    # Verifica se o username já existe
    if get_user_from_db(user_in.username): # Usa a função get_user_from_db
        raise HTTPException(status_code=400, detail="Nome de usuário já registrado")

    # Hasheia a senha
    hashed_password = get_password_hash(user_in.password)

    # Converte o UserCreate para UserInDB para armazenar
    # Use .dict() com exclude_unset=True para pegar apenas os campos definidos pelo usuário
    user_data = user_in.model_dump(exclude_unset=True) # use .model_dump() para Pydantic v2+
    user_data["hashed_password"] = hashed_password
    user_data["disabled"] = False # Garante que o novo usuário não está desabilitado

    # Cria uma instância de UserInDB para garantir a estrutura
    new_user_in_db = UserInDB(**user_data)

    # Adiciona ao fake_users_db (diretamente no dicionário)
    fake_users_db[new_user_in_db.username] = new_user_in_db.model_dump() # Armazena como dict

    # Retorna o modelo User (sem a senha hash)
    # Cuidado para não retornar o hashed_password!!
    return User(**new_user_in_db.model_dump(exclude={'hashed_password'})) # Retorna User sem o hash