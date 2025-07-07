# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends
# Importa os modelos User e UserInDB de app.models.user
from app.models.user import User, UserInDB
# Importa a dependência de get_current_user (que já recebe a sessão do DB)
from app.api.v1.deps import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Usuários"]
)

@router.get("/me", response_model=User)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    """
    Retorna informações do usuário atualmente logado.
    O current_user é um objeto UserInDB vindo da dependência de autenticação.
    """
    # Converte o objeto UserInDB (do banco de dados) para o modelo de resposta User
    # Excluímos 'hashed_password', 'id' e 'refresh_token_hash' da resposta pública.
    return User.model_validate(current_user)