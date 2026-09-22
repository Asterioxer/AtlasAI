from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


class UnsupportedDocumentType(ValueError):
    pass


def parse_document(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".md", ".markdown", ".txt"}:
        return content.decode("utf-8")
    if suffix == ".pdf":
        reader = PdfReader(BytesIO(content))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages).strip()
    raise UnsupportedDocumentType(f"Unsupported document type: {suffix or 'unknown'}")
