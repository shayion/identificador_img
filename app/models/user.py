# app/models/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr

# Modelo para a criação de um novo usuário (o que o cliente envia)
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

# Modelo para a resposta de um usuário (o que a API retorna, sem a senha hash)
class User(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

# Modelo de como o usuário é armazenado no "banco de dados"
class UserInDB(User):
    hashed_password: str