"""
Document Ingestion Script
Processes PDF, chunks text, generates embeddings, and stores in vector DB
"""

import os
import sys
from dotenv import load_dotenv
import json

from backend.ingestion.pdf_processor import process_cms_pdf
from backend.ingestion.chunker import chunk_cms_document
from backend.ingestion.embedder import embed_chunks
from backend.retrieval.vector_store import initialize_vector_store


def main():
    """Main ingestion process"""
    print("=" * 60)
    print("CMS Compliance Assistant - Document Ingestion")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    # Configuration
    pdf_path = os.getenv("PDF_PATH", "./data/raw/Medicare_Benefit_Policy_Manual.pdf")
    vector_db_path = os.getenv("VECTOR_DB_PATH", "./data/vector_store")
    processed_data_path = "./data/processed/chunks.json"
    chunk_size = int(os.getenv("MAX_CHUNK_SIZE", 1000))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 200))
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        print("ERROR: OPENAI_API_KEY not found in environment variables")
        print("Please set it in .env file or export it")
        sys.exit(1)

    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF file not found at {pdf_path}")
        sys.exit(1)

    print(f"\nConfiguration:")
    print(f"  PDF Path: {pdf_path}")
    print(f"  Vector DB Path: {vector_db_path}")
    print(f"  Chunk Size: {chunk_size} tokens")
    print(f"  Chunk Overlap: {chunk_overlap} tokens")
    print()

    # Step 1: Extract text from PDF
    print("Step 1: Extracting text from PDF...")
    try:
        pages_data, doc_info = process_cms_pdf(pdf_path)
        print(f"  ✓ Extracted {len(pages_data)} pages")
        print(f"  ✓ Document: {doc_info.get('file_name', 'Unknown')}")
        print(f"  ✓ Total pages: {doc_info.get('num_pages', 0)}")
    except Exception as e:
        print(f"  ✗ Error extracting PDF: {e}")
        sys.exit(1)

    # Step 2: Chunk text
    print("\nStep 2: Chunking text...")
    try:
        chunks = chunk_cms_document(
            pages_data=pages_data,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        print(f"  ✓ Created {len(chunks)} chunks")
        avg_tokens = sum(c['token_count'] for c in chunks) / len(chunks)
        print(f"  ✓ Average chunk size: {avg_tokens:.0f} tokens")
    except Exception as e:
        print(f"  ✗ Error chunking text: {e}")
        sys.exit(1)

    # Step 3: Generate embeddings
    print("\nStep 3: Generating embeddings...")
    try:
        chunks_with_embeddings = embed_chunks(
            chunks=chunks,
            api_key=openai_api_key
        )

        # Count successful embeddings
        successful = sum(1 for c in chunks_with_embeddings if c.get('embedding') is not None)
        print(f"  ✓ Generated {successful}/{len(chunks)} embeddings")

        if successful < len(chunks):
            print(f"  ⚠ Warning: {len(chunks) - successful} chunks failed to generate embeddings")

    except Exception as e:
        print(f"  ✗ Error generating embeddings: {e}")
        sys.exit(1)

    # Step 4: Save processed data
    print("\nStep 4: Saving processed data...")
    try:
        os.makedirs(os.path.dirname(processed_data_path), exist_ok=True)

        # Save chunks (without embeddings for readability)
        chunks_to_save = []
        for chunk in chunks_with_embeddings:
            chunk_copy = chunk.copy()
            # Remove embedding for JSON storage (too large)
            if 'embedding' in chunk_copy:
                chunk_copy['has_embedding'] = chunk_copy['embedding'] is not None
                del chunk_copy['embedding']
            chunks_to_save.append(chunk_copy)

        with open(processed_data_path, 'w') as f:
            json.dump({
                'document_info': doc_info,
                'total_chunks': len(chunks_to_save),
                'chunks': chunks_to_save
            }, f, indent=2)

        print(f"  ✓ Saved processed data to {processed_data_path}")

    except Exception as e:
        print(f"  ⚠ Warning: Could not save processed data: {e}")

    # Step 5: Initialize vector store
    print("\nStep 5: Initializing vector store...")
    try:
        vector_store = initialize_vector_store(
            chunks=chunks_with_embeddings,
            persist_directory=vector_db_path,
            collection_name="cms_guidelines",
            reset=True  # Reset existing collection
        )

        stats = vector_store.get_collection_stats()
        print(f"  ✓ Vector store initialized")
        print(f"  ✓ Total documents: {stats['count']}")

    except Exception as e:
        print(f"  ✗ Error initializing vector store: {e}")
        sys.exit(1)

    # Summary
    print("\n" + "=" * 60)
    print("Ingestion Complete!")
    print("=" * 60)
    print(f"Total chunks processed: {len(chunks)}")
    print(f"Chunks in vector store: {stats['count']}")
    print(f"Vector store location: {vector_db_path}")
    print("\nYou can now start the API server:")
    print("  python backend/app.py")
    print("  or")
    print("  uvicorn backend.app:app --reload")
    print("=" * 60)


if __name__ == "__main__":
    main()
