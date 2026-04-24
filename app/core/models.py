from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ChatSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now)
    user_label: Optional[str] = None
    status: str = Field(default="open")


class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(index=True)
    role: str
    content: str
    transcript: Optional[str] = None
    answer: Optional[str] = None
    confidence: Optional[float] = None
    escalate: Optional[bool] = None
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)


class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(index=True)
    issue_type: str
    status: str = Field(default="open")
    summary: str
    created_at: datetime = Field(default_factory=utc_now)


class KBDocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_filename: str
    stored_filename: str = Field(index=True)
    relative_path: str
    content_type: Optional[str] = None
    size_bytes: int
    created_at: datetime = Field(default_factory=utc_now)