from dataclasses import dataclass
from fastapi import Header, HTTPException


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
    # Phase 3 local auth boundary. Replace token validation with OIDC/JWT verification in Phase 4.
    return AuthContext(subject=token, role="member")
