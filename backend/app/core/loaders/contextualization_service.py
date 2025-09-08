"""
Simple Contextualization Service
Add simple context to markdown chunks without LLM
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass

from .markdown_reader import MarkdownChunk
from ..config.constants import RAGConstants

logger = logging.getLogger(__name__)

@dataclass
class ContextualizedChunk:
    """Represents a contextualized markdown chunk"""
    original_chunk: MarkdownChunk
    contextualized_content: str
    context_added: bool
    processing_time: float = 0.0
    
    def to_document(self) -> Dict[str, Any]:
        """Convert to document format for vector storage"""
        doc = self.original_chunk.to_document()
        
        # Use contextualized content if available
        doc['content'] = self.contextualized_content if self.context_added else self.original_chunk.content
        
        # Add contextualization metadata (only essential ones)
        doc['metadata'].update({
            'is_contextualized': self.context_added,
            'context_method': 'simple_injection' if self.context_added else 'none'
        })
        
        return doc

class ContextualizationService:
    """Simple contextualization service - add context metadata without using LLM"""
    
    def __init__(self, add_context_header: bool = True):
        self.add_context_header = add_context_header
        
    async def contextualize_chunks(
        self,
        chunks: List[MarkdownChunk],
        filename: str
    ) -> List[ContextualizedChunk]:
        """
        Simplified: Add context metadata and header to chunks
        
        Args:
            chunks: List of markdown chunks to process
            filename: Filename for logging
            
        Returns:
            List of contextualized chunks
        """
        logger.info(f"Starting simple contextualization for {len(chunks)} chunks from {filename}")
        
        contextualized_chunks = []
        
        for chunk in chunks:
            contextualized_chunk = self._contextualize_single_chunk(chunk, filename)
            contextualized_chunks.append(contextualized_chunk)
        
        success_count = sum(1 for c in contextualized_chunks if c.context_added)
        logger.info(f"Simple contextualization completed: {success_count}/{len(chunks)} chunks contextualized")
        
        return contextualized_chunks
    
    def _contextualize_single_chunk(
        self,
        chunk: MarkdownChunk,
        filename: str
    ) -> ContextualizedChunk:
        """Add simple context to a single chunk"""
        import time
        
        start_time = time.time()
        
        # Create context header with hierarchy
        document_name = filename.replace('.md', '').replace('_', ' ').title()
        
        if self.add_context_header and chunk.header_level > 0:
            # Build hierarchy context
            context_parts = [f"**Document: {document_name}**"]
            
            # Add parent headers if available
            parent_headers = chunk.metadata.get('parent_headers', [])
            if parent_headers:
                hierarchy_text = " > ".join(parent_headers)
                context_parts.append(f"**Context: {hierarchy_text}**")
            
            context_parts.append(f"**Current Section: {chunk.header_text}**")
            
            # Combine context header with content
            context_header = '\n'.join(context_parts) + '\n\n'
            contextualized_content = context_header + chunk.content
            context_added = True
        else:
            # Don't add context header, keep original content
            contextualized_content = chunk.content
            context_added = False
        
        processing_time = time.time() - start_time
        
        return ContextualizedChunk(
            original_chunk=chunk,
            contextualized_content=contextualized_content,
            context_added=context_added,
            processing_time=processing_time
        )
    
    def should_contextualize_chunk(self, chunk: MarkdownChunk) -> bool:
        """
        Determine if a chunk needs contextualization
        Skip very short chunks or chunks with specific patterns
        """
        
        if chunk.word_count < RAGConstants.MIN_CONTEXTUALIZATION_WORD_COUNT:
            return False
            
        # Skip chunks that are mostly code or tables  
        content_lower = chunk.content.lower()
        if (content_lower.count('```') >= RAGConstants.CODE_BLOCK_THRESHOLD or 
            content_lower.count('|') > RAGConstants.TABLE_PIPE_THRESHOLD):
            return False
            
        return True