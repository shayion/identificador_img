# Arquivo: identificador_img/main.py

from fastapi import Depends, FastAPI, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from google.cloud import vision
# ATENÇÃO AQUI: Importação de auth
from auth.auth import authenticate_user, create_access_token, get_current_user # <-- Corrigido!
from pydantic import BaseModel
import os, io

# Configura a chave do serviço
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/service_account_key.json"

app = FastAPI()
client = vision.ImageAnnotatorClient()

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    token = create_access_token(data={"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

# Exemplo de rota protegida
@app.post("/analyze", dependencies=[Depends(get_current_user)]) # <-- Rota protegida com Depends(get_current_user)
async def analyze_image(file: UploadFile = File(...)):
    content = await file.read()
    image = vision.Image(content=content)
    response = client.label_detection(image=image)
    labels = [l.description for l in response.label_annotations]
    return {"labels": labels}

# Exemplo de rota de teste protegida (apenas para verificar se a autenticação funciona)
@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user