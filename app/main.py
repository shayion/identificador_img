# app/main.py
from fastapi import FastAPI
from app.api.v1.endpoints import auth, users, vision
from app.database import create_db_and_tables # <-- NOVO: Importa a função de criação de tabelas

app = FastAPI(
    title="Minha API de Análise de Imagem",
    description="API para autenticação de usuários e análise de imagens com Google Cloud Vision.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# NOVO: Evento de startup para criar as tabelas do banco de dados
@app.on_event("startup")
def on_startup():
    print("Criando tabelas do banco de dados...")
    create_db_and_tables()
    print("Tabelas do banco de dados criadas (se não existiam).")


# Inclui os roteadores com um prefixo /api/v1
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(vision.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API de Análise de Imagem! Acesse /docs para ver a documentação."}