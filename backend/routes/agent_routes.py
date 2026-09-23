from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.models.db_models import ChatMessage, Document, DocumentChunk
from backend.models.schemas import (
    AgentChatRequest,
    AgentChatResponse,
    SummaryRequest,
    SummaryResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    KeyConceptItem,
    ChatHistoryItem,
)
from backend.agent.agent_service import agent_service


router = APIRouter(
    prefix="/api/agent",
    tags=["AI Agent & Reasoning"],
)


# =========================================================
# HELPER — NORMALIZE SUMMARY TIMESTAMPS
# =========================================================

def normalize_timestamp(value: Any):
    """
    Convert timestamps returned by the AI into the numeric
    format expected by KeyConceptItem.

    Examples:

        12.5
            -> 12.5

        "12.5"
            -> 12.5

        "00:00 - 00:15"
            -> 0.0

        "01:25 - 01:40"
            -> 85.0

        None
            -> None
    """

    if value is None:
        return None

    # Already numeric
    if isinstance(value, (int, float)):
        return float(value)

    # String timestamp
    if isinstance(value, str):
        value = value.strip()

        if not value:
            return None

        # ---------------------------------------------
        # Case 1:
        # "00:00 - 00:15"
        # ---------------------------------------------
        if "-" in value:
            start_time = value.split("-", 1)[0].strip()
            return _timestamp_to_seconds(start_time)

        # ---------------------------------------------
        # Case 2:
        # "00:15"
        # ---------------------------------------------
        return _timestamp_to_seconds(value)

    return None


def _timestamp_to_seconds(timestamp: str):
    """
    Convert:
        SS
        MM:SS
        HH:MM:SS

    into seconds.
    """

    try:
        parts = timestamp.strip().split(":")

        if len(parts) == 1:
            return float(parts[0])

        if len(parts) == 2:
            minutes = float(parts[0])
            seconds = float(parts[1])

            return minutes * 60 + seconds

        if len(parts) == 3:
            hours = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])

            return (
                hours * 3600
                + minutes * 60
                + seconds
            )

    except (ValueError, TypeError):
        pass

    return None


# =========================================================
# CHAT
# =========================================================

@router.post(
    "/chat",
    response_model=AgentChatResponse,
    summary="Chat with AI Agent",
    description="Query the grounded RAG agent with contextual citations.",
)
def chat_with_agent(
    request: AgentChatRequest,
    db: Session = Depends(get_db),
):

    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty.",
        )

    history_dicts = [
        {
            "role": h.role,
            "content": h.content,
        }
        for h in (request.chat_history or [])
    ]

    try:

        result = agent_service.chat(
            db=db,
            query=request.query,
            document_id=request.document_id,
            chat_history=history_dicts,
        )

        # -------------------------------------------------
        # Store user message
        # -------------------------------------------------

        db.add(
            ChatMessage(
                document_id=request.document_id,
                role="user",
                content=request.query,
            )
        )

        # -------------------------------------------------
        # Store assistant message
        # -------------------------------------------------

        citations_json = [
            c.model_dump()
            for c in result.get("citations", [])
        ]

        db.add(
            ChatMessage(
                document_id=request.document_id,
                role="assistant",
                content=result.get("response", ""),
                citations=citations_json,
                tools_used=result.get("tools_used", []),
            )
        )

        db.commit()

        return AgentChatResponse(
            response=result.get("response", ""),
            citations=result.get("citations", []),
            tools_used=result.get("tools_used", []),
            is_grounded=result.get("is_grounded", False),
            grounding_status=result.get(
                "grounding_status",
                "NOT_FOUND",
            ),
        )

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        print(
            "[AgentRoutes] Chat error: "
            f"{type(e).__name__}: {e}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}",
        )


# =========================================================
# STUDY SUMMARY
# =========================================================

@router.post(
    "/summary",
    response_model=SummaryResponse,
    summary="Generate Educational Study Notes",
    description="Generates structured study notes, key concepts, and action items from the selected document.",
)
def get_summary(
    request: SummaryRequest,
    db: Session = Depends(get_db),
):

    document_id = request.document_id

    print(
        "[AgentRoutes] Summary requested for document_id: "
        f"{document_id}"
    )

    # -----------------------------------------------------
    # Validate document ID
    # -----------------------------------------------------

    if not document_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="document_id is required.",
        )

    # -----------------------------------------------------
    # Verify document exists
    # -----------------------------------------------------

    doc = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not doc:

        print(
            "[AgentRoutes] Summary document NOT FOUND: "
            f"{document_id}"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Document '{document_id}' was not found "
                "in the database."
            ),
        )

    print(
        "[AgentRoutes] Summary document found: "
        f"{doc.filename} | status={doc.status}"
    )

    # -----------------------------------------------------
    # Check processing status
    # -----------------------------------------------------

    if doc.status == "PROCESSING":

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Document '{doc.filename}' is still being "
                "processed. Please wait until it becomes READY."
            ),
        )

    if doc.status == "ERROR":

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Document processing failed: "
                f"{doc.error_message or 'Unknown processing error.'}"
            ),
        )

    # -----------------------------------------------------
    # Generate summary using Agent Service
    # -----------------------------------------------------

    try:

        data = agent_service.generate_summary(
            db=db,
            document_id=document_id,
        )

        print(
            "[AgentRoutes] Raw summary generated for: "
            f"{doc.filename}"
        )

        # -------------------------------------------------
        # NORMALIZE KEY CONCEPT TIMESTAMPS
        # -------------------------------------------------

        normalized_key_concepts = []

        for concept in data.get("key_concepts", []):

            normalized_concept = {
                "concept": concept.get(
                    "concept",
                    "",
                ),
                "description": concept.get(
                    "description",
                    "",
                ),
                "timestamp": normalize_timestamp(
                    concept.get("timestamp")
                ),
                "page": concept.get("page"),
            }

            normalized_key_concepts.append(
                normalized_concept
            )

        data["key_concepts"] = normalized_key_concepts

        print(
            "[AgentRoutes] Normalized "
            f"{len(normalized_key_concepts)} key concepts."
        )

        # -------------------------------------------------
        # Build validated response
        # -------------------------------------------------

        response = SummaryResponse(
            **data
        )

        print(
            "[AgentRoutes] Summary generated successfully "
            f"for: {doc.filename}"
        )

        return response

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        print(
            "[AgentRoutes] Summary generation error: "
            f"{type(e).__name__}: {e}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to generate educational summary: "
                f"{str(e)}"
            ),
        )


# =========================================================
# COMPREHENSIVE ANALYSIS
# =========================================================

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze Educational Media",
    description="Triggers comprehensive analysis and returns a full study packet.",
)
def analyze_document(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
):

    # -----------------------------------------------------
    # Find document
    # -----------------------------------------------------

    doc = (
        db.query(Document)
        .filter(
            Document.id == request.document_id
        )
        .first()
    )

    if not doc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Document '{request.document_id}' "
                "not found."
            ),
        )

    # -----------------------------------------------------
    # Generate summary
    # -----------------------------------------------------

    try:

        summary_data = agent_service.generate_summary(
            db=db,
            document_id=request.document_id,
        )

        # -------------------------------------------------
        # Normalize timestamps here as well
        # -------------------------------------------------

        normalized_key_concepts = []

        for concept in summary_data.get(
            "key_concepts",
            [],
        ):

            normalized_key_concepts.append(
                KeyConceptItem(
                    concept=concept.get(
                        "concept",
                        "",
                    ),
                    description=concept.get(
                        "description",
                        "",
                    ),
                    timestamp=normalize_timestamp(
                        concept.get("timestamp")
                    ),
                    page=concept.get("page"),
                )
            )

        chunks_count = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id
                == request.document_id
            )
            .count()
        )

        return AnalyzeResponse(
            document_id=doc.id,
            filename=doc.filename,
            media_type=doc.media_type,
            status=doc.status,
            page_count=doc.page_count,
            duration_seconds=doc.duration_seconds,
            chunks_count=chunks_count,
            title=summary_data.get(
                "title",
                f"Study Packet: {doc.filename}",
            ),
            overview=summary_data.get(
                "overview",
                "",
            ),
            key_concepts=normalized_key_concepts,
            action_items=summary_data.get(
                "action_items",
                [],
            ),
            file_url=(
                f"/api/media/{doc.id}/stream"
            ),
        )

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        print(
            "[AgentRoutes] Analyze error: "
            f"{type(e).__name__}: {e}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to analyze media: "
                f"{str(e)}"
            ),
        )


# =========================================================
# CHAT HISTORY
# =========================================================

@router.get(
    "/history/{document_id}",
    response_model=List[ChatHistoryItem],
    summary="Get Chat History",
    description="Retrieves previous chat conversation messages.",
)
def get_history(
    document_id: str,
    db: Session = Depends(get_db),
):

    messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.document_id
            == document_id
        )
        .order_by(
            ChatMessage.created_at.asc()
        )
        .all()
    )

    return [
        ChatHistoryItem(
            role=m.role,
            content=m.content,
        )
        for m in messages
    ]