# app/database.py
from typing import Generator

from sqlmodel import create_engine, Session, SQLModel # <-- NOVO: Importe SQLModel aqui

# NOVO: Importa os modelos UserInDB, Image e ImageLabel
# UserInDB é o modelo que se torna a tabela de usuários
from app.models.user import UserInDB, Image, ImageLabel # <-- ADICIONADO: Importe Image e ImageLabel

# URL do banco de dados SQLite. O arquivo 'database.db' será criado na raiz do projeto.
DATABASE_URL = "sqlite:///./database.db"

# Cria o motor do banco de dados. connect_args é necessário para SQLite.
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Cria as tabelas no banco de dados com base nos modelos SQLModel."""
    # SQLModel.metadata.create_all(engine) cria todas as tabelas
    # que foram definidas através dos modelos SQLModel (UserInDB, Image, ImageLabel).
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependência para obter uma sessão de banco de dados.
    Usada com `Depends()` nos endpoints do FastAPI.
    """
    with Session(engine) as session:
        yield session