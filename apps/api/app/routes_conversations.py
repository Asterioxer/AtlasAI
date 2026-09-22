from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .conversation_models import Conversation, Message
from .conversation_schemas import ConversationRead, MessageCreate, MessageRead
from .db import get_db
from .models import Workspace

router = APIRouter(prefix="/api/v1")


@router.post("/workspaces/{workspace_id}/conversations", response_model=ConversationRead, status_code=201)
def create_conversation(workspace_id: UUID, db: Session = Depends(get_db)):
    if db.get(Workspace, workspace_id) is None:
        raise HTTPException(404, "Workspace not found")
    conversation = Conversation(workspace_id=workspace_id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("/workspaces/{workspace_id}/conversations", response_model=list[ConversationRead])
def list_conversations(workspace_id: UUID, db: Session = Depends(get_db)):
    if db.get(Workspace, workspace_id) is None:
        raise HTTPException(404, "Workspace not found")
    return db.scalars(
        select(Conversation).where(Conversation.workspace_id == workspace_id).order_by(Conversation.created_at.desc())
    ).all()


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageRead])
def list_messages(conversation_id: UUID, db: Session = Depends(get_db)):
    if db.get(Conversation, conversation_id) is None:
        raise HTTPException(404, "Conversation not found")
    return db.scalars(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
    ).all()


@router.post("/conversations/{conversation_id}/messages", response_model=MessageRead, status_code=201)
def create_message(conversation_id: UUID, payload: MessageCreate, db: Session = Depends(get_db)):
    if db.get(Conversation, conversation_id) is None:
        raise HTTPException(404, "Conversation not found")
    message = Message(conversation_id=conversation_id, **payload.model_dump())
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
