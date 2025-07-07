# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select  # <-- NOVO: Importa Session e select do SQLModel

from app.models.token import Token
from app.models.user import UserCreate, User, UserInDB  # Importa os modelos de usuário

# Importa as funções de segurança (sem fake_users_db)
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_user_from_db,
    create_refresh_token,
    get_current_user_from_refresh_token
)
from app.api.v1.deps import get_current_user
from app.database import get_session  # <-- NOVO: Importa a dependência de sessão do DB

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)


@router.post("/login", response_model=Token)
# ATUALIZADO: Injeta a sessão do DB
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_session)  # <-- NOVO: Injeta a sessão
):
    user = authenticate_user(db, form_data.username, form_data.password)  # <-- Passa a sessão
    if not user:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(db, data={"sub": user.username})  # <-- Passa a sessão

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
# ATUALIZADO: Injeta a sessão do DB
def register_new_user(user_in: UserCreate, db: Session = Depends(get_session)):  # <-- NOVO: Injeta a sessão
    # Verifica se o username já existe no DB
    if get_user_from_db(db, user_in.username):  # <-- Passa a sessão
        raise HTTPException(status_code=400, detail="Nome de usuário já registrado")

    # Hasheia a senha
    hashed_password = get_password_hash(user_in.password)

    # Cria o novo usuário como um modelo UserInDB
    user_to_db = UserInDB(
        username=user_in.username,
        hashed_password=hashed_password,
        disabled=False,
        # Campos opcionais, se existirem em UserCreate, adicione aqui
        # full_name=user_in.full_name,
        # email=user_in.email,
    )

    # Adiciona e salva o usuário no DB
    db.add(user_to_db)
    db.commit()
    db.refresh(user_to_db)  # Atualiza o objeto com o ID gerado pelo DB

    # Retorna o modelo User (sem a senha hash)
    return User(**user_to_db.model_dump(exclude={'hashed_password', 'id', 'refresh_token_hash'}))  # <-- Usa model_validate para converter UserInDB para User


@router.post("/logout")
# ATUALIZADO: Injeta a sessão do DB e atualiza a lógica
async def logout_user(current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_session)):
    """
    Realiza o logout do usuário.
    Com JWT, o "logout" é primariamente uma ação do lado do cliente (descartar o token).
    Para invalidar o refresh token no servidor, precisamos limpá-lo do DB.
    """
    # NOVO: Remove o refresh token hash do usuário no DB para invalidá-lo
    if current_user:
        current_user.refresh_token_hash = None  # Limpa o hash do refresh token
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        return {"message": f"Usuário {current_user.username} deslogado com sucesso. Refresh token invalidado."}
    return {"message": "Deslogado. Refresh token já invalidado ou usuário não encontrado."}


@router.post("/refresh", response_model=Token)
# ATUALIZADO: Injeta a sessão do DB
async def refresh_access_token(
        user_from_refresh: UserInDB = Depends(get_current_user_from_refresh_token),
        db: Session = Depends(get_session)  # <-- NOVO: Injeta a sessão
):
    """
    Obtém um novo access token usando um refresh token válido.
    """
    new_access_token = create_access_token(data={"sub": user_from_refresh.username})

    # ATENÇÃO: Numa estratégia de rotação de refresh tokens, você geraria um NOVO refresh token aqui
    # e INVALIDARIA o refresh token antigo (que foi usado na requisição).
    # Para simplicidade agora, vamos apenas retornar o novo access token e o refresh token existente.
    # Se quiser implementar a rotação, seria:
    # new_refresh_token = create_refresh_token(db, data={"sub": user_from_refresh.username})
    # return {"access_token": new_access_token, "token_type": "bearer", "refresh_token": new_refresh_token}

    return {"access_token": new_access_token, "token_type": "bearer",
            "refresh_token": user_from_refresh.refresh_token_hash}  # <-- Retorna o refresh token hash (que foi o original)