"""
Retrieval module for hybrid search, scoring, citation generation, and grounded context preparation.
"""

import math
import re
from typing import List, Dict, Any, Optional
from backend.search.azure_search import azure_search_manager
from backend.rag.embedder import embedder
from backend.models.schemas import Citation


class RAGRetriever:
    """Retrieves relevant educational chunks, scores similarity, and constructs verified citations."""

    @classmethod
    def retrieve(
        cls,
        query: str,
        document_id: Optional[str] = None,
        db_chunks: Optional[List[Any]] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        # 1. Try Azure AI Search with query vector (or in-memory search manager cache)
        query_vector = embedder.generate_embedding(query)
        azure_results = azure_search_manager.search_hybrid(
            query=query,
            query_vector=query_vector,
            document_id=document_id,
            top_k=top_k
        )
        if azure_results:
            return azure_results

        # 2. Local Hybrid Ranker Fallback on database chunks
        if db_chunks:
            return cls._rank_local_chunks(query, db_chunks, top_k)

        return []

    @classmethod
    def build_citations(cls, retrieved_chunks: List[Dict[str, Any]], min_score: float = 0.1) -> List[Citation]:
        """Constructs verified Citation objects from retrieved chunks."""
        citations = []
        for c in retrieved_chunks:
            if c.get("score", 0.0) >= min_score:
                snippet = c.get("content", "")
                if len(snippet) > 160:
                    snippet = snippet[:160] + "..."
                citations.append(Citation(
                    chunk_id=str(c.get("chunk_id", "c1")),
                    media_type=c.get("media_type", "document"),
                    page_number=c.get("page_number"),
                    timestamp_start=c.get("timestamp_start"),
                    timestamp_end=c.get("timestamp_end"),
                    snippet=snippet,
                    source_filename=c.get("source_filename", "Lecture Notes")
                ))
        return citations

    @classmethod
    def format_context_for_agent(cls, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Formats retrieved educational chunks into structured context for the AI Agent.
        Enforces grounding and explicit source citations.
        """
        if not retrieved_chunks:
            return "NO_RELEVANT_CONTEXT"

        context_blocks = []
        for idx, chunk in enumerate(retrieved_chunks, 1):
            source = chunk.get("source_filename", "Lecture")
            loc = ""
            if chunk.get("page_number") is not None:
                loc = f" | Page {chunk['page_number']}"
            elif chunk.get("timestamp_start") is not None:
                start_sec = chunk["timestamp_start"]
                loc = f" | Timestamp {int(start_sec // 60):02d}:{int(start_sec % 60):02d}"

            topic = f" ({chunk.get('topic_section')})" if chunk.get("topic_section") else ""
            block = (
                f"[Source #{idx}: {source}{loc}{topic} | Relevance Score: {chunk.get('score', 1.0):.2f}]\n"
                f"{chunk.get('content', '').strip()}"
            )
            context_blocks.append(block)

        return "\n\n".join(context_blocks)

    @classmethod
    def _rank_local_chunks(cls, query: str, chunks: List[Any], top_k: int) -> List[Dict[str, Any]]:
        stop_words = {
            "is", "in", "a", "an", "the", "and", "or", "of", "to", "for", "with",
            "on", "at", "by", "from", "what", "how", "why", "who", "which", "this",
            "that", "it", "are", "as", "be", "do", "does", "did", "can", "could",
            "during", "between", "through", "under", "above", "into", "within", "about",
            "against", "after", "before", "out", "over", "then", "there", "when", "where",
            "whom", "whose", "will", "would", "shall", "should", "may", "might", "must",
            "also", "such", "only", "than", "too", "very", "explain", "tell", "me"
        }
        all_query_words = re.findall(r'\w+', query.lower())
        query_words = set(w for w in all_query_words if w not in stop_words and len(w) > 2) or set(all_query_words)
        scored = []

        for chunk in chunks:
            text = chunk.content if hasattr(chunk, "content") else chunk.get("content", "")
            chunk_id = chunk.id if hasattr(chunk, "id") else chunk.get("id", "c1")
            media_type = chunk.media_type if hasattr(chunk, "media_type") else chunk.get("media_type", chunk.get("content_type", "document"))
            page_number = chunk.page_number if hasattr(chunk, "page_number") else chunk.get("page_number")
            timestamp_start = chunk.timestamp_start if hasattr(chunk, "timestamp_start") else chunk.get("timestamp_start")
            timestamp_end = chunk.timestamp_end if hasattr(chunk, "timestamp_end") else chunk.get("timestamp_end")
            source_filename = chunk.source_filename if hasattr(chunk, "source_filename") else (chunk.get("source_filename", "Lecture") if isinstance(chunk, dict) else "Lecture")
            topic_section = chunk.metadata_json.get("topic_section") if hasattr(chunk, "metadata_json") and isinstance(chunk.metadata_json, dict) else (chunk.get("topic_section") if isinstance(chunk, dict) else None)

            text_words = re.findall(r'\w+', text.lower())
            total_words = max(len(text_words), 1)

            # Keyword overlap
            overlap = sum(1 for w in query_words if w in text_words)
            phrase_bonus = 2.5 if query.lower() in text.lower() else 0.0

            # If no meaningful keywords overlap and no phrase match, skip
            if overlap == 0 and phrase_bonus == 0.0:
                continue

            # If only 1 keyword overlaps out of multiple query keywords and no phrase match, require significant ratio
            if len(query_words) >= 3 and overlap < 2 and phrase_bonus == 0.0:
                continue

            score = ((overlap / math.log(total_words + 2)) * 1.5) + phrase_bonus

            if score >= 0.35:
                scored.append({
                    "chunk_id": str(chunk_id),
                    "content": text,
                    "media_type": media_type,
                    "page_number": page_number,
                    "timestamp_start": timestamp_start,
                    "timestamp_end": timestamp_end,
                    "source_filename": source_filename,
                    "topic_section": topic_section,
                    "score": score
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]


retriever = RAGRetriever()

