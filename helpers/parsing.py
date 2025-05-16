# helpers/parsing.py
import re
from decimal import Decimal

_PATTERNS = {
    "activo_corriente":    r"Activo\s+Corriente\s+([\d\.,]+)",
    "pasivo_corriente":    r"Pasivo\s+Corriente\s+([\d\.,]+)",
    "pasivo_no_corriente": r"Pasivo\s+No\s+Corriente\s+([\d\.,]+)",
    "efectivo_liquido":    r"Efectivo\s+y\s+otros\s+l[ií]quidos\s+([\d\.,]+)",
    "patrimonio_neto":     r"Patrimonio\s+Neto\s+([\d\.,]+)",
    "fondos_propios":      r"Fondos\s+Propios\s+([\d\.,]+)",
    "resultado_antes_imp": r"Resultado\s+antes\s+de\s+impuestos\s+([\d\.,\-\+]+)",
    "existencias":         r"Existencias\s+([\d\.,]+)",
    "inversiones_cp":      r"Inversi[oó]n(?:es)?\s+grupo\s+\(c/p\)\s+([\d\.,]+)",
    "riesgo":              r"Riesgo\s+([\d\.,]+)",
}

def _to_decimal(s: str) -> Decimal:
    return Decimal(s.replace('.', '').replace(',', '.'))

def extract_values(text: str) -> dict:
    out = {}
    for key, pat in _PATTERNS.items():
        m = re.search(pat, text, flags=re.I)
        if not m:
            return {}  # fallamos si falta alguno
        out[key] = _to_decimal(m.group(1))
    return out

