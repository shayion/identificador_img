# app/models/user.py
from typing import Optional
from sqlmodel import Field, SQLModel # Importe Field e SQLModel
from pydantic import BaseModel # Mantenha BaseModel para UserCreate e Token

# UserInDB agora herda de SQLModel e Field para definir colunas do DB
class UserInDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    disabled: bool = False

    refresh_token_hash: Optional[str] = Field(default=None)


# User é o modelo que será retornado pela API (não inclui a senha hash)
class User(BaseModel): # User continua sendo um BaseModel para a resposta da API
    username: str
    disabled: Optional[bool] = None

# UserCreate é o modelo para criar um novo usuário (recebe a senha em texto claro)
class UserCreate(BaseModel): # UserCreate continua sendo um BaseModel para a entrada da API
    username: str
    password: str