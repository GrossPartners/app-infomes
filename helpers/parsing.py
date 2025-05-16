# helpers/parsing.py
import re
from decimal import Decimal

_PATTERNS = {
    "activo_corriente":     r"Activo\s+Corriente\s+([\d\.,]+)",
    "pasivo_corriente":     r"Pasivo\s+Corriente\s+([\d\.,]+)",
    "pasivo_no_corriente":  r"Pasivo\s+No\s+Corriente\s+([\d\.,]+)",
    "efectivo_liquido":     r"Efectivo\s+y\s+otros\s+líquidos\s+([\d\.,]+)",
    "patrimonio_neto":      r"Patrimonio\s+Neto\s+([\d\.,]+)",
    "fondos_propios":       r"Fondos\s+Propios\s+([\d\.,]+)",
    "resultado_antes_imp":  r"Resultado\s+antes\s+de\s+impuestos\s+([\d\.,]+)",
    "existencias":          r"Existencias\s+([\d\.,]+)",
    # Esto puede variar según cómo aparezca en tu informe. Ajusta la parte "grupo" si es otra etiqueta:
    "inversiones_cp":       r"Inversiones\s+empresas\s+grupo.*?C/P\s*=\s*([\d\.,]+)|Inversiones\s+grupo\s+C/P\s+([\d\.,]+)",
    "riesgo":               r"Riesgo\s+([\d\.,]+)",
}

def _to_decimal(num: str) -> Decimal:
    # quita puntos de miles y cambia coma decimal
    return Decimal(num.replace(".", "").replace(",", "."))

def extract_values(text: str) -> dict:
    out = {}
    for key, pat in _PATTERNS.items():
        m = re.search(pat, text, flags=re.I)
        if not m:
            # si falta alguno, devolvemos dict vacío para forzar el error
            return {}
        # group(1) o group(2) según el alternation
        val = m.group(1) or m.group(2)
        out[key] = _to_decimal(val)
    return out


