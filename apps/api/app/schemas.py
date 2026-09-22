from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class WorkspaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str


class SourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    source_type: str = Field(min_length=1, max_length=50)


class SourceRead(SourceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    workspace_id: UUID


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1)


class DocumentRead(DocumentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    source_id: UUID


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    limit: int = Field(default=8, ge=1, le=30)


class SearchResult(BaseModel):
    chunk_id: UUID
    source_id: UUID
    document_id: UUID
    score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]
