import pytest
from fastapi import HTTPException

from app.auth import require_auth


@pytest.mark.asyncio
async def test_auth_requires_bearer_token() -> None:
    with pytest.raises(HTTPException) as exc:
        await require_auth(None)
    assert exc.value.status_code == 401
