"""
Vector Store Module
Manages ChromaDB vector database for document retrieval
"""

import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions


class VectorStore:
    """Manages vector storage and retrieval using ChromaDB"""

    def __init__(
        self,
        persist_directory: str = "./data/vector_store",
        collection_name: str = "cms_guidelines"
    ):
        """
        Initialize vector store

        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        self.collection = None

    def create_collection(self, reset: bool = False):
        """
        Create or get collection

        Args:
            reset: If True, delete existing collection and create new one
        """
        if reset:
            try:
                self.client.delete_collection(name=self.collection_name)
                print(f"Deleted existing collection: {self.collection_name}")
            except Exception as e:
                print(f"No existing collection to delete: {e}")

        # Create collection without embedding function (we'll provide embeddings)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "CMS Medicare guidelines for home health"}
        )

        print(f"Collection '{self.collection_name}' ready")

    def add_chunks(
        self,
        chunks: List[Dict[str, any]],
        batch_size: int = 100
    ):
        """
        Add chunks to vector store

        Args:
            chunks: List of chunks with embeddings
            batch_size: Batch size for adding documents
        """
        if not self.collection:
            self.create_collection()

        total_chunks = len(chunks)
        print(f"Adding {total_chunks} chunks to vector store...")

        # Filter chunks with valid embeddings
        valid_chunks = [c for c in chunks if c.get('embedding') is not None]
        if len(valid_chunks) < total_chunks:
            print(f"Warning: {total_chunks - len(valid_chunks)} chunks have no embeddings")

        # Process in batches
        for i in range(0, len(valid_chunks), batch_size):
            batch = valid_chunks[i:i + batch_size]

            ids = [f"chunk_{chunk['chunk_id']}" for chunk in batch]
            documents = [chunk['text'] for chunk in batch]
            embeddings = [chunk['embedding'] for chunk in batch]
            metadatas = [
                {
                    'chunk_id': chunk['chunk_id'],
                    'page_number': chunk['page_number'],
                    'section_header': chunk.get('section_header', ''),
                    'token_count': chunk.get('token_count', 0)
                }
                for chunk in batch
            ]

            try:
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
                print(f"Added {min(i + batch_size, len(valid_chunks))}/{len(valid_chunks)} chunks")

            except Exception as e:
                print(f"Error adding batch {i}: {e}")

        print(f"Successfully added chunks to vector store")

    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Search for similar chunks

        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            Search results
        """
        if not self.collection:
            raise ValueError("Collection not initialized. Call create_collection() first.")

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata,
                include=['documents', 'metadatas', 'distances']
            )

            return results

        except Exception as e:
            print(f"Error searching vector store: {e}")
            return {
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]]
            }

    def get_collection_stats(self) -> Dict[str, any]:
        """
        Get collection statistics

        Returns:
            Statistics dictionary
        """
        if not self.collection:
            return {'count': 0}

        try:
            count = self.collection.count()
            return {
                'count': count,
                'name': self.collection_name,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {'count': 0}

    def delete_collection(self):
        """Delete the collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = None
            print(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            print(f"Error deleting collection: {e}")


def initialize_vector_store(
    chunks: List[Dict[str, any]],
    persist_directory: str = "./data/vector_store",
    collection_name: str = "cms_guidelines",
    reset: bool = False
) -> VectorStore:
    """
    Initialize and populate vector store

    Args:
        chunks: Chunks with embeddings
        persist_directory: Directory for ChromaDB
        collection_name: Collection name
        reset: Reset existing collection

    Returns:
        Initialized VectorStore instance
    """
    store = VectorStore(
        persist_directory=persist_directory,
        collection_name=collection_name
    )

    store.create_collection(reset=reset)
    store.add_chunks(chunks)

    stats = store.get_collection_stats()
    print(f"Vector store initialized with {stats['count']} chunks")

    return store
