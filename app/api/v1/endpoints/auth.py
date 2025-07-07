# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.models.token import Token
# Importa os modelos de usuário atualizados
from app.models.user import UserCreate, User, UserInDB

# Importa as funções de segurança
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_user_from_db,
    create_refresh_token,
    get_current_user_from_refresh_token
)
from app.api.v1.deps import get_current_user
from app.database import get_session

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(db, data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_new_user(user_in: UserCreate, db: Session = Depends(get_session)):
    # Verifica se o username já existe no DB
    if get_user_from_db(db, user_in.username):
        raise HTTPException(status_code=400, detail="Nome de usuário já registrado")

    # Hasheia a senha
    hashed_password = get_password_hash(user_in.password)

    # Cria o novo usuário como um modelo UserInDB
    user_to_db = UserInDB(
        username=user_in.username,
        hashed_password=hashed_password,
        full_name=user_in.full_name, # NOVO: Salva full_name
        email=user_in.email,         # NOVO: Salva email
        disabled=False,
    )

    # Adiciona e salva o usuário no DB
    db.add(user_to_db)
    db.commit()
    db.refresh(user_to_db) # Atualiza o objeto com o ID gerado pelo DB

    # Retorna o modelo User (sem a senha hash)
    # Usa model_dump com exclude para não retornar a senha hash e o ID do DB
    return User(**user_to_db.model_dump(exclude={'hashed_password', 'id', 'refresh_token_hash'}))

@router.post("/logout")
async def logout_user(current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_session)):
    if current_user:
        current_user.refresh_token_hash = None
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        return {"message": f"Usuário {current_user.username} deslogado com sucesso. Refresh token invalidado."}
    return {"message": "Deslogado. Refresh token já invalidado ou usuário não encontrado."}


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    user_from_refresh: UserInDB = Depends(get_current_user_from_refresh_token),
    db: Session = Depends(get_session)
):
    new_access_token = create_access_token(data={"sub": user_from_refresh.username})
    return {"access_token": new_access_token, "token_type": "bearer", "refresh_token": user_from_refresh.refresh_token_hash}