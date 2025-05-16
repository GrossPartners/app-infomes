# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse
from typing import List
from pathlib import Path
import tempfile, shutil
from decimal import Decimal
from pydantic import BaseModel, Field

from helpers.pdf_utils import pdf_to_text
from helpers.parsing import extract_values

# OCR deps
from pdf2image import convert_from_path
import pytesseract

app = FastAPI(title="App Informes")

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


class Ratios(BaseModel):
    activo_corriente:  Decimal = Field(..., gt=0)
    pasivo_corriente:  Decimal = Field(..., gt=0)
    patrimonio_neto:   Decimal = Field(..., gt=0)

    @property
    def fondo_maniobra(self) -> Decimal:
        return self.activo_corriente - self.pasivo_corriente

    @property
    def ratio_liquidez(self) -> Decimal:
        return self.activo_corriente / self.pasivo_corriente


@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    resultados = []

    for file in files:
        # 1) Guardar temporalmente
        tmpdir = tempfile.mkdtemp()
        pdf_path = Path(tmpdir) / file.filename
        with pdf_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        # 2) Intentar extraer texto nativo
        text = pdf_to_text(pdf_path)

        # 3) Si está vacío o no hay datos, fallback OCR
        if not text or text.strip() == "":
            try:
                images = convert_from_path(str(pdf_path))
                ocr_text = ""
                for img in images:
                    ocr_text += pytesseract.image_to_string(img, lang="spa")
                text = ocr_text
            except Exception as e:
                # Si falla OCR, lo registramos y seguimos
                resultados.append({
                    "filename": file.filename,
                    "error": f"Error en OCR: {e}"
                })
                continue

        # 4) Extraer importes
        values = extract_values(text)
        if not values:
            resultados.append({
                "filename": file.filename,
                "error": "No se encontraron importes reconocibles"
            })
            continue

        # 5) Calcular ratios
        try:
            r = Ratios(**values)
        except Exception as e:
            resultados.append({
                "filename": file.filename,
                "error": f"Error calculando ratios: {e}"
            })
            continue

        # 6) Construir respuesta
        resultados.append({
            "filename": file.filename,
            "kb": round(pdf_path.stat().st_size / 1024, 1),
            "data": values,
            "fondo_maniobra": str(r.fondo_maniobra),
            "ratio_liquidez": str(round(r.ratio_liquidez, 2)),
        })

    return resultados


    return resultados


