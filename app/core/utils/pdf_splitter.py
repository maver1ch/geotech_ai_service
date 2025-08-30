"""
PDF Page Splitting Utilities
Tools for splitting PDF files into manageable chunks for OCR processing
"""

import logging
import tempfile
from pathlib import Path
from typing import List, Tuple
import fitz  # PyMuPDF

from ..config.constants import RAGConstants

logger = logging.getLogger(__name__)

class PDFPageSplitter:
    """Utility for splitting PDF files into smaller chunks for OCR processing"""
    
    def __init__(self, max_pages_per_chunk: int = RAGConstants.MAX_PAGES_PER_CHUNK):
        """
        Initialize PDF splitter
        
        Args:
            max_pages_per_chunk: Maximum pages per chunk (default: 5)
        """
        self.max_pages_per_chunk = max_pages_per_chunk
        logger.info(f"PDFPageSplitter initialized with max_pages_per_chunk={max_pages_per_chunk}")
    
    def split_pdf_to_chunks(self, pdf_path: str) -> List[Tuple[str, int, int]]:
        """
        Split PDF into temporary chunk files
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of tuples (chunk_file_path, start_page, end_page)
        """
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            logger.info(f"Splitting PDF: {pdf_path.name}")
            
            # Open PDF document
            doc = fitz.open(str(pdf_path))
            total_pages = len(doc)
            
            logger.info(f"Total pages in PDF: {total_pages}")
            
            chunks = []
            
            # Calculate chunks
            for start_page in range(0, total_pages, self.max_pages_per_chunk):
                end_page = min(start_page + self.max_pages_per_chunk - 1, total_pages - 1)
                
                # Create temporary file for this chunk
                temp_file = tempfile.NamedTemporaryFile(
                    suffix=f"_pages_{start_page+1}-{end_page+1}.pdf", 
                    delete=False
                )
                temp_file.close()
                
                # Create new PDF with selected pages
                chunk_doc = fitz.open()
                chunk_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
                chunk_doc.save(temp_file.name)
                chunk_doc.close()
                
                chunks.append((temp_file.name, start_page + 1, end_page + 1))
                logger.debug(f"Created chunk: pages {start_page+1}-{end_page+1} -> {temp_file.name}")
            
            doc.close()
            
            logger.info(f"Split PDF into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting PDF {pdf_path}: {e}")
            raise
    
    def cleanup_temp_files(self, chunk_paths: List[str]) -> None:
        """
        Clean up temporary chunk files
        
        Args:
            chunk_paths: List of temporary file paths to clean up
        """
        try:
            for chunk_path in chunk_paths:
                temp_file = Path(chunk_path)
                if temp_file.exists():
                    temp_file.unlink()
                    logger.debug(f"Cleaned up temp file: {chunk_path}")
            
            logger.info(f"Cleaned up {len(chunk_paths)} temporary chunk files")
            
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Get basic information about the PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with PDF information
        """
        try:
            doc = fitz.open(pdf_path)
            info = {
                "total_pages": len(doc),
                "title": doc.metadata.get("title", "Unknown"),
                "author": doc.metadata.get("author", "Unknown"),
                "subject": doc.metadata.get("subject", ""),
                "estimated_chunks": (len(doc) + self.max_pages_per_chunk - 1) // self.max_pages_per_chunk
            }
            doc.close()
            
            logger.debug(f"PDF info for {pdf_path}: {info}")
            return info
            
        except Exception as e:
            logger.error(f"Error getting PDF info for {pdf_path}: {e}")
            raise

class PDFTextExtractor:
    """Extract text content from PDF for preprocessing analysis"""
    
    @staticmethod
    def get_text_sample(pdf_path: str, max_pages: int = RAGConstants.PDF_TEXT_SAMPLE_MAX_PAGES) -> str:
        """
        Extract text sample from first few pages for analysis
        
        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to sample (default: 2)
            
        Returns:
            Text content from sampled pages
        """
        try:
            doc = fitz.open(pdf_path)
            text_content = []
            
            pages_to_sample = min(max_pages, len(doc))
            
            for page_num in range(pages_to_sample):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    text_content.append(f"=== Page {page_num + 1} ===\n{text.strip()}")
            
            doc.close()
            
            sample_text = "\n\n".join(text_content)
            logger.debug(f"Extracted {len(sample_text)} characters from {pages_to_sample} pages")
            
            return sample_text
            
        except Exception as e:
            logger.error(f"Error extracting text sample from {pdf_path}: {e}")
            return ""
    
    @staticmethod
    def estimate_token_count(text: str) -> int:
        """
        Rough estimation of token count for text
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count (rough approximation: 1 token ≈ 4 characters)
        """
        # Rough estimation: 1 token ≈ 4 characters for English text
        return len(text) // RAGConstants.TOKEN_TO_CHAR_RATIO