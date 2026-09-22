from fastapi import FastAPI

from .routes import router
from .routes_chat import router as chat_router

app = FastAPI(title="AtlasAI API", version="0.1.0")
app.include_router(router)
app.include_router(chat_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
