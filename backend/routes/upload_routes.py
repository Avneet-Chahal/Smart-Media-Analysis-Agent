import os
import shutil
import asyncio
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.database.db import get_db, SessionLocal
from backend.models.db_models import Document, DocumentChunk
from backend.models.schemas import DocumentResponse, DocumentDetailResponse, ChunkSchema
from backend.utils.helpers import detect_media_type, get_file_size
from backend.processing.base import ContentValidationError
from backend.processing.multimodal_processor import multimodal_processor
from backend.rag.rag_engine import rag_engine

from backend.search.azure_search import azure_search_manager

router = APIRouter(prefix="/api", tags=["Media Ingestion & Inventory"])

def process_file_background(document_id: str, file_path: str, media_type: str, filename: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return
        doc.status = "PROCESSING"
        db.commit()

        result = multimodal_processor.process_legacy(file_path, media_type)

        doc.page_count = result.get("page_count")
        doc.duration_seconds = result.get("duration_seconds")

        chunks_data = result.get("chunks", [])
        for c in chunks_data:
            db_chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=c["chunk_index"],
                content=c["content"],
                media_type=c.get("media_type", media_type),
                page_number=c.get("page_number"),
                timestamp_start=c.get("timestamp_start"),
                timestamp_end=c.get("timestamp_end"),
                metadata_json=c.get("metadata")
            )
            db.add(db_chunk)

        db.commit()

        # Vectorize and Index into Azure AI Search
        rag_engine.index_document_chunks(document_id, filename, chunks_data)

        doc.status = "READY" if result.get("success", True) else "ERROR"
        if not result.get("success", True):
            doc.error_message = result.get("error_message")
        db.commit()
    except Exception as e:
        print(f"[UploadRoutes] Error processing {document_id}: {e}")
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = "ERROR"
            doc.error_message = str(e)
            db.commit()
    finally:
        db.close()



@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")

    filename = Path(file.filename.replace('\\', '/')).name
    if not filename or filename in [".", ".."]:
        raise HTTPException(status_code=400, detail="Invalid filename")

    media_type = detect_media_type(filename)
    dest_path = os.path.join(settings.UPLOAD_DIR, filename)

    if os.path.exists(dest_path):
        stem = Path(filename).stem
        ext = Path(filename).suffix
        dest_path = os.path.join(settings.UPLOAD_DIR, f"{stem}_{int(asyncio.get_event_loop().time())}{ext}")

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Validate file integrity, type, and size limits synchronously
    try:
        multimodal_processor.validate_file(dest_path, media_type)
    except ContentValidationError as e:
        if os.path.exists(dest_path):
            try:
                os.remove(dest_path)
            except Exception:
                pass
        raise HTTPException(status_code=400, detail=str(e))

    file_size = get_file_size(dest_path)

    doc = Document(
        filename=filename,
        file_path=dest_path,
        media_type=media_type,
        file_size=file_size,
        mime_type=file.content_type or "",
        status="PROCESSING"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(
        process_file_background,
        document_id=doc.id,
        file_path=dest_path,
        media_type=media_type,
        filename=filename
    )

    return doc


@router.get("/documents", response_model=List[DocumentResponse])
def get_all_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.created_at.desc()).all()


@router.get("/documents/{document_id}", response_model=DocumentDetailResponse)
def get_single_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    chunks_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).count()
    return DocumentDetailResponse(
        id=doc.id,
        filename=doc.filename,
        media_type=doc.media_type,
        file_size=doc.file_size,
        status=doc.status,
        duration_seconds=doc.duration_seconds,
        page_count=doc.page_count,
        summary_text=doc.summary_text,
        key_concepts=doc.key_concepts,
        action_items=doc.action_items,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        chunks_count=chunks_count,
        file_url=f"/api/media/{doc.id}/stream"
    )


@router.get("/documents/{document_id}/chunks", response_model=List[ChunkSchema])
def get_document_chunks(document_id: str, db: Session = Depends(get_db)):
    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index.asc()).all()
    return [
        ChunkSchema(
            id=c.id,
            chunk_index=c.chunk_index,
            content=c.content,
            media_type=c.media_type,
            page_number=c.page_number,
            timestamp_start=c.timestamp_start,
            timestamp_end=c.timestamp_end,
            metadata=c.metadata_json
        )
        for c in chunks
    ]


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    # Clear indexed search chunks
    try:
        azure_search_manager.delete_document_chunks(document_id)
    except Exception:
        pass

    db.delete(doc)
    db.commit()
    return None
