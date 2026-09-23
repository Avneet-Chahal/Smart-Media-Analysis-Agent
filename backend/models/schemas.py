from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

# Document Schemas
class DocumentBase(BaseModel):
    filename: str
    media_type: str
    file_size: int
    status: str

class DocumentResponse(DocumentBase):
    id: str
    duration_seconds: Optional[float] = None
    page_count: Optional[int] = None
    summary_text: Optional[str] = None
    key_concepts: Optional[List[Dict[str, Any]]] = None
    action_items: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class DocumentDetailResponse(DocumentResponse):
    chunks_count: int = 0
    file_url: str = ""

# Chunk Schema
class ChunkSchema(BaseModel):
    id: str
    chunk_index: int
    content: str
    media_type: str
    page_number: Optional[int] = None
    timestamp_start: Optional[float] = None
    timestamp_end: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

# Citation Schema
class Citation(BaseModel):
    chunk_id: str
    media_type: str  # 'pdf', 'audio', 'video'
    page_number: Optional[int] = None
    timestamp_start: Optional[float] = None
    timestamp_end: Optional[float] = None
    snippet: str
    source_filename: str

# Chat & Agent Schemas
class ChatHistoryItem(BaseModel):
    role: str
    content: str

class AgentChatRequest(BaseModel):
    document_id: Optional[str] = None
    query: str
    chat_history: Optional[List[ChatHistoryItem]] = []

class AgentChatResponse(BaseModel):
    response: str
    citations: List[Citation] = []
    tools_used: List[str] = []
    is_grounded: bool = True
    grounding_status: str = "GROUNDED"

# Summary Schema
class SummaryRequest(BaseModel):
    document_id: str

class KeyConceptItem(BaseModel):
    concept: str
    description: str
    timestamp: Optional[float] = None
    page: Optional[int] = None

class SummaryResponse(BaseModel):
    document_id: str
    title: str
    overview: str
    key_concepts: List[KeyConceptItem] = []
    action_items: List[str] = []

# Quiz Schemas
class QuizRequest(BaseModel):
    document_id: str
    num_questions: int = Field(default=5, ge=1, le=10)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")

class MCQQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_answer_index: int
    explanation: str
    citation: Optional[Dict[str, Any]] = None

class QuizResponse(BaseModel):
    quiz_id: str
    document_id: str
    title: str
    difficulty: str
    questions: List[MCQQuestion]

# Analysis Schemas
class AnalyzeRequest(BaseModel):
    document_id: str = Field(..., description="ID of the uploaded educational media document to analyze")

class AnalyzeResponse(BaseModel):
    document_id: str
    filename: str
    media_type: str
    status: str
    page_count: Optional[int] = None
    duration_seconds: Optional[float] = None
    chunks_count: int = 0
    title: str
    overview: str
    key_concepts: List[KeyConceptItem] = []
    action_items: List[str] = []
    file_url: str = ""

# Error Response Schema
class APIErrorResponse(BaseModel):
    status: str = "error"
    code: int
    message: str
    details: Optional[Any] = None

# Health Schema
class SystemHealthResponse(BaseModel):
    status: str
    azure_openai_configured: bool
    azure_search_configured: bool
    database_connected: bool
    environment: str
    uptime_message: str

