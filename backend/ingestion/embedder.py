"""
Embedding Generation Module
Handles embedding generation using OpenAI API
"""

import os
from typing import List, Dict
import openai
from openai import OpenAI
import time


class EmbeddingGenerator:
    """Generates embeddings using OpenAI's embedding models"""

    def __init__(
        self,
        api_key: str = None,
        model: str = "text-embedding-3-small",
        batch_size: int = 100
    ):
        """
        Initialize embedding generator

        Args:
            api_key: OpenAI API key (defaults to env variable)
            model: Embedding model to use
            batch_size: Number of texts to embed at once
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.batch_size = batch_size

    def generate_embeddings(
        self,
        chunks: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        """
        Generate embeddings for text chunks

        Args:
            chunks: List of chunk dictionaries with 'text' field

        Returns:
            Chunks with added 'embedding' field
        """
        total_chunks = len(chunks)
        print(f"Generating embeddings for {total_chunks} chunks...")

        # Process in batches
        for i in range(0, total_chunks, self.batch_size):
            batch = chunks[i:i + self.batch_size]
            texts = [chunk['text'] for chunk in batch]

            try:
                # Generate embeddings
                response = self.client.embeddings.create(
                    model=self.model,
                    input=texts
                )

                # Add embeddings to chunks
                for j, embedding_obj in enumerate(response.data):
                    chunks[i + j]['embedding'] = embedding_obj.embedding

                print(f"Processed {min(i + self.batch_size, total_chunks)}/{total_chunks} chunks")

                # Rate limiting (optional, adjust as needed)
                if i + self.batch_size < total_chunks:
                    time.sleep(0.5)

            except Exception as e:
                print(f"Error generating embeddings for batch {i}: {e}")
                # Add empty embeddings for failed batch
                for j in range(len(batch)):
                    if 'embedding' not in chunks[i + j]:
                        chunks[i + j]['embedding'] = None

        return chunks

    def generate_single_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=[text]
            )
            return response.data[0].embedding

        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None


def embed_chunks(
    chunks: List[Dict[str, any]],
    api_key: str = None,
    model: str = "text-embedding-3-small"
) -> List[Dict[str, any]]:
    """
    Convenience function to embed chunks

    Args:
        chunks: List of chunks
        api_key: OpenAI API key
        model: Embedding model

    Returns:
        Chunks with embeddings
    """
    embedder = EmbeddingGenerator(api_key=api_key, model=model)
    return embedder.generate_embeddings(chunks)
