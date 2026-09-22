CREATE TABLE IF NOT EXISTS workspace_members (
    id uuid PRIMARY KEY,
    workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    subject varchar(255) NOT NULL,
    role varchar(20) NOT NULL CHECK (role IN ('owner', 'member', 'viewer')),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(workspace_id, subject)
);

ALTER TABLE chunks ADD COLUMN IF NOT EXISTS embedding vector(8);

CREATE INDEX IF NOT EXISTS idx_workspace_members_subject ON workspace_members(subject);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
    ON chunks USING hnsw (embedding vector_cosine_ops)
    WHERE embedding IS NOT NULL;
