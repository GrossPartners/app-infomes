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

# Arranca uvicorn con expansión de $PORT (o usa 8000 si no está definida)
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"


