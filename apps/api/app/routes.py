from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db import get_db
from .models import Document, Source, Workspace
from .schemas import DocumentCreate, DocumentRead, SourceCreate, SourceRead, WorkspaceCreate, WorkspaceRead

router = APIRouter(prefix="/api/v1")

@router.post("/workspaces", response_model=WorkspaceRead, status_code=201)
def create_workspace(payload: WorkspaceCreate, db: Session = Depends(get_db)):
    item = Workspace(name=payload.name); db.add(item); db.commit(); db.refresh(item); return item

@router.get("/workspaces", response_model=list[WorkspaceRead])
def list_workspaces(db: Session = Depends(get_db)):
    return db.scalars(select(Workspace).order_by(Workspace.created_at.desc())).all()

@router.post("/workspaces/{workspace_id}/sources", response_model=SourceRead, status_code=201)
def create_source(workspace_id: UUID, payload: SourceCreate, db: Session = Depends(get_db)):
    if db.get(Workspace, workspace_id) is None: raise HTTPException(404, "Workspace not found")
    item = Source(workspace_id=workspace_id, **payload.model_dump()); db.add(item); db.commit(); db.refresh(item); return item

@router.post("/sources/{source_id}/documents", response_model=DocumentRead, status_code=201)
def create_document(source_id: UUID, payload: DocumentCreate, db: Session = Depends(get_db)):
    if db.get(Source, source_id) is None: raise HTTPException(404, "Source not found")
    item = Document(source_id=source_id, **payload.model_dump()); db.add(item); db.commit(); db.refresh(item); return item
