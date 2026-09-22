# AtlasAI

Production-oriented enterprise knowledge platform for grounded, cited answers over heterogeneous knowledge sources.

## Source of truth
Architecture, ADRs, API contracts, evaluation methodology and backlog are maintained in [Notion](https://app.notion.com/p/3e3bbfeb609681d19663dfabb62a101b?pvs=204). GitHub contains implementation, tests, CI/CD and release artifacts.

## Phase 1 — Foundation
Private development repository. Phase 1 establishes the monorepo, service boundaries, local infrastructure, health API, web shell, contracts and CI.

## Stack
Next.js + TypeScript · FastAPI + Pydantic · PostgreSQL + pgvector · Redis · Docker · GitHub Actions

## Roadmap
M0 Foundation → M1 Ingestion → M2 Retrieval → M3 Generation → M4 Evaluation → M5 Observability → M6 Production Hardening.
