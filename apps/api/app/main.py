from fastapi import FastAPI

from .routes import router
from .routes_chat import router as chat_router
from .routes_conversations import router as conversations_router
from .routes_sources import router as sources_router
from .routes_search import router as search_router

app = FastAPI(title="AtlasAI API", version="0.1.0")
app.include_router(router)
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(sources_router)
app.include_router(search_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
