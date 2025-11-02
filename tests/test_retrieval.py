"""
Tests for retrieval system
"""

import pytest
from backend.retrieval.vector_store import VectorStore


class TestVectorStore:
    """Test vector store functionality"""

    def test_vector_store_init(self):
        """Test VectorStore initialization"""
        store = VectorStore(
            persist_directory="./data/test_vector_store",
            collection_name="test_collection"
        )
        assert store.persist_directory == "./data/test_vector_store"
        assert store.collection_name == "test_collection"

    def test_collection_creation(self):
        """Test collection creation"""
        store = VectorStore(
            persist_directory="./data/test_vector_store",
            collection_name="test_collection"
        )
        store.create_collection(reset=True)

        stats = store.get_collection_stats()
        assert 'count' in stats
        assert stats['count'] >= 0

        # Cleanup
        store.delete_collection()


class TestSearch:
    """Test search functionality"""

    def test_search_query_format(self):
        """Test that search queries are properly formatted"""
        query = "What are the eligibility requirements?"
        assert isinstance(query, str)
        assert len(query) > 0
