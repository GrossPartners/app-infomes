FROM python:3.12-slim

# Instala poppler-utils y Tesseract con español
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      poppler-utils \
      tesseract-ocr \
      tesseract-ocr-spa && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

EXPOSE 8080

# Arranca Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]



