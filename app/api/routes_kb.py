import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, select

from app.core.config import settings
from app.core.db import get_session
from app.core.models import KBDocument
from app.core.schemas import KBDocumentResponse, KBReindexResponse, KBUploadResponse
from app.retrieval.index_admin import clear_retrieval_caches
from app.retrieval.loader import SUPPORTED_KB_SUFFIXES, load_markdown_documents
from app.retrieval.search import build_chunk_index

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
KB_DIR = BASE_DIR / "knowledge_base"
UPLOAD_DIR = KB_DIR / "uploads"


def _safe_filename(filename: str) -> str:
    stem = Path(filename).stem.lower()
    stem = re.sub(r"[^a-z0-9_-]+", "-", stem)
    stem = re.sub(r"-+", "-", stem).strip("-")
    return stem or "document"


def _validate_kb_upload(file: UploadFile, content: bytes) -> str:
    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in SUPPORTED_KB_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported KB file type: {suffix}. Use .md or .txt.",
        )

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded document is empty.")

    max_bytes = settings.max_kb_upload_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Document exceeds {settings.max_kb_upload_mb} MB limit.",
        )

    try:
        content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="Document must be valid UTF-8 text.",
        ) from exc

    return suffix


@router.post("/kb/upload", response_model=KBUploadResponse)
async def upload_kb_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
) -> KBUploadResponse:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    content = await file.read()
    suffix = _validate_kb_upload(file, content)

    safe_stem = _safe_filename(file.filename or "document")
    stored_filename = f"{uuid4().hex[:10]}_{safe_stem}{suffix}"
    target_path = UPLOAD_DIR / stored_filename

    target_path.write_bytes(content)

    relative_path = str(target_path.relative_to(KB_DIR))

    document = KBDocument(
        original_filename=file.filename or stored_filename,
        stored_filename=stored_filename,
        relative_path=relative_path,
        content_type=file.content_type,
        size_bytes=len(content),
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    clear_retrieval_caches()

    return KBUploadResponse(
        id=document.id,
        filename=document.original_filename,
        stored_filename=document.stored_filename,
        size_bytes=document.size_bytes,
        message="Knowledge-base document uploaded and index cache cleared.",
    )


@router.get("/kb/documents", response_model=list[KBDocumentResponse])
def list_kb_documents(db: Session = Depends(get_session)) -> list[KBDocumentResponse]:
    uploaded_docs = db.exec(select(KBDocument).order_by(KBDocument.id.desc())).all()
    uploaded_filenames = {doc.stored_filename for doc in uploaded_docs}

    responses: list[KBDocumentResponse] = []

    for doc in uploaded_docs:
        responses.append(
            KBDocumentResponse(
                id=doc.id,
                filename=doc.original_filename,
                source_type="uploaded",
                size_bytes=doc.size_bytes,
                created_at=doc.created_at.isoformat(),
            )
        )

    for path in sorted(KB_DIR.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SUPPORTED_KB_SUFFIXES:
            continue
        if path.name in uploaded_filenames:
            continue

        responses.append(
            KBDocumentResponse(
                id=None,
                filename=path.name,
                source_type="system",
                size_bytes=path.stat().st_size,
                created_at=None,
            )
        )

    return responses


@router.delete("/kb/documents/{document_id}")
def delete_kb_document(
    document_id: int,
    db: Session = Depends(get_session),
) -> dict[str, str]:
    document = db.get(KBDocument, document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Uploaded KB document not found.")

    target_path = KB_DIR / document.relative_path

    if target_path.exists():
        target_path.unlink()

    db.delete(document)
    db.commit()

    clear_retrieval_caches()

    return {"message": "Knowledge-base document deleted and index cache cleared."}


@router.post("/kb/reindex", response_model=KBReindexResponse)
def reindex_kb() -> KBReindexResponse:
    clear_retrieval_caches()

    docs = load_markdown_documents(KB_DIR)
    chunks = build_chunk_index()

    return KBReindexResponse(
        document_count=len(docs),
        chunk_count=len(chunks),
        message="Knowledge-base index cache cleared and rebuilt.",
    )