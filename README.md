# AtlasAI

Production-oriented enterprise knowledge platform for grounded, cited answers over heterogeneous knowledge sources.

## Current status
Phases 1–4 are merged into `main`. The repository now includes the complete core RAG product plus production-hardening foundations: provider-neutral LLM gateway, Redis caching/queue primitives, OpenTelemetry tracing, request correlation, JWT authentication mode, retrieval evaluation metrics, container builds and a multi-service local production stack.

## Production readiness
The production boundary is now explicit. Development defaults use local bearer authentication; production deployments must set `AUTH_MODE=jwt` and configure a strong secret, issuer/audience where applicable, managed PostgreSQL/pgvector and Redis, TLS, secret management, telemetry export and release-time migrations.

## Stack
Next.js + TypeScript · FastAPI + Pydantic · PostgreSQL + pgvector · Redis · Docker · GitHub Actions · OpenTelemetry

## Quality gates
CI provisions PostgreSQL/pgvector and Redis, applies ordered migrations, runs the full API test suite, builds both production containers, and performs a production web build.

## Roadmap
M0 Foundation → M1 Ingestion → M2 Retrieval → M3 Generation → M4 Evaluation → M5 Observability → M6 Production Hardening → Production.
