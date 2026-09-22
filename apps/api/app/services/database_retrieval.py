from sqlalchemy import text
from sqlalchemy.orm import Session

from .retrieval import RetrievalHit


def lexical_search(db: Session, workspace_id: str, query: str, limit: int = 8) -> list[RetrievalHit]:
    rows = db.execute(
        text("""
            SELECT c.id AS chunk_id, s.id AS source_id, d.id AS document_id,
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
        RetrievalHit(str(row.chunk_id), float(row.score), str(row.source_id), str(row.document_id))
        for row in rows
    ]
