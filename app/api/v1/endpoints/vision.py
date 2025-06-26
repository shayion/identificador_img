# app/api/v1/endpoints/vision.py
import os
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from google.cloud import vision
from typing import List
import shutil # Para salvar o arquivo
from pathlib import Path # Para manipular caminhos de arquivo
from sqlmodel import Session, select # Para interagir com o banco de dados

# Importações dos modelos e dependências
from app.models.user import UserInDB, Image, ImageLabel # Importe Image e ImageLabel
from app.database import get_session
from app.core.security import get_current_user

router = APIRouter()

# Configuração da chave de serviço do Google Cloud Vision
# Certifique-se de que 'credentials/service_account_key.json' está no diretório raiz do seu projeto
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/service_account_key.json"
client = vision.ImageAnnotatorClient()

# Diretório para salvar os uploads
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True) # Cria a pasta 'uploads' se ela não existir

@router.post("/analyze", summary="Analyze Image")
async def analyze_image(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(get_session) # Injeta a sessão do banco de dados
):
    """
    Recebe uma imagem, a analisa usando a API Google Cloud Vision,
    salva a imagem e seus metadados no banco de dados.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo enviado não é uma imagem."
        )

    # 1. Salvar o arquivo de imagem no disco
    # Cria um caminho único para o arquivo usando o nome original
    file_location = UPLOAD_DIR / file.filename
    # Garante que o nome do arquivo seja único para evitar sobrescrever
    counter = 1
    original_filename = file.filename
    while file_location.exists():
        name, ext = os.path.splitext(original_filename)
        file.filename = f"{name}_{counter}{ext}"
        file_location = UPLOAD_DIR / file.filename
        counter += 1

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar a imagem: {e}"
        )

    # 2. Preparar a imagem para a API do Google Vision
    with open(file_location, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    # 3. Chamar a API do Google Cloud Vision para detecção de labels
    try:
        response = client.label_detection(image=image)
        labels = response.label_annotations
    except Exception as e:
        # Se a análise falhar, ainda podemos ter salvo a imagem.
        # Decida se quer apagar a imagem ou manter. Por enquanto, vamos manter.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na análise da imagem pelo Google Vision: {e}"
        )

    # 4. Salvar os metadados da imagem no banco de dados
    new_image = Image(
        filename=original_filename, # Salva o nome original
        filepath=str(file_location), # Salva o caminho completo como string
        owner_id=current_user.id # Associa a imagem ao usuário logado
    )
    session.add(new_image)
    session.commit() # Commita a imagem para obter o ID
    session.refresh(new_image) # Atualiza o objeto para ter o ID gerado

    # 5. Salvar as labels da imagem no banco de dados
    saved_labels = []
    for label in labels:
        new_label = ImageLabel(
            description=label.description,
            score=label.score,
            image_id=new_image.id # Associa a label à imagem recém-salva
        )
        session.add(new_label)
        saved_labels.append({"description": label.description, "score": label.score}) # Para a resposta da API

    session.commit() # Commita as labels

    return {
        "message": "Imagem processada e dados salvos com sucesso!",
        "image_id": new_image.id,
        "filename": new_image.filename,
        "filepath": new_image.filepath,
        "uploaded_by": current_user.username,
        "detected_labels": saved_labels
    }