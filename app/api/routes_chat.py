from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.agent.pipeline import run_support_pipeline
from app.core.db import get_session
from app.core.models import ChatMessage, ChatSession, Ticket
from app.core.schemas import (
    ChatHistoryMessage,
    ChatHistoryResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatStartRequest,
    ChatStartResponse,
    TicketResponse,
)
from app.guardrails.tickets import build_ticket_summary, infer_issue_type

router = APIRouter()


@router.post("/chat/start", response_model=ChatStartResponse)
def start_chat(
    payload: ChatStartRequest,
    db: Session = Depends(get_session),
) -> ChatStartResponse:
    session = ChatSession(user_label=payload.user_label)
    db.add(session)
    db.commit()
    db.refresh(session)

    return ChatStartResponse(session_id=session.id, status=session.status)


@router.post("/chat/{session_id}/message", response_model=ChatMessageResponse)
def send_chat_message(
    session_id: int,
    payload: ChatMessageRequest,
    db: Session = Depends(get_session),
) -> ChatMessageResponse:
    session_obj = db.get(ChatSession, session_id)
    if session_obj is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    user_message = ChatMessage(
        session_id=session_id,
        role="user",
        content=payload.query,
    )
    db.add(user_message)

    pipeline_result = run_support_pipeline(query=payload.query)

    assistant_message = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=pipeline_result.answer,
        transcript=pipeline_result.transcript,
        answer=pipeline_result.answer,
        confidence=pipeline_result.confidence,
        escalate=pipeline_result.escalate,
        reason=pipeline_result.reason,
    )
    db.add(assistant_message)

    ticket_id = None
    if pipeline_result.escalate:
        issue_type = infer_issue_type(payload.query)
        ticket = Ticket(
            session_id=session_id,
            issue_type=issue_type,
            summary=build_ticket_summary(payload.query, issue_type),
        )
        db.add(ticket)
        db.commit()
        
        db.refresh(ticket)
        ticket_id = ticket.id
    else:
        db.commit()

    return ChatMessageResponse(
        session_id=session_id,
        answer=pipeline_result.answer,
        transcript=pipeline_result.transcript,
        evidence=pipeline_result.evidence,
        confidence=pipeline_result.confidence,
        escalate=pipeline_result.escalate,
        reason=pipeline_result.reason,
        ticket_id=ticket_id,
    )


@router.get("/chat/{session_id}", response_model=ChatHistoryResponse)
def get_chat_history(
    session_id: int,
    db: Session = Depends(get_session),
) -> ChatHistoryResponse:
    session_obj = db.get(ChatSession, session_id)
    if session_obj is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    messages = db.exec(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.id)
    ).all()

    return ChatHistoryResponse(
        session_id=session_id,
        status=session_obj.status,
        messages=[
            ChatHistoryMessage(
                id=message.id,
                role=message.role,
                content=message.content,
                transcript=message.transcript,
                answer=message.answer,
                confidence=message.confidence,
                escalate=message.escalate,
                reason=message.reason,
                created_at=message.created_at.isoformat(),
            )
            for message in messages
        ],
    )


@router.get("/tickets", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_session)) -> list[TicketResponse]:
    tickets = db.exec(select(Ticket).order_by(Ticket.id.desc())).all()

    return [
        TicketResponse(
            id=ticket.id,
            session_id=ticket.session_id,
            issue_type=ticket.issue_type,
            status=ticket.status,
            summary=ticket.summary,
            created_at=ticket.created_at.isoformat(),
        )
        for ticket in tickets
    ]