"""
Text Chunking Module
Implements intelligent chunking strategy with context preservation
"""

import re
from typing import List, Dict
import tiktoken


class TextChunker:
    """Handles intelligent text chunking with overlap and context preservation"""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        encoding_name: str = "cl100k_base"
    ):
        """
        Initialize text chunker

        Args:
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Number of overlapping tokens between chunks
            encoding_name: OpenAI encoding to use for token counting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)

    def chunk_documents(
        self,
        pages_data: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        """
        Chunk document pages intelligently

        Args:
            pages_data: List of page data from PDF processor

        Returns:
            List of chunks with metadata
        """
        all_chunks = []
        chunk_id = 0

        for page_data in pages_data:
            text = page_data['text']
            page_number = page_data['page_number']
            section_header = page_data.get('section_header', '')

            # Split into paragraphs first to maintain context
            paragraphs = self._split_into_paragraphs(text)

            # Create chunks from paragraphs
            chunks = self._create_chunks_from_paragraphs(
                paragraphs,
                page_number,
                section_header
            )

            for chunk_text in chunks:
                chunk_id += 1
                all_chunks.append({
                    'chunk_id': chunk_id,
                    'text': chunk_text,
                    'page_number': page_number,
                    'section_header': section_header,
                    'token_count': self._count_tokens(chunk_text),
                    'char_count': len(chunk_text)
                })

        return all_chunks

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs

        Args:
            text: Input text

        Returns:
            List of paragraphs
        """
        # Split by double newlines or multiple spaces
        paragraphs = re.split(r'\n\n+|\n\s*\n', text)

        # Clean and filter empty paragraphs
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        return paragraphs

    def _create_chunks_from_paragraphs(
        self,
        paragraphs: List[str],
        page_number: int,
        section_header: str
    ) -> List[str]:
        """
        Create chunks from paragraphs with overlap

        Args:
            paragraphs: List of paragraphs
            page_number: Page number
            section_header: Section header

        Returns:
            List of chunk texts
        """
        chunks = []
        current_chunk = []
        current_tokens = 0

        # Add section header context if available
        header_context = ""
        if section_header:
            header_context = f"[{section_header}]\n\n"
            header_tokens = self._count_tokens(header_context)
        else:
            header_tokens = 0

        for para in paragraphs:
            para_tokens = self._count_tokens(para)

            # If single paragraph exceeds chunk size, split it
            if para_tokens > self.chunk_size - header_tokens:
                # Save current chunk if exists
                if current_chunk:
                    chunk_text = header_context + " ".join(current_chunk)
                    chunks.append(chunk_text)
                    current_chunk = []
                    current_tokens = 0

                # Split large paragraph into sentences
                sentences = self._split_into_sentences(para)
                sub_chunks = self._create_chunks_from_sentences(
                    sentences,
                    header_context,
                    header_tokens
                )
                chunks.extend(sub_chunks)

            # If adding paragraph would exceed chunk size, save current chunk
            elif current_tokens + para_tokens > self.chunk_size - header_tokens:
                if current_chunk:
                    chunk_text = header_context + " ".join(current_chunk)
                    chunks.append(chunk_text)

                    # Start new chunk with overlap
                    overlap_text = self._get_overlap_text(current_chunk)
                    current_chunk = [overlap_text, para] if overlap_text else [para]
                    current_tokens = self._count_tokens(" ".join(current_chunk))
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens

            else:
                # Add paragraph to current chunk
                current_chunk.append(para)
                current_tokens += para_tokens

        # Add final chunk
        if current_chunk:
            chunk_text = header_context + " ".join(current_chunk)
            chunks.append(chunk_text)

        return chunks

    def _create_chunks_from_sentences(
        self,
        sentences: List[str],
        header_context: str,
        header_tokens: int
    ) -> List[str]:
        """
        Create chunks from sentences (for very long paragraphs)

        Args:
            sentences: List of sentences
            header_context: Section header context
            header_tokens: Token count of header

        Returns:
            List of chunk texts
        """
        chunks = []
        current_chunk = []
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)

            if current_tokens + sentence_tokens > self.chunk_size - header_tokens:
                if current_chunk:
                    chunk_text = header_context + " ".join(current_chunk)
                    chunks.append(chunk_text)

                    # Start new chunk with overlap
                    overlap_text = self._get_overlap_text(current_chunk)
                    current_chunk = [overlap_text, sentence] if overlap_text else [sentence]
                    current_tokens = self._count_tokens(" ".join(current_chunk))
                else:
                    # Single sentence is too long, force it into a chunk
                    chunk_text = header_context + sentence
                    chunks.append(chunk_text)
                    current_chunk = []
                    current_tokens = 0
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens

        # Add final chunk
        if current_chunk:
            chunk_text = header_context + " ".join(current_chunk)
            chunks.append(chunk_text)

        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        # Simple sentence splitting (could be enhanced with NLTK)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _get_overlap_text(self, chunks: List[str]) -> str:
        """
        Get overlap text from previous chunks

        Args:
            chunks: List of text chunks

        Returns:
            Overlap text
        """
        if not chunks:
            return ""

        # Get last few chunks for overlap
        combined = " ".join(chunks)
        overlap_tokens = self.chunk_overlap

        tokens = self.encoding.encode(combined)
        if len(tokens) <= overlap_tokens:
            return combined

        # Get last N tokens for overlap
        overlap_token_ids = tokens[-overlap_tokens:]
        overlap_text = self.encoding.decode(overlap_token_ids)

        return overlap_text

    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text

        Args:
            text: Input text

        Returns:
            Token count
        """
        return len(self.encoding.encode(text))


def chunk_cms_document(
    pages_data: List[Dict[str, any]],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Dict[str, any]]:
    """
    Convenience function to chunk CMS document

    Args:
        pages_data: Pages data from PDF processor
        chunk_size: Maximum tokens per chunk
        chunk_overlap: Overlapping tokens

    Returns:
        List of chunks with metadata
    """
    chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return chunker.chunk_documents(pages_data)
