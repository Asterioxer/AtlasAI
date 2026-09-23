from dataclasses import dataclass
from uuid import UUID

import jwt
from fastapi import Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .models import WorkspaceMember


@dataclass(frozen=True)
class AuthContext:
    subject: str
    role: str


async def require_auth(authorization: str | None = Header(default=None)) -> AuthContext:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    if settings.auth_mode == "local":
        return AuthContext(subject=token, role="member")

    if not settings.jwt_secret:
        raise HTTPException(status_code=503, detail="JWT authentication is not configured")
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer or None,
            audience=settings.jwt_audience or None,
            options={"verify_iss": bool(settings.jwt_issuer), "verify_aud": bool(settings.jwt_audience)},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication token") from exc

    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject:
        raise HTTPException(status_code=401, detail="Token subject is required")
    return AuthContext(subject=subject, role="member")


def require_workspace_access(workspace_id: UUID, auth: AuthContext, db: Session, allowed_roles: set[str] | None = None) -> WorkspaceMember:
    member = db.scalar(select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.subject == auth.subject,
    ))
    if member is None:
        raise HTTPException(status_code=403, detail="Workspace access denied")
    if allowed_roles and member.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Insufficient workspace role")
    return member
