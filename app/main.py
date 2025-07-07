# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.api.v1.endpoints import auth, users, vision
from app.database import create_db_and_tables

app = FastAPI(
    title="Minha API de Análise de Imagem",
    description="API para autenticação de usuários e análise de imagens com Google Cloud Vision.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# NECESSÁRIO: Monta a pasta 'static' para servir arquivos estáticos
# Eles estarão acessíveis em http://127.0.0.1:8000/static/
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
def on_startup():
    print("Criando tabelas do banco de dados...")
    create_db_and_tables()
    print("Tabelas do banco de dados criadas (se não existiam).")


# Inclui os roteadores com um prefixo /api/v1
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(vision.router, prefix="/api/v1")

# NECESSÁRIO: Rota principal que serve o index.html (sua tela de login)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("app/static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

# O endpoint /docs e /redoc ainda funcionarão normalmente.