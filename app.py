from fastapi import FastAPI, UploadFile, File
from google.cloud import vision
import io

app = FastAPI()
client = vision.ImageAnnotatorClient()

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    image = vision.Image(content=contents)
    response = client.label_detection(image=image)
    labels = response.label_annotations

    results = []
    for label in labels:
        results.append({"description": label.description, "score": label.score})

    return {"labels": results}
