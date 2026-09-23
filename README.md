# AtlasAI

Production-oriented enterprise knowledge and RAG platform for grounded, cited answers over heterogeneous knowledge sources.

> **Status:** Core platform, AI product layer, observability, production hardening, and hosted deployment adapters are implemented. The next gate is live infrastructure provisioning and end-to-end smoke testing.

## What AtlasAI does

AtlasAI turns organizational knowledge into a searchable, permission-aware context layer for AI answers.

The core flow is:

`Source → Parse → Chunk → Embed → Hybrid Retrieve → Rerank → Ground → Generate → Cite`

The platform is designed around measurable retrieval quality, provider-neutral model integrations, explicit access control, observable requests, durable background jobs, and reproducible local development.

## Current status

### Completed

- **Phase 1 — Foundation & Platform Core**
  - Monorepo structure for web, API, shared contracts, services, infrastructure, tests and docs
  - FastAPI and Next.js application shells
  - PostgreSQL/pgvector and Redis local infrastructure
  - CI foundation and architecture documentation

- **Phase 2 — Intelligence Core**
  - SQLAlchemy data model and migrations
  - Workspace/source/document/chunk APIs
  - PDF, Markdown and text ingestion
  - Chunking and metadata handling
  - Embedding provider abstraction with deterministic local embeddings
  - pgvector and lexical search foundations
  - Reciprocal Rank Fusion (RRF)

- **Phase 3 — AI Product Layer**
  - Conversation and message persistence
  - Workspace RBAC with owner/member/viewer roles
  - Bearer authentication boundary
  - Hybrid retrieval and deterministic reranking
  - Grounded answer generation
  - Citations
  - Streaming chat via SSE
  - Functional web chat workspace
  - API integration coverage and production web build validation

- **Phase 4 — Production / AI Engineering Foundations**
  - Provider-neutral HTTP JSON LLM gateway
  - Redis caching primitive
  - OpenTelemetry tracing
  - Request IDs and correlation
  - Security headers
  - Runtime metrics endpoint
  - Retrieval evaluation metrics: Recall@K and MRR
  - Evaluation, cache, LLM and observability tests

- **Production Hardening**
  - Configurable local/JWT authentication modes
  - JWT issuer/audience validation support
  - Redis-backed durable job queue
  - Worker runtime and dead-letter queue contract
  - Production API and web Dockerfiles
  - Multi-service Docker Compose stack
  - CI validation for PostgreSQL/pgvector, Redis, migrations, API tests and production container builds
  - Deployment and release guidance

- **Hosted Deployment Adapters**
  - Managed `DATABASE_URL` support while preserving local Postgres settings
  - Configurable production CORS origins
  - Readiness endpoint
  - Hosting-platform `PORT` support in the API container
  - Free-tier split deployment runbook for Vercel, Render, Supabase and Upstash

## Architecture

```text
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
       │ PostgreSQL  │    │    Redis    │    │ LLM Gateway │
       │  + pgvector │    │ cache/queue │    │  providers  │
       └──────┬──────┘    └──────┬──────┘    └─────────────┘
              │                  │
              │                  ▼
              │           ┌─────────────┐
              │           │   Worker    │
              │           │  ingestion  │
              │           └─────────────┘
              │
              ▼
       Hybrid Retrieval
       dense + lexical
              │
              ▼
          Reranking
              │
              ▼
       Context + Citations
```

## Repository structure

```text
atlas-ai/
├── apps/
│   ├── web/                  # Next.js frontend
│   └── api/                  # FastAPI API + worker
├── packages/
│   ├── contracts/            # Shared API/domain contracts
│   ├── ui/                   # Shared UI boundary
│   └── config/               # Shared configuration boundary
├── services/
│   ├── ingestion/            # Ingestion pipeline
│   ├── retrieval/            # Retrieval and ranking
│   ├── embeddings/           # Embedding providers
│   ├── llm-gateway/          # Provider abstraction
│   └── evaluation/           # Evaluation primitives
├── infra/
│   ├── docker/               # Container support
│   ├── migrations/           # Ordered SQL migrations
│   ├── observability/        # Observability configuration/docs
│   └── deployment/           # Deployment/release documentation
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── retrieval/
│   └── evaluation/
├── docs/
│   ├── architecture/
│   ├── decisions/
│   └── evaluation/
├── .github/workflows/        # CI
├── docker-compose.yml
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, TypeScript, Tailwind CSS, shadcn/ui |
| API | FastAPI, Pydantic |
| Database | PostgreSQL + pgvector |
| Search | pgvector + PostgreSQL lexical search + RRF |
| Cache / jobs | Redis |
| Background processing | Redis-backed worker |
| AI integration | Provider-neutral LLM gateway |
| Observability | OpenTelemetry + request correlation |
| Testing | Pytest, API integration tests, web production builds |
| Infrastructure | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Authentication | Local development bearer mode + JWT production mode |

## Local development

### Prerequisites

- Docker and Docker Compose
- Python 3.12+
- Node.js 22+
- npm

### Start the infrastructure

```bash
docker compose up --build
```

The local stack contains:

- PostgreSQL with pgvector
- Redis
- FastAPI API
- Redis worker
- Next.js web application

The local authentication mode is intentionally developer-friendly. **Do not use `AUTH_MODE=local` as a production security boundary.**

## Quality gates

The repository's CI pipeline currently validates:

1. PostgreSQL/pgvector service startup
2. Redis service startup
3. Ordered database migrations
4. API test suite
5. API production container build
6. Web production container build
7. Next.js production build

The project follows a root-cause-first workflow: features are not considered complete when only the UI works; the API, persistence, retrieval/generation path and tests must remain coherent.

## Hosted deployment

The portfolio deployment target separates the application from managed infrastructure:

```text
                    ┌─────────────────┐
                    │     Vercel      │
                    │   Next.js Web   │
                    └────────┬────────┘
                             │ HTTPS
                             ▼
                    ┌─────────────────┐
                    │     Render      │
                    │   FastAPI API   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
       │  Supabase   │ │   Upstash   │ │ LLM provider│
       │ PostgreSQL  │ │    Redis    │ │ / local mode│
       │ + pgvector  │ │ cache/queue │ │             │
       └─────────────┘ └─────────────┘ └─────────────┘
```

This is a **free-tier portfolio/demo target**, not an SLA-backed production environment. The exact hosting providers can impose cold starts, inactivity pauses, quotas and resource limits.

See `infra/deployment/README.md` for the release sequence and environment contract.

### Deployment gate

The hosted environment is not considered complete until this path is smoke-tested:

`Vercel Web → Render API → Supabase pgvector → hybrid retrieval → generation → cited response`

## Security boundary

Hosted deployments should use:

- `AUTH_MODE=jwt`
- strong secret management
- JWT issuer/audience validation where applicable
- managed PostgreSQL/pgvector and Redis
- TLS at the public ingress
- secrets supplied through the hosting platform rather than committed to Git
- release-time database migrations
- exported OpenTelemetry telemetry
- separate API and worker processes where the selected host supports them

Local authentication is intentionally limited to development.

## Evaluation

AtlasAI treats retrieval quality as an engineering concern rather than relying only on qualitative demos.

Current evaluation primitives include:

- Recall@K
- MRR
- citation/source hit rate foundations
- retrieval failure visibility
- request latency/observability foundations

Planned evaluation expansion includes answer relevance, faithfulness, p50/p95 latency, token usage, estimated cost and model/retriever comparisons.

## Roadmap

### Completed
- [x] Foundation
- [x] Ingestion
- [x] Retrieval
- [x] Generation
- [x] Conversations and citations
- [x] RBAC/authentication boundary
- [x] Caching foundation
- [x] Observability foundation
- [x] Retrieval evaluation foundation
- [x] Production containerization
- [x] Managed database/Redis configuration adapters
- [x] Deployment runbook
- [ ] Live free-tier infrastructure deployment
- [ ] Deployment smoke tests

### Next
- [ ] Live Vercel/Render/Supabase/Upstash deployment
- [ ] End-to-end hosted smoke test
- [ ] Real provider integrations behind the gateway
- [ ] Expanded evaluation dataset and dashboard
- [ ] GitHub/web/Notion ingestion
- [ ] Advanced ACLs and document versioning
- [ ] Semantic caching and cost analytics
- [ ] Reranker benchmarking
- [ ] Multi-model comparison

## Documentation

- Architecture: `docs/architecture/`
- ADRs: `docs/decisions/`
- Evaluation: `docs/evaluation/`
- Deployment: `infra/deployment/README.md`
- Changelog: `CHANGELOG.md`

## License

MIT
