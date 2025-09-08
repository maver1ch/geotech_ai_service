"""
Enhanced PDF to Markdown OCR Processor
Using Google GenAI multimodal LLM with chunk-based processing to convert PDF to Markdown
"""

import logging
import asyncio
import aiofiles
from pathlib import Path
from typing import Optional, List, Dict, Any

from app.core.config.settings import get_settings
from app.core.config.constants import RAGConstants
from app.core.utils.pdf_splitter import PDFPageSplitter, PDFTextExtractor
from app.core.utils.markdown_assembler import MarkdownAssembler

logger = logging.getLogger(__name__)

# System prompts for different processing modes
OCR_CHUNK_SYSTEM_PROMPT = """# OCR Chunk Processor (ChunkOCR-Bot)

## I. Identity and Mission

You are **ChunkOCR-Bot**, a specialist in processing parts of PDF documents. Your mission is to convert **ONE SPECIFIC PART** of a document to Markdown with the highest accuracy.

## II. Chunk Processing Principles

1. **Accurately convert** the provided chunk content
2. **Completely preserve** structure, formatting, formulas
3. **DO NOT create** general document titles (to avoid duplication when merging)
4. **DO NOT add** explanations or comments
5. **Pay special attention** to technical symbols (φ, γ, σ, τ, etc.)

## III. Output
- **ONLY return** markdown content of this chunk
- **DO NOT** add metadata or chunk information
- **DO NOT** mention "this is part X of the document"
- If chunk starts in the middle of a section, start from available content
"""

OCR_FIRST_CHUNK_SYSTEM_PROMPT = """# OCR First Chunk Processor (FirstChunkOCR-Bot)

## I. Identity and Mission

You are **FirstChunkOCR-Bot**, specialized in processing the first part of PDF documents. You are responsible for creating complete opening section with main title and table of contents.

## II. Special Tasks for First Chunk

1. **Create main title** of the document (H1)
2. **Create Table of Contents** if present in this chunk
3. **Accurately convert** all content in the chunk
4. **Establish structure** markdown foundation for the entire document

## III. Output
- Complete markdown content for first chunk
- Include main title and initial structure
- Pay special attention to technical symbols (φ, γ, σ, τ, etc.)
"""


class PDFToMarkdownOCR:
    """Enhanced PDF to Markdown OCR processor with chunk-based processing"""
    
    def __init__(self, max_pages_per_chunk: int = RAGConstants.MAX_PAGES_PER_CHUNK):
        """
        Initialize OCR processor with chunking support
        
        Args:
            max_pages_per_chunk: Maximum pages per processing chunk (default: 5)
        """
        self.settings = get_settings()
        self.max_pages_per_chunk = max_pages_per_chunk
        self.pdf_splitter = PDFPageSplitter(max_pages_per_chunk)
        self.markdown_assembler = MarkdownAssembler()
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google GenAI client"""
        try:
            from google import genai
            
            self.client = genai.Client(api_key=self.settings.GOOGLE_GENAI_API_KEY)
            logger.info("Google GenAI client initialized for chunked OCR processing")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google GenAI client: {e}")
            raise
    
    async def convert_pdf_to_markdown(
        self, 
        pdf_path: str,
        output_dir: str = None,
        use_chunking: bool = None
    ) -> str:
        """
        Convert PDF to Markdown using chunked processing approach
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save markdown file (optional)
            use_chunking: Force chunking on/off, auto-detect if None
            
        Returns:
            Path to generated markdown file
        """
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            logger.info(f"Starting enhanced OCR conversion: {pdf_path.name}")
            
            # Step 1: Analyze PDF to determine processing strategy
            pdf_info = self.pdf_splitter.get_pdf_info(str(pdf_path))
            should_chunk = self._should_use_chunking(pdf_info, use_chunking)
            
            logger.info(f"PDF Info: {pdf_info['total_pages']} pages, chunking: {should_chunk}")
            
            if should_chunk:
                # Step 2a: Chunked processing for large PDFs
                markdown_content = await self._ocr_pdf_with_chunks(str(pdf_path), pdf_info)
            else:
                # Step 2b: Single-pass processing for small PDFs
                markdown_content = await self._ocr_pdf_single_pass(str(pdf_path))
            
            if not markdown_content:
                raise ValueError("Failed to extract content from PDF")
            
            # Step 3: Save markdown file
            if output_dir is None:
                output_dir = pdf_path.parent
            
            output_path = await self._save_markdown_content(
                content=markdown_content,
                pdf_name=pdf_path.name,
                output_dir=output_dir
            )
            
            logger.info(f"Enhanced OCR conversion completed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error in enhanced PDF to Markdown conversion: {e}")
            raise
    
    def _should_use_chunking(self, pdf_info: dict, force_chunking: bool = None) -> bool:
        """
        Determine if chunking should be used based on PDF characteristics
        
        Args:
            pdf_info: PDF information dictionary
            force_chunking: Override automatic decision
            
        Returns:
            True if chunking should be used
        """
        if force_chunking is not None:
            return force_chunking
        
        # Use chunking for PDFs with more pages than threshold
        # This is a conservative threshold to avoid token limits
        return pdf_info.get("total_pages", 0) > RAGConstants.CHUNKING_PAGE_THRESHOLD
    
    async def _ocr_pdf_with_chunks(self, pdf_path: str, pdf_info: dict) -> str:
        """Process PDF using chunk-based approach for large documents"""
        try:
            logger.info(f"Starting chunked OCR processing for {pdf_info['total_pages']} pages")
            
            # Step 1: Split PDF into chunks
            chunks = self.pdf_splitter.split_pdf_to_chunks(pdf_path)
            logger.info(f"Split PDF into {len(chunks)} chunks")
            
            # Step 2: Process each chunk
            processed_chunks = []
            
            for i, (chunk_path, start_page, end_page) in enumerate(chunks):
                try:
                    logger.info(f"Processing chunk {i+1}/{len(chunks)}: pages {start_page}-{end_page}")
                    
                    # Determine if this is the first chunk (needs title and TOC)
                    is_first_chunk = (i == 0)
                    
                    # OCR the chunk
                    chunk_content = await self._ocr_single_chunk(
                        chunk_path, 
                        is_first_chunk=is_first_chunk
                    )
                    
                    if chunk_content:
                        processed_chunks.append({
                            'content': chunk_content,
                            'start_page': start_page,
                            'end_page': end_page,
                            'chunk_index': i,
                            'is_first_chunk': is_first_chunk
                        })
                        logger.info(f"✅ Successfully processed chunk {i+1}")
                    else:
                        logger.warning(f"⚠️ Empty content from chunk {i+1}")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to process chunk {i+1}: {e}")
                    # Continue with other chunks instead of failing completely
                    continue
            
            # Step 3: Clean up temporary files
            chunk_paths = [chunk[0] for chunk in chunks]
            self.pdf_splitter.cleanup_temp_files(chunk_paths)
            
            if not processed_chunks:
                raise ValueError("No chunks were successfully processed")
            
            # Step 4: Assemble chunks into final document
            pdf_name = Path(pdf_path).stem
            final_content = self.markdown_assembler.assemble_chunks(
                processed_chunks,
                document_title=pdf_info.get('title', pdf_name)
            )
            
            logger.info(f"Chunked OCR processing completed: {len(processed_chunks)} chunks assembled")
            return final_content
            
        except Exception as e:
            logger.error(f"Error in chunked OCR processing: {e}")
            raise
    
    async def _ocr_pdf_single_pass(self, pdf_path: str) -> str:
        """Process small PDF in single pass (legacy method for small files)"""
        try:
            logger.info("Using single-pass OCR processing")
            
            from google import genai
            from google.genai import types
            
            # Upload PDF file to Google GenAI
            uploaded_file = self.client.files.upload(file=pdf_path)
            
            # Generate markdown content using multimodal model
            for attempt in range(1, RAGConstants.OCR_MAX_RETRIES + 1):
                try:
                    if attempt > 1:
                        logger.info(f"Retry OCR attempt {attempt}")
                        
                    response = await asyncio.to_thread(
                        self.client.models.generate_content,
                        model=self.settings.GOOGLE_GENAI_MODEL_VISION,
                        contents=[uploaded_file],
                        config=types.GenerateContentConfig(
                            system_instruction=OCR_FIRST_CHUNK_SYSTEM_PROMPT,  # Use first chunk prompt for complete processing
                            max_output_tokens=RAGConstants.OCR_MAX_OUTPUT_TOKENS,
                            temperature=RAGConstants.OCR_TEMPERATURE
                        )
                    )
                    
                    return response.text
                    
                except Exception as e:
                    logger.error(f"Single-pass OCR attempt {attempt} failed: {e}")
                    if attempt == RAGConstants.OCR_MAX_RETRIES:
                        raise
                    await asyncio.sleep(attempt ** 2)
                    
        except Exception as e:
            logger.error(f"Error in single-pass OCR: {e}")
            raise
    
    async def _ocr_single_chunk(self, chunk_path: str, is_first_chunk: bool = False) -> str:
        """OCR a single chunk file"""
        try:
            from google import genai
            from google.genai import types
            
            # Select appropriate system prompt
            system_prompt = OCR_FIRST_CHUNK_SYSTEM_PROMPT if is_first_chunk else OCR_CHUNK_SYSTEM_PROMPT
            
            # Upload chunk file
            uploaded_file = self.client.files.upload(file=chunk_path)
            
            # Process with retry logic
            for attempt in range(1, RAGConstants.OCR_MAX_RETRIES + 1):
                try:
                    if attempt > 1:
                        logger.debug(f"Retry chunk OCR attempt {attempt}")
                        
                    response = await asyncio.to_thread(
                        self.client.models.generate_content,
                        model=self.settings.GOOGLE_GENAI_MODEL_VISION,
                        contents=[uploaded_file],
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            max_output_tokens=RAGConstants.OCR_MAX_OUTPUT_TOKENS,
                            temperature=RAGConstants.OCR_TEMPERATURE
                        )
                    )
                    
                    return response.text
                    
                except Exception as e:
                    logger.error(f"Chunk OCR attempt {attempt} failed: {e}")
                    if attempt == RAGConstants.OCR_MAX_RETRIES:
                        raise
                    await asyncio.sleep(attempt ** 2)
                    
        except Exception as e:
            logger.error(f"Error processing chunk {chunk_path}: {e}")
            raise
    
    async def _save_markdown_content(
        self, 
        content: str, 
        pdf_name: str, 
        output_dir: str
    ) -> str:
        """Save markdown content to file"""
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate markdown filename
            md_filename = f"{Path(pdf_name).stem}.md"
            md_path = output_dir / md_filename
            
            # Save content
            async with aiofiles.open(md_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            return str(md_path)
            
        except Exception as e:
            logger.error(f"Error saving markdown content: {e}")
            raise