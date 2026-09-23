import os
import mimetypes

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.database.db import get_db
from backend.models.db_models import Document
from backend.models.schemas import SystemHealthResponse


router = APIRouter(
    prefix="/api",
    tags=["Media Streaming & Health"]
)


def stream_file_range(
    file_path: str,
    start: int,
    end: int,
    chunk_size: int = 1024 * 64
):
    with open(file_path, "rb") as f:
        f.seek(start)

        remaining = end - start + 1

        while remaining > 0:
            bytes_to_read = min(
                chunk_size,
                remaining
            )

            data = f.read(bytes_to_read)

            if not data:
                break

            remaining -= len(data)

            yield data


@router.get("/media/{document_id}/stream")
def stream_media(
    document_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Stream the selected media document.

    PDF:
        Display inline inside the browser / iframe.

    Audio / Video:
        Support HTTP Range requests for seeking and playback.
    """

    # ---------------------------------------------------------
    # Find document
    # ---------------------------------------------------------

    doc = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not doc or not os.path.exists(doc.file_path):
        raise HTTPException(
            status_code=404,
            detail="Media file not found"
        )

    # ---------------------------------------------------------
    # Security check
    # ---------------------------------------------------------

    upload_dir_real = os.path.realpath(
        settings.UPLOAD_DIR
    )

    file_path_real = os.path.realpath(
        doc.file_path
    )

    if not file_path_real.startswith(
        upload_dir_real
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied: invalid file path."
        )

    # ---------------------------------------------------------
    # File information
    # ---------------------------------------------------------

    file_size = os.path.getsize(
        doc.file_path
    )

    content_type, _ = mimetypes.guess_type(
        doc.file_path
    )

    if not content_type:
        content_type = "application/octet-stream"

    # =========================================================
    # PDF / DOCUMENT
    # =========================================================

    if doc.media_type in ["pdf", "document"]:

        return FileResponse(
            path=doc.file_path,
            media_type=content_type,
            headers={
                "Content-Disposition": "inline",
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
            }
        )

    # =========================================================
    # AUDIO / VIDEO
    # =========================================================

    range_header = request.headers.get(
        "range"
    )

    if range_header:

        try:
            byte_range = (
                range_header
                .replace("bytes=", "")
                .split("-")
            )

            start = int(
                byte_range[0]
            )

            end = (
                int(byte_range[1])
                if byte_range[1]
                else file_size - 1
            )

        except (
            ValueError,
            IndexError
        ):
            raise HTTPException(
                status_code=416,
                detail="Invalid range"
            )

        if start >= file_size:
            raise HTTPException(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                detail="Range not satisfiable"
            )

        end = min(
            end,
            file_size - 1
        )

        content_length = (
            end - start + 1
        )

        headers = {
            "Content-Range":
                f"bytes {start}-{end}/{file_size}",

            "Accept-Ranges":
                "bytes",

            "Content-Length":
                str(content_length),

            "Content-Type":
                content_type,

            "Content-Disposition":
                "inline",
        }

        return StreamingResponse(
            stream_file_range(
                doc.file_path,
                start,
                end
            ),
            status_code=status.HTTP_206_PARTIAL_CONTENT,
            headers=headers
        )

    # ---------------------------------------------------------
    # Audio / Video without Range header
    # ---------------------------------------------------------

    return FileResponse(
        path=doc.file_path,
        media_type=content_type,
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
            "Content-Disposition": "inline",
        }
    )


# =============================================================
# HEALTH
# =============================================================

@router.get(
    "/health",
    response_model=SystemHealthResponse
)
def health(
    db: Session = Depends(get_db)
):
    db_ok = True

    try:
        db.execute(
            Document.__table__.select().limit(1)
        )
    except Exception:
        db_ok = False

    return SystemHealthResponse(
        status=(
            "HEALTHY"
            if db_ok
            else "DEGRADED"
        ),
        azure_openai_configured=(
            settings.is_azure_openai_configured
        ),
        azure_search_configured=(
            settings.is_azure_search_configured
        ),
        database_connected=db_ok,
        environment=settings.ENVIRONMENT,
        uptime_message=(
            "Smart Media Analysis Agent "
            "Platform is operational."
        )
    )