import pytest
from backend.rag.rag_engine import rag_engine

def test_local_hybrid_ranking():
    chunks = [
        {"id": "c1", "content": "Convolutional Neural Networks excel at computer vision tasks.", "media_type": "pdf", "page_number": 1},
        {"id": "c2", "content": "Recurrent Neural Networks and LSTMs process sequential time series data.", "media_type": "pdf", "page_number": 2},
        {"id": "c3", "content": "Transformers utilize self-attention mechanisms for natural language understanding.", "media_type": "pdf", "page_number": 3}
    ]

    results = rag_engine._local_hybrid_search(query="self-attention transformers", chunks=chunks, top_k=2)
    assert len(results) > 0
    assert results[0]["chunk_id"] == "c3"
