# Free-tier deployment

AtlasAI's portfolio deployment uses a split architecture rather than reproducing the local Docker Compose topology on one host.

## Target topology

- **Vercel:** Next.js web application
- **Render:** FastAPI API as a web service
- **Supabase:** PostgreSQL + pgvector
- **Upstash:** Redis-compatible cache/queue
- **LLM:** deterministic provider for zero-cost demos, or an external provider behind the existing gateway

This is a **free-tier portfolio/demo environment**, not an SLA-backed production system. Free services can sleep, pause, throttle, or impose resource limits.

## API on Render

Set the service root directory to `apps/api` and use the existing Dockerfile.

Required environment variables:

```text
APP_ENV=production
DATABASE_URL=<Supabase PostgreSQL connection string>
REDIS_URL=<Upstash Redis URL>
AUTH_MODE=jwt
JWT_SECRET=<strong random secret>
CORS_ORIGINS=https://<your-vercel-domain>
```

Optional JWT settings:

```text
JWT_ALGORITHM=HS256
JWT_ISSUER=
JWT_AUDIENCE=
```

Render supplies `PORT`; the container now honors it automatically.

## Database

Run the repository migrations against the managed PostgreSQL instance before exposing the API. Confirm the selected Supabase database has the `vector` extension required by AtlasAI.

The local Compose stack remains the reproducible development environment; hosted infrastructure is substituted through environment configuration.

## Frontend on Vercel

Deploy `apps/web` as a Next.js project from the AtlasAI repository.

Set:

```text
NEXT_PUBLIC_API_URL=https://<your-render-api-domain>
```

After deployment, verify the web app can reach `/health` and that authenticated calls reach the deployed API origin.

## Redis and worker

Upstash provides the Redis-compatible service for cache and queue primitives. The durable worker remains part of the repository's architecture, but the free-tier target does not assume a free always-on background worker from the API host.

Until a separate free worker runtime is selected, do not describe the hosted worker path as fully deployed. Keep the queue contract in place so a dedicated worker can be attached without changing application semantics.

## End-to-end gate

Do not call the free deployment complete until this path is smoke-tested:

`Vercel Web → Render API → Supabase pgvector → hybrid retrieval → generation → cited response`

## Release sequence

1. Create/configure Supabase and enable `vector`.
2. Create the Upstash Redis database and copy its TLS Redis URL.
3. Deploy the FastAPI API on Render and configure environment variables/secrets.
4. Run all repository migrations against Supabase.
5. Deploy the Next.js app on Vercel and point `NEXT_PUBLIC_API_URL` at Render.
6. Verify `/health` and `/ready`.
7. Create a workspace with a JWT-authenticated request.
8. Ingest a Markdown/TXT/PDF fixture and verify persisted chunks/embeddings.
9. Execute hybrid search and chat; verify citations and streaming.
10. Record the production URLs and deployment state in the changelog.
