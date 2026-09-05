from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SessionCreate(BaseModel):
    title: str = Field(
        default="New Conversation",
        max_length=255,
    )


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class Source(BaseModel):
    episode: str | None = None
    guest: str | None = None
    timestamp: str | None = None
    topic: str | None = None
    source_file: str | None = None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: UUID
    role: str
    content: str
    sources: list[Source] | None = None
    created_at: datetime


class ChatRequest(BaseModel):
    session_id: UUID
    message: str = Field(
        min_length=1,
        max_length=10000,
    )


class ArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message_id: int
    artifact_type: str
    content: str


class ChatResponse(BaseModel):
    message: MessageResponse
    artifacts: list[ArtifactResponse] = Field(default_factory=list)