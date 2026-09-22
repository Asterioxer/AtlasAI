from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .auth import AuthContext, require_auth, require_workspace_access
from .db import get_db
from .models import Chunk, Document, Source
from .services.embeddings import DeterministicEmbeddingProvider
from .services.ingestion import build_document

router = APIRouter(prefix="/api/v1")
embedding_provider = DeterministicEmbeddingProvider()


@router.post("/sources/{source_id}/upload", status_code=201)
async def upload_document(
    source_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_auth),
):
    source = db.get(Source, source_id)
    if source is None:
        raise HTTPException(404, "Source not found")
    require_workspace_access(source.workspace_id, auth, db, {"owner", "member"})
    parsed = build_document(file.filename or "document.txt", await file.read())
    document = Document(source_id=source_id, title=parsed.title, content=parsed.content)
    db.add(document)
    db.flush()
    vectors = await embedding_provider.embed([item.content for item in parsed.chunks])
    for item, embedding in zip(parsed.chunks, vectors, strict=True):
        db.add(Chunk(document_id=document.id, content=item.content, chunk_index=item.index, embedding=embedding))
    db.commit()
    db.refresh(document)
    return {"id": str(document.id), "title": document.title, "chunks_created": len(parsed.chunks)}
