from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .auth import AuthContext, require_auth, require_workspace_access
from .config import settings
from .db import get_db
from .models import Chunk, Document, Source
from .services.embeddings import EmbeddingProviderError, build_embedding_provider
from .services.ingestion import build_document
from .services.parsing import UnsupportedDocumentType

router = APIRouter(prefix="/api/v1")
embedding_provider = build_embedding_provider(
    settings.embedding_provider,
    token=settings.hf_token,
    model=settings.embedding_model,
    dimensions=settings.embedding_dimensions,
    endpoint=settings.embedding_endpoint,
    timeout=settings.embedding_timeout_seconds,
    batch_size=settings.embedding_batch_size,
)


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

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(413, f"File exceeds the {settings.max_upload_bytes // (1024 * 1024)} MB upload limit")

    filename = file.filename or "document.txt"
    try:
        parsed = build_document(filename, content)
    except UnsupportedDocumentType as exc:
        raise HTTPException(415, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(422, f"Could not parse {filename}: {exc}") from exc

    if not parsed.content.strip():
        raise HTTPException(422, f"No readable text was extracted from {filename}")

    document = Document(source_id=source_id, title=parsed.title, content=parsed.content)
    db.add(document)
    db.flush()

    try:
        vectors = await embedding_provider.embed([item.content for item in parsed.chunks])
        for item, embedding in zip(parsed.chunks, vectors, strict=True):
            db.add(
                Chunk(
                    document_id=document.id,
                    content=item.content,
                    chunk_index=item.index,
                    embedding=None,
                    semantic_embedding=embedding if embedding_provider.is_semantic else None,
                )
            )
        db.commit()
    except EmbeddingProviderError as exc:
        db.rollback()
        raise HTTPException(502, str(exc)) from exc
    except Exception:
        db.rollback()
        raise

    db.refresh(document)
    return {
        "id": str(document.id),
        "title": document.title,
        "chunks_created": len(parsed.chunks),
        "embedding_provider": settings.embedding_provider,
        "embedding_model": settings.embedding_model if embedding_provider.is_semantic else "deterministic",
        "source_type": Path(filename).suffix.lower().lstrip(".") or "file",
    }


@router.post("/workspaces/{workspace_id}/reindex", status_code=200)
async def reindex_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_auth),
):
    if not embedding_provider.is_semantic:
        raise HTTPException(
            503,
            "Semantic embeddings are not enabled. Set EMBEDDING_PROVIDER=huggingface and HF_TOKEN first.",
        )
    require_workspace_access(workspace_id, auth, db, {"owner"})

    rows = (
        db.query(Chunk)
        .join(Document, Chunk.document_id == Document.id)
        .join(Source, Document.source_id == Source.id)
        .filter(Source.workspace_id == workspace_id, Chunk.semantic_embedding.is_(None))
        .order_by(Document.created_at, Chunk.chunk_index)
        .limit(5000)
        .all()
    )
    if not rows:
        return {"workspace_id": str(workspace_id), "reindexed": 0, "remaining": 0}

    try:
        vectors = await embedding_provider.embed([row.content for row in rows])
        for row, embedding in zip(rows, vectors, strict=True):
            row.semantic_embedding = embedding
        db.commit()
    except EmbeddingProviderError as exc:
        db.rollback()
        raise HTTPException(502, str(exc)) from exc

    remaining = (
        db.query(Chunk)
        .join(Document, Chunk.document_id == Document.id)
        .join(Source, Document.source_id == Source.id)
        .filter(Source.workspace_id == workspace_id, Chunk.semantic_embedding.is_(None))
        .count()
    )
    return {"workspace_id": str(workspace_id), "reindexed": len(rows), "remaining": remaining}
