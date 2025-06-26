# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends
# Importa a dependência de get_current_user
from app.api.v1.deps import get_current_user
# Importa o modelo User
from app.models.user import User

router = APIRouter(
    prefix="/users",
    tags=["Usuários"]
)

@router.get("/me", response_model=User) # Adicionado response_model para tipagem de saída
async def read_users_me(current_user: User = Depends(get_current_user)): # current_user agora é tipado como User
    # current_user já é um modelo UserInDB (vindo de get_current_user),
    # mas queremos retornar apenas o modelo User (sem o hashed_password)
    return User(**current_user.model_dump())