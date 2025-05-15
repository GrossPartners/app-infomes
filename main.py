from fastapi import FastAPI, UploadFile, HTTPException
import logging, io, re
from typing import Dict

app = FastAPI(title="Financial Extractor API")

@app.get("/")
def root():
    return {"status": "ok"}

# Placeholder upload route – extend with your own extraction logic
@app.post("/upload")
async def upload(file: UploadFile):
    # Basic content‑type guard
    if not file.filename.lower().endswith((".pdf", ".jpg", ".png")):
        raise HTTPException(status_code=400, detail="Solo se aceptan PDFs o imágenes")
    content = await file.read()
    size_kb = len(content) / 1024
    logging.info(f"Received {file.filename} ({size_kb:.1f} KB)")
    # TODO: parse the file and return your metrics
    return {"filename": file.filename, "size_kb": f"{size_kb:.1f}", "message": "Parámetros financieros aún no implementados"}
