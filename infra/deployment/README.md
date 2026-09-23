# Production deployment

AtlasAI production consists of the Next.js web container, FastAPI API container, Redis, a background worker, and PostgreSQL/pgvector.

## Required controls
- set AUTH_MODE=jwt and provide a strong JWT_SECRET, or replace the verifier with the organization's OIDC/JWKS verifier
- use managed PostgreSQL/pgvector and Redis with TLS
- store secrets in the deployment platform, never in Git
- terminate TLS at the ingress/load balancer
- export OpenTelemetry to the organization's collector
- run database migrations as a release step before switching traffic
- configure health checks against /health
- run the worker as a separate process/container
- keep local auth disabled outside development

## Release sequence
1. Build and scan API/web images.
2. Apply database migrations.
3. Start API, worker, Redis and web.
4. Verify /health and a representative authenticated API flow.
5. Shift traffic only after health checks pass.
