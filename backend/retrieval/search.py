"""
Search Module
Handles semantic search and retrieval logic
"""

from typing import List, Dict, Optional
from backend.retrieval.vector_store import VectorStore
from backend.ingestion.embedder import EmbeddingGenerator


class SemanticSearch:
    """Handles semantic search operations"""

    def __init__(
        self,
        vector_store: VectorStore,
        embedder: EmbeddingGenerator
    ):
        """
        Initialize semantic search

        Args:
            vector_store: VectorStore instance
            embedder: EmbeddingGenerator instance
        """
        self.vector_store = vector_store
        self.embedder = embedder

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, any]]:
        """
        Perform semantic search

        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of search results with context
        """
        # Generate query embedding
        query_embedding = self.embedder.generate_single_embedding(query)

        if query_embedding is None:
            return []

        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results,
            filter_metadata=filter_metadata
        )

        # Format results
        formatted_results = self._format_results(results)

        return formatted_results

    def _format_results(self, results: Dict[str, any]) -> List[Dict[str, any]]:
        """
        Format search results

        Args:
            results: Raw results from vector store

        Returns:
            Formatted results
        """
        if not results.get('documents') or not results['documents'][0]:
            return []

        formatted = []

        documents = results['documents'][0]
        metadatas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0]

        for i, doc in enumerate(documents):
            metadata = metadatas[i] if i < len(metadatas) else {}
            distance = distances[i] if i < len(distances) else 1.0

            # Convert distance to similarity score (lower distance = higher similarity)
            similarity_score = 1 - min(distance, 1.0)

            formatted.append({
                'text': doc,
                'page_number': metadata.get('page_number'),
                'section_header': metadata.get('section_header', ''),
                'similarity_score': similarity_score,
                'distance': distance,
                'chunk_id': metadata.get('chunk_id')
            })

        return formatted

    def hybrid_search(
        self,
        query: str,
        n_results: int = 5,
        keywords: Optional[List[str]] = None
    ) -> List[Dict[str, any]]:
        """
        Perform hybrid search (semantic + keyword)

        Args:
            query: Search query
            n_results: Number of results
            keywords: Optional keywords to boost

        Returns:
            Search results
        """
        # Perform semantic search
        semantic_results = self.search(query, n_results=n_results * 2)

        if not keywords:
            return semantic_results[:n_results]

        # Boost results containing keywords
        for result in semantic_results:
            keyword_boost = 0
            text_lower = result['text'].lower()

            for keyword in keywords:
                if keyword.lower() in text_lower:
                    keyword_boost += 0.1

            result['similarity_score'] = min(
                result['similarity_score'] + keyword_boost,
                1.0
            )

        # Re-sort by boosted scores
        semantic_results.sort(key=lambda x: x['similarity_score'], reverse=True)

        return semantic_results[:n_results]


def create_search_engine(
    vector_store: VectorStore,
    api_key: str = None,
    embedding_model: str = "text-embedding-3-small"
) -> SemanticSearch:
    """
    Create search engine instance

    Args:
        vector_store: VectorStore instance
        api_key: OpenAI API key
        embedding_model: Embedding model to use

    Returns:
        SemanticSearch instance
    """
    embedder = EmbeddingGenerator(api_key=api_key, model=embedding_model)
    return SemanticSearch(vector_store=vector_store, embedder=embedder)
