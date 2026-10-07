# AtlasAI Retrieval Architecture

AtlasAI separates **lexical evidence**, **semantic evidence**, and **generation** instead of treating one similarity score as truth.

## Retrieval pipeline

`Query → lexical search + semantic vector search → RRF → relevance reranking → confidence gate → grounded generation`

### 1. Lexical retrieval

PostgreSQL full-text search remains the high-precision path for exact names, certifications, technologies, IDs, short keyword queries, and spelling-sensitive queries.

### 2. Semantic retrieval

When `EMBEDDING_PROVIDER=huggingface`, AtlasAI uses a hosted sentence-embedding model and stores vectors in `chunks.semantic_embedding`.

Reference model:

`BAAI/bge-small-en-v1.5` → 384 dimensions

The legacy `chunks.embedding` column remains intact during migration.

### 3. Fusion

Lexical and semantic rankings are merged with Reciprocal Rank Fusion. Semantic candidates may introduce results that do not share literal query terms.

When semantic embeddings are disabled, synthetic vectors are excluded from production ranking.

### 4. Reranking

The reranker combines semantic similarity, query-term coverage, exact-term matches, phrase matches, and confidence thresholding.

### 5. Re-indexing

Owners can re-index existing chunks with:

`POST /api/v1/workspaces/{workspace_id}/reindex`

The operation fills only missing semantic vectors and processes up to 5,000 chunks per call.

## Configuration

```env
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIMENSIONS=384
HF_TOKEN=<server-side secret>
```

The embedding provider is independent of `LLM_PROVIDER`, allowing retrieval and generation to use different models/providers.

## Design principle

A generator cannot recover evidence that retrieval failed to surface. Retrieval is therefore treated as an independently testable subsystem with explicit confidence gates.
