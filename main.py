# main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import RedirectResponse
from typing import List
from pathlib import Path
import tempfile, shutil
from decimal import Decimal
from pydantic import BaseModel, Field

from helpers.pdf_utils import pdf_to_text
from helpers.parsing import extract_values, _to_decimal   # <-- traer también _to_decimal
from pdf2image import convert_from_path
import pytesseract
import re

app = FastAPI(title="App Informes")

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


class InformeData(BaseModel):
    activo_corriente:    Decimal  = Field(..., alias="activo_corriente")
    pasivo_corriente:    Decimal  = Field(..., alias="pasivo_corriente")
    pasivo_no_corriente: Decimal  = Field(..., alias="pasivo_no_corriente")
    efectivo:            Decimal  = Field(..., alias="efectivo_liquido")
    patrimonio_neto:     Decimal  = Field(..., alias="patrimonio_neto")
    fondos_propios:      Decimal  = Field(..., alias="fondos_propios")
    resultado_antes_imp: Decimal  = Field(..., alias="resultado_antes_imp")
    existencias:         Decimal  = Field(..., alias="existencias")
    inv_grupo_cp:        Decimal  = Field(..., alias="inversiones_cp")
    riesgo:              Decimal  = Field(..., alias="riesgo")


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
        tmpdir = tempfile.mkdtemp()
        pdf_path = Path(tmpdir) / file.filename
        with pdf_path.open("wb") as out:
            shutil.copyfileobj(file.file, out)

        text = pdf_to_text(pdf_path) or ""
        if not text.strip():
            try:
                text = "".join(
                    pytesseract.image_to_string(img, lang="spa")
                    for img in convert_from_path(str(pdf_path))
                )
            except Exception as e:
                resultados.append({"filename": file.filename, "error": f"Error OCR: {e}"})
                continue

        raw = extract_values(text)
        if not raw:
            resultados.append({"filename": file.filename, "error": "Faltan importes en el PDF"})
            continue

        try:
            info = InformeData(**raw)
        except Exception as e:
            resultados.append({"filename": file.filename, "error": f"Formatos inválidos: {e}"})
            continue

        # ratios
        r_liq = info.activo_corriente / info.pasivo_corriente
        deuda_neta = info.pasivo_corriente + info.pasivo_no_corriente
        r_ef_deu = (info.efectivo - deuda_neta) / info.riesgo
        r_pat_riesgo = info.patrimonio_neto / info.riesgo

        # necesitamos Activo No Corriente para total activo
        m = re.search(r"Activo\s+No\s+Corriente\s+([\d\.,]+)", text, flags=re.I)
        act_no_corr = _to_decimal(m.group(1)) if m else Decimal(0)
        total_act = info.activo_corriente + act_no_corr

        pct_pat_act = info.patrimonio_neto / total_act

        inv_flag = info.inv_grupo_cp > (info.activo_corriente * Decimal("0.5"))
        exist_flag = info.existencias > (info.activo_corriente * Decimal("0.5"))

        criterios = Criterios(
            ratio_liquidez=r_liq.quantize(Decimal("0.01")),
            ratio_ef_deuda_neta=r_ef_deu.quantize(Decimal("0.01")),
            ratio_pat_riesgo=r_pat_riesgo.quantize(Decimal("0.01")),
            pct_pat_activo=pct_pat_act.quantize(Decimal("0.01")),
            inv_grupo_mayor_50_ac=inv_flag,
            existencias_mayor_50_ac=exist_flag,
        )

        resultados.append({
            "filename": file.filename,
            "kb": round(pdf_path.stat().st_size/1024, 1),
            "data": info.dict(by_alias=True),
            "criterios_principales": {
                "AC/PC": str(criterios.ratio_liquidez),
                "(E-DeudaNeta)/Riesgo": str(criterios.ratio_ef_deuda_neta),
                "PN/Riesgo": str(criterios.ratio_pat_riesgo),
            },
            "criterios_adicionales": {
                "PN/TotalActivo": str(criterios.pct_pat_activo),
                "InvGrupoCP>50%AC": criterios.inv_grupo_mayor_50_ac,
                "Exist>50%AC": criterios.existencias_mayor_50_ac,
            }
        })

    return resultados

    return resultados

