import os
import tempfile
import pytest
from pathlib import Path

from backend.utils.helpers import detect_media_type, format_timestamp
from backend.processing.base import (
    NormalizedContentItem,
    MultimodalProcessingResult,
    ContentValidationError
)
from backend.processing.chunker import SemanticChunker
from backend.processing.document_processor import DocumentProcessor
from backend.processing.audio_processor import AudioProcessor
from backend.processing.video_processor import VideoProcessor
from backend.processing.multimodal_processor import MultimodalProcessor, multimodal_processor
from backend.rag.rag_engine import rag_engine


def test_type_detection():
    assert detect_media_type("lecture.pdf") == "pdf"
    assert detect_media_type("audio.mp3") == "audio"
    assert detect_media_type("voice_note.wav") == "audio"
    assert detect_media_type("video.mp4") == "video"
    assert detect_media_type("screen_record.mkv") == "video"
    assert detect_media_type("notes.txt") == "document"
    assert detect_media_type("summary.md") == "document"


def test_timestamp_formatter():
    assert format_timestamp(0.0) == "00:00"
    assert format_timestamp(65.0) == "01:05"
    assert format_timestamp(3665.0) == "01:01:05"


def test_semantic_chunker():
    text = "Paragraph 1 is about AI.\n\nParagraph 2 is about RAG.\n\nParagraph 3 is about Agents."
    chunks = SemanticChunker.chunk_text(text, max_chars=50, overlap=10)
    assert len(chunks) >= 2


def test_pdf_validation_and_corrupted_file_handling():
    """PDF Input Validation: non-existent file, empty file, and invalid PDF header checks."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Non-existent file
        with pytest.raises(ContentValidationError):
            DocumentProcessor.validate_file(os.path.join(tmpdir, "missing.pdf"), "pdf")

        # 2. Empty file (0 bytes)
        empty_pdf = os.path.join(tmpdir, "empty.pdf")
        with open(empty_pdf, "wb") as f:
            pass
        with pytest.raises(ContentValidationError, match="is empty"):
            DocumentProcessor.validate_file(empty_pdf, "pdf")

        # 3. Corrupted PDF (missing %PDF header)
        fake_pdf = os.path.join(tmpdir, "fake.pdf")
        with open(fake_pdf, "wb") as f:
            f.write(b"NOT_A_REAL_PDF_HEADER_DATA")
        with pytest.raises(ContentValidationError, match="missing %PDF header"):
            DocumentProcessor.validate_file(fake_pdf, "pdf")


def test_pdf_processing_normalized_contract():
    """PDF Content Extraction & Normalized Output Format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "Lecture_01_ML.pdf")
        try:
            import fitz
            doc = fitz.open()
            page1 = doc.new_page()
            page1.insert_text((50, 72), "Chapter 1: Supervised Learning.\nSupervised learning maps input features X to ground truth target labels Y.")
            page2 = doc.new_page()
            page2.insert_text((50, 72), "Chapter 2: Loss Functions.\nMean Squared Error measures empirical variance between prediction and target.")
            doc.save(pdf_path)
            doc.close()
        except ImportError:
            # Fallback mock PDF with %PDF header
            with open(pdf_path, "wb") as f:
                f.write(b"%PDF-1.4 mock pdf content with Chapter 1: Supervised Learning")

        result = DocumentProcessor.process_normalized(pdf_path, "pdf")
        assert result.success is True
        assert result.source == "Lecture_01_ML.pdf"
        assert result.content_type == "pdf"
        assert len(result.items) >= 1

        first_item = result.items[0]
        assert isinstance(first_item, NormalizedContentItem)
        assert first_item.source == "Lecture_01_ML.pdf"
        assert first_item.content_type == "pdf"
        assert first_item.metadata.get("page") == 1
        assert "Supervised Learning" in first_item.text or "mock" in first_item.text


def test_audio_validation_and_processing():
    """Audio Input Validation, Speech Segmentation, and Normalized Output Format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Invalid audio extension
        bad_audio = os.path.join(tmpdir, "lecture.xyz")
        with open(bad_audio, "wb") as f:
            f.write(b"data")
        with pytest.raises(ContentValidationError, match="Unsupported audio format"):
            AudioProcessor.validate_file(bad_audio)

        # 2. Valid WAV file with RIFF container
        wav_path = os.path.join(tmpdir, "Lecture_02_Calculus.wav")
        with open(wav_path, "wb") as f:
            f.write(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00" + b"\x00" * 50000)

        result = AudioProcessor.process_normalized(wav_path)
        assert result.success is True
        assert result.content_type == "audio"
        assert len(result.items) >= 2

        first_segment = result.items[0]
        assert first_segment.metadata.get("timestamp") == "00:00"
        assert first_segment.metadata.get("timestamp_start") == 0.0
        assert first_segment.metadata.get("timestamp_end") > 0.0
        assert "section" in first_segment.metadata
        assert "Calculus" in first_segment.text


def test_video_validation_and_processing():
    """Video Input Validation, Chapter Alignment, and Normalized Output Format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Corrupted container check
        fake_mp4 = os.path.join(tmpdir, "fake.mp4")
        with open(fake_mp4, "wb") as f:
            f.write(b"BAD_CONTAINER_BYTES_WITHOUT_FTYP")
        with pytest.raises(ContentValidationError, match="Corrupted or invalid MP4"):
            VideoProcessor.validate_file(fake_mp4)

        # 2. Valid MP4 container with ftyp atom
        mp4_path = os.path.join(tmpdir, "Lecture_03_Neural_Networks.mp4")
        with open(mp4_path, "wb") as f:
            f.write(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom" + b"\x00" * 100000)

        result = VideoProcessor.process_normalized(mp4_path)
        assert result.success is True
        assert result.content_type == "video"
        assert len(result.items) >= 3

        item = result.items[0]
        assert item.content_type == "video"
        assert item.metadata.get("timestamp") is not None
        assert item.metadata.get("timestamp_start") == 0.0
        assert "section" in item.metadata
        assert "Neural Networks" in item.text


def test_multimodal_processor_router_and_rag_conversion():
    """Unified Multimodal Router: Dispatches correctly and ensures downstream RAG consistency."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a text notes document
        notes_path = os.path.join(tmpdir, "Attention_Mechanism_Notes.txt")
        with open(notes_path, "w", encoding="utf-8") as f:
            f.write("Section 1: Attention Basics.\nSelf-attention allows tokens to dynamically attend to all context positions.")

        result = multimodal_processor.process_file(notes_path)
        assert result.success is True
        assert result.content_type == "document"
        assert len(result.items) >= 1

        # Test conversion to downstream RAG chunks
        rag_chunks = result.to_rag_chunks()
        assert len(rag_chunks) == len(result.items)
        assert rag_chunks[0]["content"] == result.items[0].text
        assert rag_chunks[0]["source_filename"] == "Attention_Mechanism_Notes.txt"
        assert rag_chunks[0]["page_number"] == 1

        # Verify downstream RAG indexing and retrieval works directly with the chunks
        rag_engine.index_document_chunks("doc_multimodal_test", "Attention_Mechanism_Notes.txt", rag_chunks)
        retrieved = rag_engine.retrieve_context("dynamically attend context positions", document_id="doc_multimodal_test")
        assert len(retrieved) >= 1
        assert "Self-attention allows tokens" in retrieved[0]["content"]
