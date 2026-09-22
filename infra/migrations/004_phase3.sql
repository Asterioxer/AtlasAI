CREATE INDEX IF NOT EXISTS idx_chunks_content_fts_english
    ON chunks USING GIN (to_tsvector('english', content));
