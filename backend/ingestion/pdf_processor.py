"""
PDF Processing Module
Extracts text from CMS guideline PDFs with metadata preservation
"""

import os
import re
from typing import List, Dict, Tuple
import pdfplumber
from PyPDF2 import PdfReader


class PDFProcessor:
    """Handles PDF text extraction with metadata preservation"""

    def __init__(self, pdf_path: str):
        """
        Initialize PDF processor

        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    def extract_text_with_metadata(self) -> List[Dict[str, any]]:
        """
        Extract text from PDF with page numbers and section headers

        Returns:
            List of dictionaries containing text, page number, and metadata
        """
        pages_data = []

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()

                    if text:
                        # Clean the text
                        text = self._clean_text(text)

                        # Extract section headers if present
                        section_header = self._extract_section_header(text)

                        pages_data.append({
                            'text': text,
                            'page_number': page_num,
                            'section_header': section_header,
                            'char_count': len(text)
                        })

        except Exception as e:
            # Fallback to PyPDF2 if pdfplumber fails
            print(f"pdfplumber failed, trying PyPDF2: {e}")
            pages_data = self._extract_with_pypdf2()

        return pages_data

    def _extract_with_pypdf2(self) -> List[Dict[str, any]]:
        """Fallback extraction using PyPDF2"""
        pages_data = []

        reader = PdfReader(self.pdf_path)
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()

            if text:
                text = self._clean_text(text)
                section_header = self._extract_section_header(text)

                pages_data.append({
                    'text': text,
                    'page_number': page_num,
                    'section_header': section_header,
                    'char_count': len(text)
                })

        return pages_data

    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text

        Args:
            text: Raw text from PDF

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove page numbers pattern (common in PDFs)
        text = re.sub(r'\n\d+\n', '\n', text)

        # Remove special characters that may cause issues
        text = text.replace('\x00', '')

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def _extract_section_header(self, text: str) -> str:
        """
        Extract section header from text

        Args:
            text: Page text

        Returns:
            Section header if found, empty string otherwise
        """
        # Look for common header patterns in CMS documents
        # Patterns like: "10.1 - Section Name" or "Section X: Name"
        patterns = [
            r'^(\d+\.?\d*\s*-\s*[A-Z][^\n]{10,80})',  # Numbered sections with dash
            r'^(Section\s+\d+[:\-]\s*[A-Z][^\n]{10,80})',  # Section X: format
            r'^([A-Z][A-Z\s]{5,50})\n',  # ALL CAPS headers
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return match.group(1).strip()

        return ""

    def get_document_info(self) -> Dict[str, any]:
        """
        Get basic document information

        Returns:
            Dictionary with document metadata
        """
        try:
            reader = PdfReader(self.pdf_path)
            info = {
                'num_pages': len(reader.pages),
                'file_size': os.path.getsize(self.pdf_path),
                'file_name': os.path.basename(self.pdf_path)
            }

            # Try to get PDF metadata
            if reader.metadata:
                info['title'] = reader.metadata.get('/Title', 'Unknown')
                info['author'] = reader.metadata.get('/Author', 'Unknown')
                info['subject'] = reader.metadata.get('/Subject', 'Unknown')

            return info

        except Exception as e:
            print(f"Error getting document info: {e}")
            return {
                'num_pages': 0,
                'file_size': os.path.getsize(self.pdf_path),
                'file_name': os.path.basename(self.pdf_path)
            }


def process_cms_pdf(pdf_path: str) -> Tuple[List[Dict[str, any]], Dict[str, any]]:
    """
    Convenience function to process CMS PDF

    Args:
        pdf_path: Path to PDF file

    Returns:
        Tuple of (pages_data, document_info)
    """
    processor = PDFProcessor(pdf_path)
    pages_data = processor.extract_text_with_metadata()
    doc_info = processor.get_document_info()

    return pages_data, doc_info
