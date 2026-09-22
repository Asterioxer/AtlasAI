from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import AuthContext, require_auth, require_workspace_access
from .db import get_db
from .models import Document, Source, Workspace, WorkspaceMember
from .schemas import *

router = APIRouter(prefix="/api/v1")


@router.post("/workspaces", response_model=WorkspaceRead, status_code=201)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_auth),
):
    workspace = Workspace(name=payload.name)
    db.add(workspace)
    db.flush()
    db.add(WorkspaceMember(workspace_id=workspace.id, subject=auth.subject, role="owner"))
    db.commit()
    db.refresh(workspace)
    return workspace


@router.get("/workspaces", response_model=list[WorkspaceRead])
def list_workspaces(db: Session = Depends(get_db), auth: AuthContext = Depends(require_auth)):
    return db.scalars(
        select(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .where(WorkspaceMember.subject == auth.subject)
        .order_by(Workspace.created_at.desc())
    ).all()


@router.post("/workspaces/{workspace_id}/sources", response_model=SourceRead, status_code=201)
def create_source(
    workspace_id: UUID,
    payload: SourceCreate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_auth),
):
    require_workspace_access(workspace_id, auth, db, {"owner", "member"})
    if db.get(Workspace, workspace_id) is None:
        raise HTTPException(404, "Workspace not found")
    source = Source(workspace_id=workspace_id, **payload.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.get("/workspaces/{workspace_id}/sources", response_model=list[SourceRead])
def list_sources(workspace_id: UUID, db: Session = Depends(get_db), auth: AuthContext = Depends(require_auth)):
    require_workspace_access(workspace_id, auth, db)
    return db.scalars(select(Source).where(Source.workspace_id == workspace_id).order_by(Source.created_at.desc())).all()


@router.post("/sources/{source_id}/documents", response_model=DocumentRead, status_code=201)
def create_document(
    source_id: UUID,
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_auth),
):
    source = db.get(Source, source_id)
    if source is None:
        raise HTTPException(404, "Source not found")
    require_workspace_access(source.workspace_id, auth, db, {"owner", "member"})
    document = Document(source_id=source_id, **payload.model_dump())
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/sources/{source_id}/documents", response_model=list[DocumentRead])
def list_documents(source_id: UUID, db: Session = Depends(get_db), auth: AuthContext = Depends(require_auth)):
    source = db.get(Source, source_id)
    if source is None:
        raise HTTPException(404, "Source not found")
    require_workspace_access(source.workspace_id, auth, db)
    return db.scalars(select(Document).where(Document.source_id == source_id).order_by(Document.created_at.desc())).all()
