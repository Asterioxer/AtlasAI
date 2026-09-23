import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes import router
from .routes_chat import router as chat_router
from .routes_conversations import router as conversations_router
from .routes_sources import router as sources_router
from .routes_search import router as search_router
from .routes_stream import router as stream_router
from .routes_observability import router as observability_router
from .services.observability import record_metric, request_id, tracer

app = FastAPI(title="AtlasAI API", version="0.2.0")

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(router)
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(sources_router)
app.include_router(search_router)
app.include_router(stream_router)
app.include_router(observability_router)


@app.middleware("http")
async def request_observability(request: Request, call_next):
    rid = request.headers.get("x-request-id") or request_id()
    started = time.perf_counter()
    with tracer.start_as_current_span("http.request") as span:
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.route", request.url.path)
        span.set_attribute("http.request_id", rid)
        try:
            response = await call_next(request)
        except Exception as exc:
            span.record_exception(exc)
            record_metric("http.5xx")
            raise
        elapsed = (time.perf_counter() - started) * 1000
        span.set_attribute("http.status_code", response.status_code)
        span.set_attribute("http.duration_ms", elapsed)
        record_metric(f"http.{response.status_code // 100}xx")
        response.headers["x-request-id"] = rid
        response.headers["x-content-type-options"] = "nosniff"
        response.headers["x-frame-options"] = "DENY"
        response.headers["referrer-policy"] = "no-referrer"
        return response


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready"}
