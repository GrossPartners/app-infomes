# Usa la imagen oficial de Python 3.12 slim como base
FROM python:3.12-slim

# 1) Instala poppler-utils (pdftotext) y Tesseract + paquete de español
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      poppler-utils \                # para convertir PDF a texto
      tesseract-ocr \                # motor OCR
      tesseract-ocr-spa \            # datos de idioma español
 && rm -rf /var/lib/apt/lists/*

# 2) Crea y sitúa el directorio de trabajo
WORKDIR /app

# 3) Copia y instala las deps de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copia el resto del código (incluye helpers/pdf_utils, parsing, main.py, etc.)
COPY . .

# 5) Expone el puerto que utiliza Uvicorn
EXPOSE 8080

# 6) Arranca la aplicación con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]


