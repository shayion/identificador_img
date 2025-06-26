# app/main.py
from fastapi import FastAPI
from app.api.v1.endpoints import auth, users, vision

app = FastAPI(
    title="Minha API de Análise de Imagem",
    description="API para autenticação de usuários e análise de imagens com Google Cloud Vision.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Inclui os roteadores com um prefixo /api/v1
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(vision.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API de Análise de Imagem! Acesse /docs para ver a documentação."}