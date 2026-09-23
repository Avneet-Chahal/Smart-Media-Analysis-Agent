"""
Embedding generator supporting Azure OpenAI text-embedding-3-small and text-embedding-ada-002.
Provides a deterministic normalized vector fallback for offline testing and local execution.
"""

import hashlib
import math
from typing import List, Optional
from backend.config.settings import settings

try:
    from openai import AzureOpenAI
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    AZURE_OPENAI_AVAILABLE = False


class AzureEmbedder:
    """Generates dense vector embeddings using Azure OpenAI or deterministic local fallback."""

    def __init__(self, vector_dim: int = 1536):
        self.client = None
        self.vector_dim = vector_dim
        if settings.is_azure_openai_configured and AZURE_OPENAI_AVAILABLE:
            try:
                self.client = AzureOpenAI(
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION
                )
            except Exception as e:
                print(f"[AzureEmbedder] Init Warning: {e}")

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generates a 1536-dimensional embedding vector for input educational text."""
        if not text or not text.strip():
            return None

        # 1. Try Azure OpenAI Embedding API
        if self.client and settings.is_azure_openai_configured:
            try:
                response = self.client.embeddings.create(
                    input=text[:8000],
                    model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
                )
                return response.data[0].embedding
            except Exception as e:
                print(f"[AzureEmbedder] Azure embedding generation error: {e}")

        # 2. Deterministic normalized embedding fallback for offline testing
        return self._generate_local_fallback_embedding(text)

    def _generate_local_fallback_embedding(self, text: str) -> List[float]:
        """Creates a deterministic unit-length pseudo-embedding for local testing."""
        clean_words = text.lower().split()
        vector = [0.0] * self.vector_dim
        for word in clean_words:
            # Hash word to a specific dimension
            h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            dim_idx = h % self.vector_dim
            val = ((h >> 8) % 1000) / 1000.0
            vector[dim_idx] += val

        # Normalize vector to unit length (L2 norm)
        sq_sum = sum(v * v for v in vector)
        if sq_sum > 0:
            norm = math.sqrt(sq_sum)
            vector = [v / norm for v in vector]
        else:
            vector[0] = 1.0

        return vector


embedder = AzureEmbedder()

