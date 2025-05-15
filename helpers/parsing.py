import re
from decimal import Decimal

_PATTERNS = {
    "activo_corriente":  r"Activo\s+Corriente\s+([\d\.,]+)",
    "pasivo_corriente":  r"Pasivo\s+Corriente\s+([\d\.,]+)",
    "patrimonio_neto":   r"Patrimonio\s+Neto\s+([\d\.,]+)",
}

def _to_decimal(num: str) -> Decimal:
    return Decimal(num.replace('.', '').replace(',', '.'))

def extract_values(text: str) -> dict:
    out = {}
    for k, p in _PATTERNS.items():
        if m := re.search(p, text, flags=re.I):
            out[k] = _to_decimal(m.group(1))
    return out
