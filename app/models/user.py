# app/models/user.py
from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel # Mantenha BaseModel para UserCreate e Token

# UserInDB agora herda de SQLModel e Field para definir colunas do DB
class UserInDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    disabled: bool = False

    refresh_token_hash: Optional[str] = Field(default=None)

    images: List["Image"] = Relationship(back_populates="owner")


# User é o modelo que será retornado pela API (não inclui a senha hash)
class User(BaseModel): # User continua sendo um BaseModel para a resposta da API
    username: str
    disabled: Optional[bool] = None
    # full_name: Optional[str] = None
    # email: Optional[EmailStr] = None

# UserCreate é o modelo para criar um novo usuário (recebe a senha em texto claro)
class UserCreate(BaseModel): # UserCreate continua sendo um BaseModel para a entrada da API
    username: str
    password: str
    # full_name: Optional[str] = None
    # email: Optional[EmailStr] = None


class Image(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(index=True)  # Nome original do arquivo
    filepath: str = Field(index=True, unique=True)  # Caminho completo da imagem salva no disco
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)  # Data e hora do upload

    # Chave estrangeira para o usuário que enviou a imagem
    owner_id: Optional[int] = Field(default=None, foreign_key="userindb.id")

    # Relação com o modelo User (UserInDB)
    # back_populates cria a relação inversa no modelo UserInDB
    owner: Optional[UserInDB] = Relationship(back_populates="images")

    # Relação com as labels geradas pelo Google Vision
    labels: List["ImageLabel"] = Relationship(back_populates="image")


class ImageLabel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str = Field(index=True)  # A label retornada pelo Google Vision
    score: float  # A confiança da label

    # Chave estrangeira para a imagem à qual esta label pertence
    image_id: Optional[int] = Field(default=None, foreign_key="image.id")

    # Relação com o modelo Image
    image: Optional[Image] = Relationship(back_populates="labels")