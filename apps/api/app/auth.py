from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_db
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
    return AuthContext(subject=token, role="member")


def require_workspace_access(
    workspace_id: UUID,
    auth: AuthContext,
    db: Session,
    allowed_roles: set[str] | None = None,
) -> WorkspaceMember:
    member = db.scalar(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.subject == auth.subject,
        )
    )
    if member is None:
        raise HTTPException(status_code=403, detail="Workspace access denied")
    if allowed_roles and member.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Insufficient workspace role")
    return member
