from pydantic import BaseModel
from typing import Optional

fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrador",
        "email": "admin@email.com",
        "hashed_password": "$pbkdf2-sha256$29000$hTDmnBOC8J6TUkppjdGacw$7bqLZ9U5LHXTORmYltHf49J0pZZgtcNG2jTE2bziBLE",  # senha: admin123
        "disabled": False,
    }
}

def get_user(db, username: str):
    return db.get(username)

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

