from pathlib import Path
import subprocess, tempfile

def pdf_to_text(pdf_path: Path) -> str:
    """Convierte PDF a texto plano con pdftotext -layout (ya viene en la imagen)."""
    with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
        subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), tmp.name],
            check=True,
        )
        return Path(tmp.name).read_text(encoding="utf-8", errors="ignore")
