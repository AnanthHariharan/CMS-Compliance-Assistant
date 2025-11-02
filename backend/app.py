"""
FastAPI Application
Main application file for CMS Compliance Assistant
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import json

from backend.models.schemas import (
    QueryRequest,
    QueryResponse,
    VisitNote,
    ComplianceResult,
    HealthStatus,
    SourceReference
)
from backend.retrieval.vector_store import VectorStore
from backend.retrieval.search import create_search_engine
from backend.llm.chains import create_llm_chain
from backend.validation.validator import create_validator

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="CMS Compliance Assistant",
    description="RAG-powered compliance assistant for home health agencies",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for services
vector_store = None
search_engine = None
llm_chain = None
validator = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global vector_store, search_engine, llm_chain, validator

    print("Initializing CMS Compliance Assistant...")

    # Get configuration from environment
    vector_db_path = os.getenv("VECTOR_DB_PATH", "./data/vector_store")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        print("WARNING: OPENAI_API_KEY not set. Some features may not work.")

    try:
        # Initialize vector store
        vector_store = VectorStore(persist_directory=vector_db_path)
        vector_store.create_collection(reset=False)

        # Check if vector store is populated
        stats = vector_store.get_collection_stats()
        if stats['count'] == 0:
            print("WARNING: Vector store is empty. Please run the ingestion script first.")
        else:
            print(f"Vector store loaded with {stats['count']} chunks")

        # Initialize search engine
        search_engine = create_search_engine(
            vector_store=vector_store,
            api_key=openai_api_key
        )

        # Initialize LLM chain
        llm_chain = create_llm_chain(api_key=openai_api_key)

        # Initialize validator
        validator = create_validator(
            search_engine=search_engine,
            llm_chain=llm_chain,
            use_rules=True
        )

        print("Initialization complete!")

    except Exception as e:
        print(f"Error during initialization: {e}")
        print("Some features may not be available.")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "CMS Compliance Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthStatus, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    stats = vector_store.get_collection_stats()

    return HealthStatus(
        status="healthy" if stats['count'] > 0 else "no_data",
        vector_store_count=stats['count'],
        message="Service is operational" if stats['count'] > 0 else "Vector store is empty"
    )


@app.post("/api/query", response_model=QueryResponse, tags=["Q&A"])
async def query_guidelines(request: QueryRequest):
    """
    Query CMS guidelines

    Args:
        request: Query request

    Returns:
        Answer with source references
    """
    if search_engine is None or llm_chain is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Search for relevant context
        context_chunks = search_engine.search(
            query=request.query,
            n_results=request.n_results
        )

        if not context_chunks:
            return QueryResponse(
                answer="I couldn't find relevant information in the CMS guidelines to answer your question. Please try rephrasing or ask a different question.",
                sources=[],
                query=request.query
            )

        # Generate answer
        answer = llm_chain.generate_answer(
            question=request.query,
            context_chunks=context_chunks
        )

        # Format sources
        sources = [
            SourceReference(
                text=chunk['text'][:300] + "..." if len(chunk['text']) > 300 else chunk['text'],
                page_number=chunk.get('page_number'),
                section_header=chunk.get('section_header', ''),
                similarity_score=chunk.get('similarity_score', 0.0)
            )
            for chunk in context_chunks
        ]

        return QueryResponse(
            answer=answer,
            sources=sources,
            query=request.query
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/api/query/stream", tags=["Q&A"])
async def query_guidelines_stream(request: QueryRequest):
    """
    Query CMS guidelines with streaming response

    Args:
        request: Query request

    Returns:
        Streamed answer
    """
    if search_engine is None or llm_chain is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Search for relevant context
        context_chunks = search_engine.search(
            query=request.query,
            n_results=request.n_results
        )

        if not context_chunks:
            async def error_stream():
                yield "I couldn't find relevant information in the CMS guidelines to answer your question."

            return StreamingResponse(error_stream(), media_type="text/plain")

        # Stream answer
        def answer_stream():
            for chunk in llm_chain.stream_answer(
                question=request.query,
                context_chunks=context_chunks
            ):
                yield chunk

        return StreamingResponse(answer_stream(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/api/validate", response_model=ComplianceResult, tags=["Validation"])
async def validate_note(visit_note: VisitNote):
    """
    Validate visit note for CMS compliance

    Args:
        visit_note: Visit note to validate

    Returns:
        Compliance validation result
    """
    if validator is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Validate the note
        result = validator.validate(visit_note.note_text)

        return ComplianceResult(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating note: {str(e)}")


@app.get("/api/stats", tags=["Info"])
async def get_stats():
    """Get system statistics"""
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    stats = vector_store.get_collection_stats()

    return {
        "vector_store": {
            "total_chunks": stats['count'],
            "collection_name": stats.get('name', 'unknown'),
            "path": stats.get('persist_directory', 'unknown')
        },
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
