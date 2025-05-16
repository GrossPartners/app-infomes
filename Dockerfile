FROM python:3.12-slim

# Utilidades para procesar PDFs e imágenes (poppler y Tesseract para OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils tesseract-ocr tesseract-ocr-spa && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

# Arrancamos uvicorn en el puerto $PORT (o 8000 si no está definido)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
