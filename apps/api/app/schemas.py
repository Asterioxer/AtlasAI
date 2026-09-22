from uuid import UUID
from pydantic import BaseModel
class WorkspaceCreate(BaseModel): name: str
class WorkspaceRead(BaseModel): id: UUID; name: str
class SourceCreate(BaseModel): name: str; source_type: str
class SourceRead(SourceCreate): id: UUID; workspace_id: UUID
class DocumentCreate(BaseModel): title: str; content: str
class DocumentRead(DocumentCreate): id: UUID; source_id: UUID
