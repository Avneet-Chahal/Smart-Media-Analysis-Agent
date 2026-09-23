"""
Semantic and metadata-preserving chunking module for educational content.
"""

import re
from typing import List, Dict, Any, Optional
from backend.rag.cleaner import ContentCleaner

class RAGChunker:
    """Partitions educational text into overlapping chunks with preserved metadata."""

    @classmethod
    def chunk_document(
        cls,
        text: str,
        source_filename: str,
        content_type: str = "document",
        page_number: Optional[int] = None,
        timestamp_start: Optional[float] = None,
        timestamp_end: Optional[float] = None,
        max_chars: int = 750,
        overlap: int = 100
    ) -> List[Dict[str, Any]]:
        cleaned_text = ContentCleaner.clean_text(text)
        if not cleaned_text:
            return []

        raw_chunks = cls._split_into_windows(cleaned_text, max_chars, overlap)
        structured_chunks = []

        for idx, chunk_str in enumerate(raw_chunks):
            # Extract possible topic/section header from first sentence
            first_line = chunk_str.split("\n")[0].split(".")[0].strip()
            topic_section = first_line[:50] if len(first_line) > 5 else f"Section {idx + 1}"

            structured_chunks.append({
                "chunk_index": idx,
                "content": chunk_str,
                "source_filename": source_filename,
                "content_type": content_type,
                "page_number": page_number,
                "timestamp_start": timestamp_start,
                "timestamp_end": timestamp_end,
                "topic_section": topic_section,
                "char_length": len(chunk_str)
            })

        return structured_chunks

    @staticmethod
    def _split_into_windows(text: str, max_chars: int, overlap: int) -> List[str]:
        if len(text) <= max_chars:
            return [text]

        paragraphs = text.split("\n\n")
        chunks: List[str] = []
        current = ""

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue

            if len(current) + len(p) + 2 <= max_chars:
                current = f"{current}\n\n{p}".strip()
            else:
                if current:
                    chunks.append(current)
                if len(p) > max_chars:
                    sentences = re.split(r'(?<=[.?!])\s+', p)
                    sub = ""
                    for s in sentences:
                        if len(sub) + len(s) + 1 <= max_chars:
                            sub = f"{sub} {s}".strip()
                        else:
                            if sub:
                                chunks.append(sub)
                            sub = s
                    if sub:
                        current = sub
                else:
                    current = p

        if current:
            chunks.append(current)

        return chunks
