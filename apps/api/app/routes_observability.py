from fastapi import APIRouter

from .services.observability import metrics_snapshot

router = APIRouter(prefix="/api/v1", tags=["observability"])

@router.get("/metrics")
async def metrics() -> dict[str, dict[str, int]]:
    return {"counters": metrics_snapshot()}
