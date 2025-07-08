# app/models/user.py
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel, EmailStr # IMPORTAÇÃO CORRETA E ATIVA
from datetime import datetime # Importado para o modelo Image (para campos de data/hora)

# Modelo de como o usuário é armazenado no "banco de dados"
class UserInDB(SQLModel, table=True): # table=True indica que esta classe é uma tabela do DB
    id: Optional[int] = Field(default=None, primary_key=True) # ID auto-incrementado
    username: str = Field(index=True, unique=True) # Campo indexado e único
    hashed_password: str
    disabled: bool = False
    refresh_token_hash: Optional[str] = Field(default=None) # Campo para o hash do refresh token
    full_name: Optional[str] = None # ATIVO: Descomentado
    email: Optional[EmailStr] = None # ATIVO: Descomentado

    # Relação com as imagens que o usuário enviou
    images: List["Image"] = Relationship(back_populates="owner")


# Modelo para a criação de um novo usuário (o que o cliente envia)
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None # ATIVO: Descomentado
    email: Optional[EmailStr] = None # ATIVO: Descomentado


# Modelo para a resposta de um usuário (o que a API retorna, sem a senha hash)
class User(BaseModel): # User continua sendo um BaseModel para a resposta da API
    username: str
    full_name: Optional[str] = None # ATIVO: Descomentado
    email: Optional[EmailStr] = None # ATIVO: Descomentado
    disabled: Optional[bool] = None


# Modelo para Imagens (Também é uma tabela do DB)
class Image(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(index=True) # Nome original do arquivo
    filepath: str = Field(index=True, unique=True) # Caminho completo da imagem salva no disco
    uploaded_at: datetime = Field(default_factory=datetime.utcnow) # Data e hora do upload

    # Chave estrangeira para o usuário que enviou a imagem
    owner_id: Optional[int] = Field(default=None, foreign_key="userindb.id")

    # Relação com o modelo User (UserInDB)
    owner: Optional[UserInDB] = Relationship(back_populates="images")

    # Relação com as labels geradas pelo Google Vision
    labels: List["ImageLabel"] = Relationship(back_populates="image")


# Modelo para Labels da Imagem (Também é uma tabela do DB)
class ImageLabel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str = Field(index=True)
    score: float

    image_id: Optional[int] = Field(default=None, foreign_key="image.id")

    # Relação com o modelo Image
    image: Optional[Image] = Relationship(back_populates="labels")