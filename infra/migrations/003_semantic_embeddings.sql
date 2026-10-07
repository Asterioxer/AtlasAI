-- AtlasAI semantic retrieval migration
-- Safe additive migration: legacy 8-D deterministic embeddings remain intact
-- while the production semantic index is populated progressively.

ALTER TABLE public.chunks
  ADD COLUMN IF NOT EXISTS semantic_embedding vector(384);

CREATE INDEX IF NOT EXISTS chunks_semantic_embedding_hnsw
  ON public.chunks USING hnsw (semantic_embedding vector_cosine_ops);
