"""
Tests for document ingestion pipeline
"""

import pytest
import os
from backend.ingestion.pdf_processor import PDFProcessor
from backend.ingestion.chunker import TextChunker


class TestPDFProcessor:
    """Test PDF processing functionality"""

    def test_pdf_exists(self):
        """Test that the PDF file exists"""
        pdf_path = "./data/raw/Medicare_Benefit_Policy_Manual.pdf"
        assert os.path.exists(pdf_path), f"PDF not found at {pdf_path}"

    def test_pdf_processor_init(self):
        """Test PDFProcessor initialization"""
        pdf_path = "./data/raw/Medicare_Benefit_Policy_Manual.pdf"
        if os.path.exists(pdf_path):
            processor = PDFProcessor(pdf_path)
            assert processor.pdf_path == pdf_path

    def test_pdf_extraction(self):
        """Test PDF text extraction"""
        pdf_path = "./data/raw/Medicare_Benefit_Policy_Manual.pdf"
        if os.path.exists(pdf_path):
            processor = PDFProcessor(pdf_path)
            pages_data = processor.extract_text_with_metadata()

            assert len(pages_data) > 0, "No pages extracted"
            assert 'text' in pages_data[0], "Missing text field"
            assert 'page_number' in pages_data[0], "Missing page_number field"


class TestTextChunker:
    """Test text chunking functionality"""

    def test_chunker_init(self):
        """Test TextChunker initialization"""
        chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
        assert chunker.chunk_size == 1000
        assert chunker.chunk_overlap == 200

    def test_chunk_creation(self):
        """Test chunk creation from sample text"""
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)

        sample_pages = [
            {
                'text': "This is a test paragraph. " * 50,
                'page_number': 1,
                'section_header': 'Test Section'
            }
        ]

        chunks = chunker.chunk_documents(sample_pages)

        assert len(chunks) > 0, "No chunks created"
        assert 'text' in chunks[0], "Missing text field"
        assert 'chunk_id' in chunks[0], "Missing chunk_id field"
        assert 'page_number' in chunks[0], "Missing page_number field"

    def test_token_counting(self):
        """Test token counting"""
        chunker = TextChunker()
        test_text = "Hello, this is a test."
        token_count = chunker._count_tokens(test_text)

        assert token_count > 0, "Token count should be greater than 0"
        assert isinstance(token_count, int), "Token count should be integer"
