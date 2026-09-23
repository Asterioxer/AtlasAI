import jwt
import pytest
from fastapi import HTTPException
from app.auth import require_auth
from app.config import settings

@pytest.mark.asyncio
async def test_local_auth_accepts_non_empty_bearer() -> None:
    settings.auth_mode = "local"
    result = await require_auth("Bearer test-user")
    assert result.subject == "test-user"

@pytest.mark.asyncio
async def test_jwt_auth_validates_subject() -> None:
    settings.auth_mode = "jwt"
    settings.jwt_secret = "test-secret"
    token = jwt.encode({"sub": "user-1"}, settings.jwt_secret, algorithm="HS256")
    result = await require_auth(f"Bearer {token}")
    assert result.subject == "user-1"
    settings.auth_mode = "local"

@pytest.mark.asyncio
async def test_jwt_auth_rejects_invalid_token() -> None:
    settings.auth_mode = "jwt"
    settings.jwt_secret = "test-secret"
    with pytest.raises(HTTPException) as error:
        await require_auth("Bearer invalid")
    assert error.value.status_code == 401
    settings.auth_mode = "local"
