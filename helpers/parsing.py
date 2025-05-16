# helpers/parsing.py
import re
from decimal import Decimal

# Mapea cada campo a las posibles etiquetas que aparecen en el PDF
_FIELD_LABELS = {
    "activo_corriente":    [r"Activo\s+Corriente"],
    "pasivo_corriente":    [r"Pasivo\s+Corriente"],
    "pasivo_no_corriente": [r"Pasivo\s+No\s+Corriente"],
    "efectivo_liquido":    [r"Efectivo\s+y\s+otros\s+l[ií]quidos"],
    "patrimonio_neto":     [r"Patrimonio\s+Neto"],
    "fondos_propios":      [r"Fondos\s+Propios"],
    "resultado_antes_imp": [r"Resultado\s+antes\s+de\s+impuestos"],
    "existencias":         [r"Existencias"],
    "inversiones_cp":      [
        # puede aparecer como "Inversiones grupo C/P = 123.456,78"
        r"Inversiones.*?C\/P",
        # o "Inversiones en empresas del grupo y asociadas a C/P  17.850,00"
        r"Inversiones.*?grupo.*?C\/P"
    ],
    "riesgo":              [r"Riesgo"],
}

# Convierte "1.234.567,89" → Decimal("1234567.89")
def _to_decimal(num: str) -> Decimal:
    clean = num.strip().replace(".", "").replace(",", ".")
    return Decimal(clean)

def extract_values(text: str) -> dict:
    """
    Busca en `text` cada uno de los 10 campos. 
    Si falta alguno, devuelve {}.
    """
    out = {}
    for key, labels in _FIELD_LABELS.items():
        found = None
        for lab in labels:
            # /m para multiline, /i insensible a mayúsculas
            pat = re.compile(rf"{lab}\s*[:\-\–]?\s*([\d\.,]+)", re.IGNORECASE | re.M)
            m = pat.search(text)
            if m:
                found = m.group(1)
                break
        if not found:
            # No encontramos este campo → abortamos
            return {}
        try:
            out[key] = _to_decimal(found)
        except Exception:
            return {}
    return out
