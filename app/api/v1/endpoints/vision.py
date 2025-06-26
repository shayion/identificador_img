# app/api/v1/endpoints/vision.py
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from google.cloud import vision
import os, io
# Importa a dependência de get_current_user
from app.api.v1.deps import get_current_user

# Configura a chave do serviço (mantenha aqui por enquanto, mas idealmente centralize config)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/service_account_key.json"
client = vision.ImageAnnotatorClient()

router = APIRouter(
    prefix="/analyze", # Prefixo para todos os endpoints neste roteador (ex: /api/v1/analyze)
    tags=["Análise de Imagem"] # Tag para o Swagger UI
)

@router.post("/", dependencies=[Depends(get_current_user)]) # A rota agora é apenas /
async def analyze_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        image = vision.Image(content=content)
        response = client.label_detection(image=image)
        labels = [l.description for l in response.label_annotations]
        return {"labels": labels}
    except Exception as e:
        # Captura erros da Google API e retorna como 500
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao processar imagem com Google Vision API: {e}")