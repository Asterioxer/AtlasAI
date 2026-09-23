# AtlasAI

Production-oriented enterprise knowledge platform for grounded, cited answers over heterogeneous knowledge sources.

## Source of truth
Architecture, ADRs, API contracts, evaluation methodology and backlog are maintained in [Notion](https://app.notion.com/p/3e3bbfeb609681d19663dfabb62a101b?pvs=204). GitHub contains implementation, tests, CI/CD and release artifacts.

## Current status
Phases 1–3 are merged into `main`. Phase 4 adds production engineering foundations: provider-neutral LLM HTTP gateway, OpenTelemetry tracing, request correlation and security headers, process metrics, Redis cache primitives, and retrieval evaluation metrics.

## Stack
Next.js + TypeScript · FastAPI + Pydantic · PostgreSQL + pgvector · Redis · Docker · GitHub Actions · OpenTelemetry

## Quality gates
API CI provisions pgvector/PostgreSQL, applies ordered migrations and runs the full pytest suite. The web job performs a production build. Retrieval evaluation includes Recall@K and MRR primitives for golden-dataset regression tests.

## Roadmap
M0 Foundation → M1 Ingestion → M2 Retrieval → M3 Generation → M4 Evaluation → M5 Observability → M6 Production Hardening.
