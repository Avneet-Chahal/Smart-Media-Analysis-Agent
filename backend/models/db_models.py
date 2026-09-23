import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from backend.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    media_type = Column(String(32), nullable=False)  # 'pdf', 'audio', 'video'
    file_size = Column(Integer, default=0)
    mime_type = Column(String(128), default="")
    status = Column(String(32), default="PENDING", index=True)  # PENDING, PROCESSING, READY, ERROR
    error_message = Column(Text, nullable=True)
    
    # Analyzed Content Metadata
    duration_seconds = Column(Float, nullable=True)
    page_count = Column(Integer, nullable=True)
    summary_text = Column(Text, nullable=True)
    key_concepts = Column(JSON, nullable=True)  # List of {concept, description, timestamp/page}
    action_items = Column(JSON, nullable=True)  # List of strings

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="document", cascade="all, delete-orphan")
    quizzes = relationship("GeneratedQuiz", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(64), primary_key=True, default=generate_uuid, index=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    media_type = Column(String(32), nullable=False)
    page_number = Column(Integer, nullable=True)
    timestamp_start = Column(Float, nullable=True)
    timestamp_end = Column(Float, nullable=True)
    metadata_json = Column(JSON, nullable=True)

    document = relationship("Document", back_populates="chunks")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True, index=True)
    role = Column(String(32), nullable=False)  # 'user', 'assistant'
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True)  # List of citation objects
    tools_used = Column(JSON, nullable=True)  # List of tool names called
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="chat_messages")

class GeneratedQuiz(Base):
    __tablename__ = "generated_quizzes"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), default="Educational Quiz")
    difficulty = Column(String(32), default="medium")
    questions = Column(JSON, nullable=False)  # List of MCQ objects
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="quizzes")
