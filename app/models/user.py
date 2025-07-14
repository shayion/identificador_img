# app/models/user.py
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserInDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    disabled: bool = False
    refresh_token_hash: Optional[str] = Field(default=None)
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

    images: List["Image"] = Relationship(back_populates="owner")


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    disabled: Optional[bool] = None


class Image(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(index=True)
    filepath: str = Field(index=True, unique=True)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    owner_id: Optional[int] = Field(default=None, foreign_key="userindb.id")
    owner: Optional[UserInDB] = Relationship(back_populates="images")
    labels: List["ImageLabel"] = Relationship(back_populates="image")


class ImageLabel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str = Field(index=True)
    score: float

    image_id: Optional[int] = Field(default=None, foreign_key="image.id")
    image: Optional[Image] = Relationship(back_populates="labels")