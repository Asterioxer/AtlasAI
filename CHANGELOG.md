# Changelog

All notable AtlasAI development milestones are documented here.

## [Unreleased]

### Planned
- Free-tier deployment using Vercel, Render, Supabase and Upstash.
- Production deployment configuration for managed PostgreSQL/pgvector and Redis.
- Deployment smoke tests and environment validation.
- Expanded evaluation dataset and quality dashboard.
- Additional ingestion connectors and advanced retrieval/model benchmarking.

## 2026-09-23 — Production Hardening

### Added
- Configurable authentication modes:
  - local bearer authentication for development
  - JWT validation for production
  - optional JWT issuer and audience validation
- Redis-backed durable job queue.
- Worker runtime with ingestion job contract.
- Dead-letter queue handling for unknown jobs.
- Production API Dockerfile.
- Production Next.js Dockerfile using standalone output.
- Multi-service Docker Compose topology for API, worker, web, PostgreSQL/pgvector and Redis.
- Production deployment and release documentation.
- CI validation for API and web container builds.

### Improved
- Production configuration now explicitly separates development authentication from the production security boundary.
- README now documents the production architecture and deployment expectations.
- Release workflow documents image build/scan, migrations, service startup and health verification.

### Validation
- API tests passed.
- PostgreSQL/pgvector migrations passed.
- API container build passed.
- Web container build passed.
- Web production build passed.

## 2026-09-23 — Phase 4: Production / AI Engineering Foundations

### Added
- Provider-neutral HTTP JSON LLM gateway.
- Redis cache primitive.
- OpenTelemetry tracing foundation.
- Request IDs and correlation.
- Security headers.
- Runtime metrics endpoint.
- Retrieval evaluation metrics:
  - Recall@K
  - MRR
- Evaluation, cache, LLM and observability test coverage.

### Improved
- LLM integrations are isolated behind provider abstractions.
- Observability can follow a request across the API and retrieval/generation path.
- Retrieval quality can be measured programmatically instead of relying solely on demo output.

### Validation
- API tests passed.
- PostgreSQL/pgvector migrations passed.
- Web production build passed.

## 2026-09-23 — Phase 3: AI Product Layer

### Added
- Conversation and message persistence.
- Workspace chat API.
- Streaming chat API using Server-Sent Events.
- Grounded answer generation.
- Citation handling.
- PostgreSQL lexical search.
- pgvector similarity search.
- Hybrid retrieval with Reciprocal Rank Fusion.
- Deterministic reranker.
- Workspace RBAC:
  - owner
  - member
  - viewer
- Bearer authentication boundary.
- Functional web chat workspace.
- PDF, Markdown and TXT ingestion producing persisted chunks and embeddings.

### Improved
- Workspace resources are protected by membership/role checks.
- The frontend exercises the real API path instead of relying on placeholder interactions.
- CI provisions pgvector PostgreSQL and Redis for integration validation.

### Validation
- API test suite passed.
- Database migrations passed.
- Web production build passed.

## 2026-09-23 — Phase 2: Intelligence Core

### Added
- Pydantic settings.
- SQLAlchemy engine/session/base.
- Workspace, source, document and chunk models.
- Shared API contracts.
- Workspace/source/document APIs.
- Ordered SQL migrations.
- Chunking service.
- Embedding provider abstraction.
- Deterministic local embedding provider.
- Reciprocal Rank Fusion primitive.
- Markdown/text parsing.
- Ingestion pipeline.
- PostgreSQL full-text search and pgvector search foundations.

### Improved
- Core intelligence services were separated from the API layer to preserve provider and infrastructure boundaries.
- Ingestion became a reusable pipeline rather than a frontend-specific operation.

### Validation
- Unit and API tests passed through the phase.
- Migration path validated in CI.

## 2026-09-23 — Phase 1: Foundation & Platform Core

### Added
- AtlasAI monorepo structure.
- Next.js web application shell.
- FastAPI API shell.
- Shared package/service boundaries.
- PostgreSQL + pgvector local infrastructure.
- Redis local infrastructure.
- Docker Compose foundation.
- GitHub Actions CI.
- MIT license.
- Architecture documentation.
- Evaluation and architecture decision documentation.
- Environment template and repository hygiene configuration.

### Improved
- Established a single repository boundary for web, API, services, infrastructure, tests and documentation.
- Added a repeatable local development and CI foundation.

## Repository milestone history

| Milestone | Status |
|---|---|
| Phase 1 — Foundation | Complete |
| Phase 2 — Intelligence Core | Complete |
| Phase 3 — AI Product Layer | Complete |
| Phase 4 — Production / AI Engineering Foundations | Complete |
| Production Hardening | Complete |
| Free-tier deployment | Next |
