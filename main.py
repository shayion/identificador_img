import os
from fastapi import FastAPI, File, UploadFile
from google.cloud import vision
import io

# Configura a chave do serviço
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/service_account_key.json"

app = FastAPI()
client = vision.ImageAnnotatorClient()

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    content = await file.read()
    image = vision.Image(content=content)
    response = client.label_detection(image=image)
    labels = [l.description for l in response.label_annotations]
    return {"labels": labels}
