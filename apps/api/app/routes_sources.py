from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from .auth import AuthContext, require_auth
from .db import get_db
from .models import Document, Source
from .services.ingestion import build_document

router = APIRouter(prefix="/api/v1")


@router.post("/sources/{source_id}/upload", status_code=201)
async def upload_document(
    source_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_auth),
):
    source = db.get(Source, source_id)
    if source is None:
        raise HTTPException(404, "Source not found")
    parsed = build_document(file.filename or "document.txt", await file.read())
    document = Document(source_id=source_id, title=parsed.title, content=parsed.content)
    db.add(document)
    db.flush()
    db.commit()
    db.refresh(document)
    return {"id": str(document.id), "title": document.title, "chunks_created": len(parsed.chunks)}
