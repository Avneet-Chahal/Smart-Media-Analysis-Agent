"""
Smart Media Analysis Agent - FastAPI Backend Application
Chitkara University - AI-103 Group Project

High-performance REST API supporting multimodal educational content processing,
Hybrid Azure AI Search RAG pipeline, and grounded conversational AI agents.
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.config.settings import settings
from backend.database.db import init_db
from backend.processing.base import ContentValidationError
from backend.routes import upload_routes, agent_routes, quiz_routes, media_routes

# Configure structured application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("SmartMediaAgent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    logger.info("Initializing Smart Media Analysis Agent Backend...")
    init_db()
    logger.info("SQLite Database initialized and verified.")
    logger.info(f"Azure OpenAI Endpoint Configured: {settings.is_azure_openai_configured}")
    logger.info(f"Azure AI Search Configured: {settings.is_azure_search_configured}")
    logger.info(f"Server environment: {settings.ENVIRONMENT} on port {settings.PORT}")
    yield
    logger.info("Gracefully shutting down Smart Media Analysis Agent Backend.")


# OpenAPI Tags Metadata for Interactive Swagger Documentation
TAGS_METADATA = [
    {
        "name": "Media Ingestion & Inventory",
        "description": "Upload, validate, and inventory multimodal educational resources (PDFs, lectures, podcasts, videos)."
    },
    {
        "name": "AI Agent & Reasoning",
        "description": "Grounded educational chat agent, executive study summary generation, and key concept extraction."
    },
    {
        "name": "Interactive Practice Quiz",
        "description": "Curriculum-aligned Multiple Choice Question (MCQ) generation with answer explanations and citations."
    },
    {
        "name": "Media Streaming & Health",
        "description": "Range-based partial-content media streaming (HTTP 206) and system health monitoring."
    }
]

app = FastAPI(
    title="Smart Media Analysis Agent API",
    description=(
        "**Smart Media Analysis Agent for Educational Content**\n\n"
        "An agentic AI educational platform developed for Chitkara University AI-103.\n"
        "Features multimodal document ingestion, dense vector & hybrid search with Azure AI Search, "
        "and grounded reasoning to minimize hallucination."
    ),
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request Logging and Latency Timing Middleware
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"Incoming {request.method} {request.url.path} from {client_host}")

    try:
        response = await call_next(request)
        process_time_ms = (time.time() - start_time) * 1000.0
        logger.info(
            f"Completed {request.method} {request.url.path} -> Status {response.status_code} "
            f"in {process_time_ms:.1f}ms"
        )
        return response
    except Exception as exc:
        process_time_ms = (time.time() - start_time) * 1000.0
        logger.error(f"Unhandled Exception on {request.method} {request.url.path} after {process_time_ms:.1f}ms: {exc}")
        raise exc


# Global Exception Handlers for Clean & Consistent Error Responses
@app.exception_handler(ContentValidationError)
async def content_validation_exception_handler(request: Request, exc: ContentValidationError):
    logger.warning(f"Content Validation Error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"status": "error", "code": 400, "message": str(exc), "details": None}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "code": exc.status_code, "message": exc.detail, "details": None}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Schema Request Validation Error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"status": "error", "code": 422, "message": "Invalid request schema.", "details": exc.errors()}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Internal Server Error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "code": 500, "message": "An internal server error occurred.", "details": str(exc)}
    )


# Register Routers
app.include_router(upload_routes.router)
app.include_router(agent_routes.router)
app.include_router(quiz_routes.router)
app.include_router(media_routes.router)

# Root-level Endpoints for standard REST compliance
# 1. POST /upload
app.add_api_route(
    "/upload",
    upload_routes.upload_document,
    methods=["POST"],
    response_model=upload_routes.DocumentResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload Educational Media (Root Alias)",
    tags=["Media Ingestion & Inventory"]
)

# 2. POST /analyze
app.add_api_route(
    "/analyze",
    agent_routes.analyze_document,
    methods=["POST"],
    response_model=agent_routes.AnalyzeResponse,
    summary="Analyze Educational Media (Root Alias)",
    tags=["AI Agent & Reasoning"]
)

# 3. POST /chat
app.add_api_route(
    "/chat",
    agent_routes.chat_with_agent,
    methods=["POST"],
    response_model=agent_routes.AgentChatResponse,
    summary="Chat with AI Agent (Root Alias)",
    tags=["AI Agent & Reasoning"]
)

# 4. POST /summary
app.add_api_route(
    "/summary",
    agent_routes.get_summary,
    methods=["POST"],
    response_model=agent_routes.SummaryResponse,
    summary="Generate Executive Summary (Root Alias)",
    tags=["AI Agent & Reasoning"]
)

# 5. POST /generate-mcqs
app.add_api_route(
    "/generate-mcqs",
    quiz_routes.create_quiz,
    methods=["POST"],
    response_model=quiz_routes.QuizResponse,
    summary="Generate Grounded MCQs (Root Alias)",
    tags=["Interactive Practice Quiz"]
)

# 6. GET /health
app.add_api_route(
    "/health",
    media_routes.health,
    methods=["GET"],
    response_model=media_routes.SystemHealthResponse,
    summary="System Health & Status (Root Alias)",
    tags=["Media Streaming & Health"]
)


@app.get("/", tags=["Media Streaming & Health"], summary="Root Health & Overview")
def root():
    """Returns project overview and quick reference URLs."""
    return {
        "project": "Smart Media Analysis Agent for Educational Content",
        "course": "AI-103 Group Project (Chitkara University)",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload or /api/upload",
            "analyze": "/analyze or /api/agent/analyze",
            "chat": "/chat or /api/agent/chat",
            "summary": "/summary or /api/agent/summary",
            "generate_mcqs": "/generate-mcqs or /api/generate-mcqs",
            "health": "/health or /api/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
