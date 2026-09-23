import math
from typing import List, Dict, Any, Optional
from backend.config.settings import settings

try:
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndex,
        SimpleField,
        SearchFieldDataType,
        SearchableField,
        SearchField,
        VectorSearch,
        HnswAlgorithmConfiguration,
        VectorSearchProfile
    )
    from azure.search.documents.models import VectorizedQuery
    AZURE_SEARCH_AVAILABLE = True
except ImportError:
    AZURE_SEARCH_AVAILABLE = False


class AzureSearchManager:
    """Manages index creation, document indexing, and hybrid vector queries with Azure AI Search."""

    def __init__(self):
        self.search_client = None
        self.index_client = None
        self._local_index: List[Dict[str, Any]] = []

        if settings.is_azure_search_configured and AZURE_SEARCH_AVAILABLE:
            try:
                credential = AzureKeyCredential(settings.AZURE_SEARCH_API_KEY)
                self.search_client = SearchClient(
                    endpoint=settings.AZURE_SEARCH_ENDPOINT,
                    index_name=settings.AZURE_SEARCH_INDEX_NAME,
                    credential=credential
                )
                self.index_client = SearchIndexClient(
                    endpoint=settings.AZURE_SEARCH_ENDPOINT,
                    credential=credential
                )
                self._ensure_index()
            except Exception as e:
                print(f"[AzureSearch] Init Warning: {e}")

    def _ensure_index(self):
        if not self.index_client:
            return
        try:
            indices = [i.name for i in self.index_client.list_indexes()]
            if settings.AZURE_SEARCH_INDEX_NAME not in indices:
                fields = [
                    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                    SimpleField(name="document_id", type=SearchFieldDataType.String, filterable=True, facetable=True),
                    SimpleField(name="chunk_index", type=SearchFieldDataType.Int32),
                    SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="standard.lucene"),
                    SimpleField(name="media_type", type=SearchFieldDataType.String, filterable=True),
                    SimpleField(name="page_number", type=SearchFieldDataType.Int32, filterable=True),
                    SimpleField(name="timestamp_start", type=SearchFieldDataType.Double, filterable=True),
                    SimpleField(name="timestamp_end", type=SearchFieldDataType.Double, filterable=True),
                    SimpleField(name="source_filename", type=SearchFieldDataType.String, filterable=True),
                    SearchField(
                        name="vector",
                        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        searchable=True,
                        vector_search_dimensions=1536,
                        vector_search_profile_name="eduHnswProfile"
                    )
                ]
                vector_search = VectorSearch(
                    profiles=[VectorSearchProfile(name="eduHnswProfile", algorithm_configuration_name="eduHnsw")],
                    algorithms=[HnswAlgorithmConfiguration(name="eduHnsw")]
                )
                index = SearchIndex(
                    name=settings.AZURE_SEARCH_INDEX_NAME,
                    fields=fields,
                    vector_search=vector_search
                )
                self.index_client.create_index(index)
                print(f"[AzureSearch] Created Azure AI Search Index: {settings.AZURE_SEARCH_INDEX_NAME}")
        except Exception as e:
            print(f"[AzureSearch] Ensure index error: {e}")

    def upload_chunks(self, docs: List[Dict[str, Any]]):
        """Indexes chunks in Azure AI Search and maintains local cache."""
        if not docs:
            return

        # Store in local index for instant search fallback
        for doc in docs:
            # Replace existing if id matches
            self._local_index = [d for d in self._local_index if d.get("id") != doc.get("id")]
            self._local_index.append(doc)

        # Upload to Azure AI Search if configured
        if self.search_client:
            try:
                self.search_client.upload_documents(documents=docs)
            except Exception as e:
                print(f"[AzureSearch] Document upload failed: {e}")

    def delete_document_chunks(self, document_id: str):
        """Removes indexed chunks for a document from local search index and Azure AI Search."""
        if not document_id:
            return
        self._local_index = [d for d in self._local_index if d.get("document_id") != document_id]
        if self.search_client:
            try:
                results = self.search_client.search(
                    search_text="*",
                    filter=f"document_id eq '{document_id}'",
                    select=["id"]
                )
                ids_to_delete = [{"id": r["id"]} for r in results]
                if ids_to_delete:
                    self.search_client.delete_documents(documents=ids_to_delete)
            except Exception as e:
                print(f"[AzureSearch] Delete documents failed: {e}")

    def search_hybrid(
        self,
        query: str,
        query_vector: Optional[List[float]] = None,
        document_id: Optional[str] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """Performs hybrid vector + text search on Azure AI Search or fallback local index."""
        # 1. Try Azure AI Search
        if self.search_client:
            try:
                filter_expr = f"document_id eq '{document_id}'" if document_id else None
                vector_queries = []
                if query_vector:
                    vector_queries.append(
                        VectorizedQuery(vector=query_vector, k_nearest_neighbors=top_k, fields="vector")
                    )

                results = self.search_client.search(
                    search_text=query,
                    vector_queries=vector_queries if vector_queries else None,
                    filter=filter_expr,
                    top=top_k
                )

                retrieved = []
                for r in results:
                    retrieved.append({
                        "chunk_id": r["id"],
                        "content": r["content"],
                        "media_type": r.get("media_type", "document"),
                        "page_number": r.get("page_number"),
                        "timestamp_start": r.get("timestamp_start"),
                        "timestamp_end": r.get("timestamp_end"),
                        "source_filename": r.get("source_filename", "Lecture"),
                        "score": r.get("@search.score", 1.0)
                    })
                if retrieved:
                    return retrieved
            except Exception as e:
                print(f"[AzureSearch] Azure Search query failed: {e}")

        # 2. Local Fallback Hybrid Search on indexed chunks
        if self._local_index:
            return self._search_local_index(query, query_vector, document_id, top_k)

        return []

    def _search_local_index(
        self,
        query: str,
        query_vector: Optional[List[float]],
        document_id: Optional[str],
        top_k: int
    ) -> List[Dict[str, Any]]:
        import re
        q_lower = query.lower()
        stop_words = {
            "what", "is", "the", "capital", "of", "and", "in", "a", "an", "to", "for",
            "with", "on", "at", "by", "from", "are", "do", "does", "did", "can", "how",
            "why", "which", "this", "that", "it", "be", "explain", "tell", "me", "about",
            "was", "were", "been", "being", "have", "has", "had", "having", "when", "where",
            "who", "whom", "whose", "which", "will", "would", "shall", "should", "may",
            "might", "must", "can", "could", "during", "between", "through", "under", "above",
            "into", "within", "against", "after", "before", "out", "over", "then", "there",
            "also", "such", "only", "than", "too", "very", "as", "signed"
        }
        all_words = re.findall(r'\w+', q_lower)
        meaningful_query_words = set(w for w in all_words if w not in stop_words and len(w) > 2) or set(all_words)

        candidates = self._local_index
        if document_id:
            candidates = [d for d in candidates if d.get("document_id") == document_id]

        scored = []
        for doc in candidates:
            content = doc.get("content", "")
            content_lower = content.lower()
            content_words = set(re.findall(r'\w+', content_lower))

            # Lexical score
            overlap = len(meaningful_query_words.intersection(content_words))
            phrase_bonus = 3.0 if q_lower in content_lower else 0.0

            # If no meaningful words overlap and phrase is not in content, it's irrelevant
            if overlap == 0 and phrase_bonus == 0.0:
                continue

            # If 3+ keywords in query, require at least 2 overlapping keywords unless exact phrase matched
            if len(meaningful_query_words) >= 3 and overlap < 2 and phrase_bonus == 0.0:
                continue

            lexical_score = (overlap / max(len(meaningful_query_words), 1)) * 2.0 + phrase_bonus

            # Vector cosine similarity
            vector_score = 0.0
            if query_vector and "vector" in doc and doc["vector"]:
                doc_vec = doc["vector"]
                dot = sum(a * b for a, b in zip(query_vector, doc_vec))
                if dot > 0.2:
                    vector_score = dot * 1.5

            total_score = lexical_score + vector_score

            if total_score >= 0.4:
                scored.append({
                    "chunk_id": str(doc.get("id", "c1")),
                    "content": content,
                    "media_type": doc.get("media_type", "document"),
                    "page_number": doc.get("page_number"),
                    "timestamp_start": doc.get("timestamp_start"),
                    "timestamp_end": doc.get("timestamp_end"),
                    "source_filename": doc.get("source_filename", "Lecture"),
                    "score": total_score
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]


azure_search_manager = AzureSearchManager()

