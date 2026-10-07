# AtlasAI

Production-oriented enterprise knowledge and RAG platform for grounded, cited answers over heterogeneous knowledge sources.

> **Status:** Hosted core is live. AtlasAI now has a real configurable LLM path through Hugging Face Inference Providers and broad document extraction for common enterprise formats.

## What AtlasAI does

AtlasAI turns organizational knowledge into a searchable, permission-aware context layer for AI answers.

The core flow is:

\`Source → Parse → Chunk → Embed → Hybrid Retrieve → Rerank → Ground → Generate → Cite\`

The generation layer is no longer a placeholder: the API can route grounded prompts to a real hosted model while retaining a deterministic provider for tests and local development.

## Current status

### Completed

- **Platform**
  - FastAPI + Next.js application
  - PostgreSQL/pgvector persistence
  - Redis/cache and worker foundations
  - workspace RBAC and bearer authentication boundary
  - conversation and message persistence

- **Universal ingestion layer**
  - PDF
  - DOCX
  - XLSX and XLS
  - PPTX
  - ODT / ODS / ODP
  - EPUB
  - RTF and EML
  - CSV / TSV
  - JSON / YAML / TOML
  - HTML / XML
  - Markdown / TXT / logs
  - common source-code and configuration formats
  - 25 MB upload guardrail
  - parser-specific error handling

- **RAG**
  - PostgreSQL lexical retrieval
  - optional hosted semantic embeddings through Hugging Face Inference Providers
  - 384-D pgvector semantic index with HNSW
  - Reciprocal Rank Fusion when semantic retrieval is enabled
  - confidence-aware reranking
  - additive semantic re-indexing for existing chunks
  - retrieved chunk text is passed to the model, not merely document IDs
  - citation-preserving grounded responses

- **Real AI**
  - provider abstraction
  - Hugging Face Inference Providers adapter
  - configurable model and endpoint
  - grounded system prompt with anti-hallucination behavior
  - deterministic fallback for local tests
  - default low-cost model configuration: \`Qwen/Qwen3-4B-Instruct-2507:cheapest\`

## AI configuration

For hosted inference, configure Render with:

\`LLM_PROVIDER=huggingface\`
\`HF_TOKEN=<your Hugging Face token>\`

Optional:

\`LLM_MODEL=Qwen/Qwen3-4B-Instruct-2507:cheapest\`

The Hugging Face token must remain a server-side Render secret; never put it in the Next.js frontend or Git repository.

### Semantic retrieval configuration

AtlasAI keeps generation and retrieval as separate provider boundaries. To activate semantic retrieval on the hosted API:

`EMBEDDING_PROVIDER=huggingface`
`EMBEDDING_MODEL=BAAI/bge-small-en-v1.5`
`EMBEDDING_DIMENSIONS=384`
`HF_TOKEN=<your Hugging Face token>`

After enabling the provider, existing chunks can be upgraded without deleting the legacy vectors:

`POST /api/v1/workspaces/{workspace_id}/reindex`

The endpoint fills `semantic_embedding` in batches and reports how many chunks remain. The semantic column uses a pgvector HNSW cosine index, while the legacy deterministic vector remains available during the migration.

Hugging Face Inference Providers exposes an OpenAI-compatible chat endpoint and currently provides a small free monthly inference credit for free accounts; usage beyond the included credit is billable, so the project keeps the provider configurable rather than coupling AtlasAI to one vendor. See the Hugging Face provider documentation for current model availability and pricing.

## Architecture

\`\`\`text
                         ┌──────────────────┐
                         │     Next.js      │
                         │       Web        │
                         └────────┬─────────┘
                                  │ HTTPS
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │       API       │
                         └───────┬──────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
       ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
       │ PostgreSQL  │    │    Redis    │    │ Real LLM    │
       │  + pgvector │    │ cache/queue │    │ HF provider │
       └──────┬──────┘    └──────┬──────┘    └─────────────┘
              │                  │
              ▼                  ▼
       Hybrid Retrieval       Worker layer
       dense + lexical        ingestion/jobs
              │
              ▼
          Reranking
              │
              ▼
      Retrieved evidence
              │
              ▼
       Grounded generation
              │
              ▼
          Citations
\`\`\`

## Repository structure

\`\`\`text
atlas-ai/
├── apps/
│   ├── web/                  # Next.js frontend
│   └── api/                  # FastAPI API + worker
├── packages/                 # Shared contracts/UI/config
├── services/                 # Ingestion/retrieval/embedding/LLM boundaries
├── infra/                    # Docker/migrations/observability/deployment
├── tests/                    # Integration/retrieval/evaluation coverage
└── docs/                     # Architecture, ADRs and evaluation
\`\`\`

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, TypeScript, custom AtlasAI UI |
| API | FastAPI, Pydantic |
| Database | PostgreSQL + pgvector |
| Search | pgvector + PostgreSQL lexical search + RRF |
| Ingestion | pypdf, python-docx, openpyxl, python-pptx, xlrd, BeautifulSoup, PyYAML |
| AI | Provider-neutral LLM abstraction + Hugging Face Inference Providers |
| Cache / jobs | Redis |
| Observability | OpenTelemetry + request correlation |
| Testing | Pytest + production web build |
| Infrastructure | Docker, Render, Vercel, Supabase |

## Hosted deployment

\`\`\`text
Vercel Next.js
     │
     ▼
Render FastAPI
     │
     ├── Supabase PostgreSQL + pgvector
     ├── Redis-compatible cache/queue
     └── Hugging Face Inference Providers
\`\`\`

The hosted gate is:

\`Vercel Web → Render API → Supabase pgvector → hybrid retrieval → real model generation → cited response\`

## Security boundary

Hosted deployments should use:

- \`AUTH_MODE=jwt\`
- strong secret management
- TLS at the public ingress
- secrets supplied through the hosting platform rather than committed to Git
- release-time migrations
- separate worker processes where supported
- database RLS policies when Supabase's Data API is exposed

Local authentication is intentionally limited to development.

## Roadmap

### Next evolution

- [ ] multimodal ingestion for images and scanned PDFs using a VLM/OCR path
- [ ] document versioning and deduplication
- [ ] asynchronous ingestion jobs for large files
- [x] semantic retrieval foundation + confidence-aware reranking
  - [ ] cross-encoder semantic reranking
- [ ] answer faithfulness/evaluation dashboard
- [ ] retrieval benchmark suite with precision@k / recall@k / MRR
- [ ] GitHub / Notion / web connectors
- [ ] ACL-aware retrieval at chunk level
- [ ] model comparison and cost analytics

## License

MIT
