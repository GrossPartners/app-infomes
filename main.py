from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")

from fastapi import FastAPI, UploadFile, HTTPException
from pathlib import Path
import tempfile, shutil
from decimal import Decimal
from pydantic import BaseModel, Field

from helpers.pdf_utils import pdf_to_text
from helpers.parsing import extract_values

app = FastAPI(title="App Informes")

class Ratios(BaseModel):
    activo_corriente:  Decimal = Field(..., gt=0)
    pasivo_corriente:  Decimal = Field(..., gt=0)
    patrimonio_neto:   Decimal = Field(..., gt=0)

    @property
    def fondo_maniobra(self):   # AC – PC
        return self.activo_corriente - self.pasivo_corriente

    @property
    def ratio_liquidez(self):   # AC / PC
        return self.activo_corriente / self.pasivo_corriente

@app.post("/upload")
async def upload(file: UploadFile):
    # 1) guardar temporalmente
    tmpdir = tempfile.mkdtemp()
    pdf_path = Path(tmpdir) / file.filename
    with pdf_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # 2) texto plano
    text = pdf_to_text(pdf_path)

    # 3) extraer importes
    values = extract_values(text)
    if not values:
        raise HTTPException(422, "No se encontraron importes reconocibles")

    # 4) calcular ratios
    r = Ratios(**values)

    return {
        "filename": file.filename,
        "kb": round(pdf_path.stat().st_size / 1024, 1),
        "data": values,
        "fondo_maniobra": str(r.fondo_maniobra),
        "ratio_liquidez": str(round(r.ratio_liquidez, 2)),
    }

