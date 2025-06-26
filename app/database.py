# app/database.py
from typing import Generator

from sqlmodel import create_engine, Session

# URL do banco de dados SQLite. O arquivo 'database.db' será criado na raiz do projeto.
# Se você quiser que ele fique em outro lugar (ex: dentro de 'app/'), ajuste o caminho.
DATABASE_URL = "sqlite:///./database.db"

# Cria o motor do banco de dados. connect_args é necessário para SQLite.
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Cria as tabelas no banco de dados com base nos modelos SQLModel."""
    # Importar todos os modelos aqui garante que o SQLModel os "veja"
    # e crie as tabelas correspondentes.
    # Por enquanto, só temos o User, mas adicionaremos Image e Label depois.
    from app.models.user import User # Importe User aqui

    # SQLModel.metadata.create_all(engine) cria todas as tabelas
    # que foram definidas através dos modelos SQLModel.
    # Isso deve ser chamado apenas uma vez na inicialização da aplicação.
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependência para obter uma sessão de banco de dados.
    Usada com `Depends()` nos endpoints do FastAPI.
    """
    with Session(engine) as session:
        yield session