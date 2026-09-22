from pathlib import Path


class UnsupportedDocumentType(ValueError):
    pass


def parse_document(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".md", ".markdown", ".txt"}:
        return content.decode("utf-8")
    if suffix == ".pdf":
        raise UnsupportedDocumentType(
            "PDF extraction adapter is not enabled yet; install the PDF parser in the ingestion worker."
        )
    raise UnsupportedDocumentType(f"Unsupported document type: {suffix or 'unknown'}")
