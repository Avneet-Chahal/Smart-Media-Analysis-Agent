"""
Indexing module for pushing vector and text chunks into Azure AI Search.
"""

from typing import List, Dict, Any
from backend.search.azure_search import azure_search_manager
from backend.rag.embedder import embedder

class AzureRAGIndexer:
    """Indexes multimodal educational chunks into Azure AI Search."""

    @classmethod
    def index_chunks(cls, document_id: str, filename: str, chunks: List[Dict[str, Any]]) -> int:
        search_docs = []
        for c in chunks:
            vector = embedder.generate_embedding(c["content"])
            chunk_idx = c.get("chunk_index", 0)
            doc = {
                "id": f"{document_id}_{chunk_idx}",
                "document_id": document_id,
                "chunk_index": chunk_idx,
                "content": c["content"],
                "media_type": c.get("content_type", c.get("media_type", "document")),
                "page_number": c.get("page_number"),
                "timestamp_start": c.get("timestamp_start"),
                "timestamp_end": c.get("timestamp_end"),
                "source_filename": filename,
            }
            if vector:
                doc["vector"] = vector
            search_docs.append(doc)

        azure_search_manager.upload_chunks(search_docs)
        return len(search_docs)

indexer = AzureRAGIndexer()
