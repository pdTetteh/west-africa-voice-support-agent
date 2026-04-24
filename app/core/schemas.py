from typing import List, Optional

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    source: str
    chunk_id: str
    snippet: str


class RetrievedChunk(BaseModel):
    source: str
    chunk_id: str
    text: str
    score: float


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User support query")


class AskResponse(BaseModel):
    transcript: Optional[str] = None
    answer: str
    evidence: List[EvidenceItem]
    confidence: float
    escalate: bool
    reason: str


class TranscribeResponse(BaseModel):
    transcript: str


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str


class EvalExample(BaseModel):
    id: str
    query: str
    expected_primary_source: str
    expected_escalation: bool
    gold_points: List[str]


class EvalSummary(BaseModel):
    total_examples: int
    top1_retrieval_accuracy: float
    evidence_recall_at_3: float
    escalation_accuracy: float
    average_gold_coverage: float
    average_confidence: float
    unsupported_answer_count: int
    report_path: str


class ChatStartRequest(BaseModel):
    user_label: Optional[str] = None


class ChatStartResponse(BaseModel):
    session_id: int
    status: str


class ChatMessageRequest(BaseModel):
    query: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    session_id: int
    answer: str
    transcript: Optional[str] = None
    evidence: List[EvidenceItem]
    confidence: float
    escalate: bool
    reason: str
    ticket_id: Optional[int] = None


class ChatHistoryMessage(BaseModel):
    id: int
    role: str
    content: str
    transcript: Optional[str] = None
    answer: Optional[str] = None
    confidence: Optional[float] = None
    escalate: Optional[bool] = None
    reason: Optional[str] = None
    created_at: str


class ChatHistoryResponse(BaseModel):
    session_id: int
    status: str
    messages: List[ChatHistoryMessage]


class TicketResponse(BaseModel):
    id: int
    session_id: int
    issue_type: str
    status: str
    summary: str
    created_at: str