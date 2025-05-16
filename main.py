from typing    import List
from fastapi   import FastAPI, UploadFile, File
from fastapi.responses import RedirectResponse
from pathlib   import Path
import tempfile, shutil
from decimal   import Decimal
from pydantic  import BaseModel, Field

from helpers.pdf_utils  import pdf_to_text
from helpers.parsing    import extract_values

app = FastAPI(title="App Informes")

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


class Ratios(BaseModel):
    activo_corriente: Decimal = Field(..., gt=0)
    pasivo_corriente: Decimal = Field(..., gt=0)
    patrimonio_neto:  Decimal = Field(..., gt=0)

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
        # 1) guardo el PDF
        tmpdir   = tempfile.mkdtemp()
        pdf_path = Path(tmpdir) / file.filename
        with pdf_path.open("wb") as out:
            shutil.copyfileobj(file.file, out)

        # 2) extraigo texto
        text = pdf_to_text(pdf_path)

        # 3) extraigo valores
        try:
            values = extract_values(text)
            if not values:
                raise ValueError("sin valores")
            r = Ratios(**values)

            resultados.append({
                "filename":       file.filename,
                "kb":             round(pdf_path.stat().st_size / 1024, 1),
                "data":           values,
                "fondo_maniobra": str(r.fondo_maniobra),
                "ratio_liquidez": str(round(r.ratio_liquidez, 2)),
            })

        except Exception:
            # si algo falla, lo anoto pero no paro el bucle
            resultados.append({
                "filename": file.filename,
                "error":    "No se encontraron importes reconocibles"
            })

    return resultados


    return resultados


