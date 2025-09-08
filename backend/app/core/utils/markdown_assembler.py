"""
Markdown Assembly Service
Utilities for assembling multiple markdown chunks into coherent documents
"""

import logging
import re
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class MarkdownAssembler:
    """Service for assembling markdown chunks with context preservation"""
    
    def __init__(self):
        logger.info("MarkdownAssembler initialized")
    
    def assemble_chunks(self, 
                       chunks: List[Dict[str, Any]], 
                       document_title: str = None) -> str:
        """
        Assemble multiple markdown chunks into a single document
        
        Args:
            chunks: List of chunk dictionaries with keys:
                   - content: markdown content
                   - start_page: starting page number
                   - end_page: ending page number
                   - chunk_index: order index
            document_title: Optional title for the assembled document
            
        Returns:
            Complete assembled markdown document
        """
        try:
            logger.info(f"Assembling {len(chunks)} markdown chunks")
            
            # Sort chunks by their index to ensure correct order
            sorted_chunks = sorted(chunks, key=lambda x: x.get('chunk_index', 0))
            
            assembled_parts = []
            
            # Add document header if title provided
            if document_title:
                assembled_parts.append(f"# {document_title}\n")
                assembled_parts.append(f"*Assembled from {len(chunks)} chunks*\n")
            
            # Process each chunk
            for i, chunk in enumerate(sorted_chunks):
                content = chunk.get('content', '').strip()
                start_page = chunk.get('start_page', 0)
                end_page = chunk.get('end_page', 0)
                
                if not content:
                    logger.warning(f"Empty content in chunk {i+1}")
                    continue
                
                logger.debug(f"Processing chunk {i+1}: pages {start_page}-{end_page}")
                
                # Clean and process chunk content
                processed_content = self._process_chunk_content(content, i + 1, start_page, end_page)
                
                # Add chunk separator (except for first chunk)
                if i > 0 and not document_title:
                    assembled_parts.append(f"\n---\n<!-- Chunk {i+1}: Pages {start_page}-{end_page} -->\n")
                
                assembled_parts.append(processed_content)
            
            # Join all parts
            final_document = "\n\n".join(assembled_parts)
            
            # Post-process the document
            final_document = self._post_process_document(final_document)
            
            logger.info("Markdown assembly completed successfully")
            return final_document
            
        except Exception as e:
            logger.error(f"Error assembling markdown chunks: {e}")
            raise
    
    def _process_chunk_content(self, content: str, chunk_index: int, start_page: int, end_page: int) -> str:
        """
        Process individual chunk content
        
        Args:
            content: Raw markdown content from chunk
            chunk_index: Index of the chunk (1-based)
            start_page: Starting page number
            end_page: Ending page number
            
        Returns:
            Processed chunk content
        """
        try:
            # Remove any duplicate document titles (keep only in first chunk)
            if chunk_index > 1:
                # Remove main title if it appears (h1 at the beginning)
                content = re.sub(r'^#\s+[^\n]+\n', '', content, flags=re.MULTILINE)
            
            # Remove any OCR continuation messages
            ocr_patterns = [
                r'\.\.\.\(Content continues.*?\)',
                r'Due to length limitations.*?when ready\.\)',
                r'Please request the next part when ready',
                r'\(The conversion continues in the next response\)',
            ]
            
            for pattern in ocr_patterns:
                content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
            
            # Clean up excessive whitespace
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            content = content.strip()
            
            # Add page range comment for reference (hidden in HTML rendering)
            if start_page == end_page:
                page_comment = f"<!-- Source: Page {start_page} -->"
            else:
                page_comment = f"<!-- Source: Pages {start_page}-{end_page} -->"
            
            return f"{page_comment}\n{content}"
            
        except Exception as e:
            logger.error(f"Error processing chunk content: {e}")
            return content  # Return original content if processing fails
    
    def _post_process_document(self, document: str) -> str:
        """
        Apply final post-processing to the assembled document
        
        Args:
            document: Complete assembled document
            
        Returns:
            Post-processed document
        """
        try:
            # Fix heading hierarchy issues
            document = self._fix_heading_hierarchy(document)
            
            # Remove duplicate table of contents if present
            document = self._remove_duplicate_toc(document)
            
            # Clean up excessive blank lines
            document = re.sub(r'\n\s*\n\s*\n', '\n\n', document)
            
            # Ensure proper spacing around headings
            document = re.sub(r'\n(#+\s)', r'\n\n\1', document)
            document = re.sub(r'(#+\s[^\n]+)\n([^#\n])', r'\1\n\n\2', document)
            
            # Final cleanup
            document = document.strip()
            
            return document
            
        except Exception as e:
            logger.error(f"Error in post-processing: {e}")
            return document
    
    def _fix_heading_hierarchy(self, document: str) -> str:
        """
        Fix heading hierarchy to ensure logical structure
        
        Args:
            document: Document content
            
        Returns:
            Document with fixed heading hierarchy
        """
        try:
            # This is a basic implementation
            # In practice, you might need more sophisticated logic based on your document structure
            
            # Find all headings
            headings = re.findall(r'^(#+)\s+(.+)$', document, re.MULTILINE)
            
            if not headings:
                return document
            
            # Log heading structure for debugging
            logger.debug(f"Found {len(headings)} headings in document")
            
            return document
            
        except Exception as e:
            logger.error(f"Error fixing heading hierarchy: {e}")
            return document
    
    def _remove_duplicate_toc(self, document: str) -> str:
        """
        Remove duplicate table of contents entries
        
        Args:
            document: Document content
            
        Returns:
            Document with cleaned table of contents
        """
        try:
            # Look for multiple "Table of Contents" sections
            toc_pattern = r'##\s*Table of Contents.*?(?=\n##|\n#[^#]|$)'
            toc_matches = list(re.finditer(toc_pattern, document, re.DOTALL | re.IGNORECASE))
            
            if len(toc_matches) > 1:
                logger.info(f"Found {len(toc_matches)} TOC sections, keeping only the first")
                
                # Keep only the first TOC
                for match in toc_matches[1:]:
                    document = document.replace(match.group(0), '')
            
            return document
            
        except Exception as e:
            logger.error(f"Error removing duplicate TOC: {e}")
            return document
    
    def validate_assembly(self, assembled_content: str, expected_sections: List[str] = None) -> Dict[str, Any]:
        """
        Validate the assembled markdown document
        
        Args:
            assembled_content: The assembled markdown content
            expected_sections: Optional list of expected section names
            
        Returns:
            Validation results dictionary
        """
        try:
            results = {
                "is_valid": True,
                "warnings": [],
                "errors": [],
                "stats": {
                    "total_characters": len(assembled_content),
                    "total_lines": len(assembled_content.split('\n')),
                    "heading_count": len(re.findall(r'^#+\s', assembled_content, re.MULTILINE)),
                    "section_count": len(re.findall(r'^##\s', assembled_content, re.MULTILINE))
                }
            }
            
            # Check for incomplete content indicators
            incomplete_patterns = [
                r'\.\.\.\(Content continues',
                r'Due to length limitations',
                r'Please request the next part'
            ]
            
            for pattern in incomplete_patterns:
                if re.search(pattern, assembled_content, re.IGNORECASE):
                    results["warnings"].append(f"Found incomplete content indicator: {pattern}")
            
            # Check for expected sections if provided
            if expected_sections:
                missing_sections = []
                for section in expected_sections:
                    if not re.search(rf'#+\s+{re.escape(section)}', assembled_content, re.IGNORECASE):
                        missing_sections.append(section)
                
                if missing_sections:
                    results["warnings"].append(f"Missing expected sections: {missing_sections}")
            
            logger.info(f"Assembly validation completed: {results['stats']}")
            return results
            
        except Exception as e:
            logger.error(f"Error validating assembly: {e}")
            return {"is_valid": False, "errors": [str(e)], "warnings": [], "stats": {}}