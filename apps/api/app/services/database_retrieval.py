from sqlalchemy import text
from sqlalchemy.orm import Session

from .embeddings import EmbeddingProvider
from .retrieval import RetrievalHit


def lexical_search(db: Session, workspace_id: str, query: str, limit: int = 8) -> list[RetrievalHit]:
    rows = db.execute(
        text("""
            SELECT c.id AS chunk_id, c.content AS content, s.id AS source_id, d.id AS document_id,
                   ts_rank_cd(to_tsvector('english', c.content), plainto_tsquery('english', :query)) AS score
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            JOIN sources s ON s.id = d.source_id
            WHERE s.workspace_id = CAST(:workspace_id AS uuid)
              AND to_tsvector('english', c.content) @@ plainto_tsquery('english', :query)
            ORDER BY score DESC
            LIMIT :limit
        """),
        {"workspace_id": workspace_id, "query": query, "limit": limit},
    )
    return [
        RetrievalHit(str(r.chunk_id), float(r.score), str(r.source_id), str(r.document_id), str(r.content))
        for r in rows
    ]


async def vector_search(
    db: Session, workspace_id: str, query: str, provider: EmbeddingProvider, limit: int = 8
) -> list[RetrievalHit]:
    embedding = (await provider.embed([query]))[0]
    vector = "[" + ",".join(str(float(v)) for v in embedding) + "]"
    rows = db.execute(
        text("""
            SELECT c.id AS chunk_id, c.content AS content, s.id AS source_id, d.id AS document_id,
                   1 - (c.embedding <=> CAST(:embedding AS vector)) AS score
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            JOIN sources s ON s.id = d.source_id
            WHERE s.workspace_id = CAST(:workspace_id AS uuid)
              AND c.embedding IS NOT NULL
            ORDER BY c.embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """),
        {"workspace_id": workspace_id, "embedding": vector, "limit": limit},
    )
    return [
        RetrievalHit(str(r.chunk_id), float(r.score), str(r.source_id), str(r.document_id), str(r.content))
        for r in rows
    ]
