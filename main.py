# main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import RedirectResponse
from typing import List
from pathlib import Path
import tempfile, shutil
from decimal import Decimal
from pydantic import BaseModel, Field

from helpers.pdf_utils import pdf_to_text
from helpers.parsing import extract_values   # solo esto, no hace falta _to_decimal aquí

from pdf2image import convert_from_path
import pytesseract

app = FastAPI(title="App Informes")

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


class InformeData(BaseModel):
    activo_corriente:    Decimal = Field(..., alias="activo_corriente")
    pasivo_corriente:    Decimal = Field(..., alias="pasivo_corriente")
    pasivo_no_corriente: Decimal = Field(..., alias="pasivo_no_corriente")
    efectivo_liquido:    Decimal = Field(..., alias="efectivo_liquido")
    patrimonio_neto:     Decimal = Field(..., alias="patrimonio_neto")
    fondos_propios:      Decimal = Field(..., alias="fondos_propios")
    resultado_antes_imp: Decimal = Field(..., alias="resultado_antes_imp")
    existencias:         Decimal = Field(..., alias="existencias")
    inversiones_cp:      Decimal = Field(..., alias="inversiones_cp")
    riesgo:              Decimal = Field(..., alias="riesgo")


class Criterios(BaseModel):
    ratio_liquidez:          Decimal
    ratio_ef_deuda_neta:     Decimal
    ratio_pat_riesgo:        Decimal
    pct_pat_activo:          Decimal
    inv_grupo_mayor_50_ac:   bool
    existencias_mayor_50_ac: bool


@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    resultados = []

    for file in files:
        # 1) Guardar temporalmente
        tmpdir = tempfile.mkdtemp()
        pdf_path = Path(tmpdir) / file.filename
        with pdf_path.open("wb") as out:
            shutil.copyfileobj(file.file, out)

        # 2) Extraer texto nativo
        text = pdf_to_text(pdf_path) or ""
        # 3) Fallback OCR si hace falta
        if not text.strip():
            try:
                text = "".join(
                    pytesseract.image_to_string(img, lang="spa")
                    for img in convert_from_path(str(pdf_path))
                )
            except Exception as e:
                resultados.append({
                    "filename": file.filename,
                    "error": f"Error en OCR: {e}"
                })
                continue

        # 4) Extraer valores (todos o {})
        raw = extract_values(text)
        if not raw:
            resultados.append({
                "filename": file.filename,
                "error": "Faltan importes en el PDF"
            })
            continue

        # 5) Validar e instanciar InformeData
        try:
            info = InformeData(**raw)
        except Exception as e:
            resultados.append({
                "filename": file.filename,
                "error": f"Formatos inválidos: {e}"
            })
            continue

        # 6) Calcular criterios
        r_liq = info.activo_corriente / info.pasivo_corriente
        deuda_neta = info.pasivo_corriente + info.pasivo_no_corriente
        r_ef_deu = (info.efectivo_liquido - deuda_neta) / info.riesgo
        r_pat_riesgo = info.patrimonio_neto / info.riesgo

        # Total activo = corriente + no corriente (no extraído) → ui fallback 0
        # Si necesitas Activo No Corriente, añádelo al extractor.
        act_no_corr = raw.get("activo_no_corriente", Decimal(0))
        total_act = info.activo_corriente + act_no_corr

        pct_pat_act = info.patrimonio_neto / total_act if total_act else Decimal(0)

        inv_flag = info.inversiones_cp > (info.activo_corriente * Decimal("0.5"))
        exist_flag = info.existencias > (info.activo_corriente * Decimal("0.5"))

        criterios = Criterios(
            ratio_liquidez=r_liq.quantize(Decimal("0.01")),
            ratio_ef_deuda_neta=r_ef_deu.quantize(Decimal("0.01")),
            ratio_pat_riesgo=r_pat_riesgo.quantize(Decimal("0.01")),
            pct_pat_activo=pct_pat_act.quantize(Decimal("0.01")),
            inv_grupo_mayor_50_ac=inv_flag,
            existencias_mayor_50_ac=exist_flag,
        )

        # 7) Construir respuesta
        resultados.append({
            "filename": file.filename,
            "kb": round(pdf_path.stat().st_size / 1024, 1),
            "data": info.dict(by_alias=True),
            "criterios_principales": {
                "AC/PC": str(criterios.ratio_liquidez),
                "(E - DeudaNeta) / Riesgo": str(criterios.ratio_ef_deuda_neta),
                "PN / Riesgo": str(criterios.ratio_pat_riesgo),
            },
            "criterios_adicionales": {
                "PN / TotalActivo": str(criterios.pct_pat_activo),
                "InvGrupoCP > 50% AC": criterios.inv_grupo_mayor_50_ac,
                "Existencias > 50% AC": criterios.existencias_mayor_50_ac,
            }
        })

    # ← Este return debe quedar alineado con el for, no indent extra
    return resultados
