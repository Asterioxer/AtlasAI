from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkspaceCreate(BaseModel):
    name: str


class WorkspaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class SourceCreate(BaseModel):
    name: str
    source_type: str


class SourceRead(SourceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID


class DocumentCreate(BaseModel):
    title: str
    content: str


class DocumentRead(DocumentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID
