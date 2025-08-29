"""
Intelligent Markdown Reader with Header-based Chunking
Đọc và chia Markdown thành chunks dựa trên cấu trúc headers
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MarkdownChunk:
    """Represents a chunk of markdown content"""
    content: str
    header_level: int
    header_text: str
    start_line: int
    end_line: int
    word_count: int
    metadata: Dict[str, Any]
    
    def to_document(self) -> Dict[str, Any]:
        """Convert to document format for vector storage"""
        return {
            'content': self.content,
            'metadata': {
                'source': self.metadata.get('source'),
                'header_level': self.header_level,
                'header_text': self.header_text,
                'word_count': self.word_count,
                'parent_headers': self.metadata.get('parent_headers', [])
            }
        }

class MarkdownReader:
    """Intelligent Markdown reader with header-based chunking"""
    
    def __init__(
        self,
        min_chunk_size: int = 200,
        max_chunk_size: int = 1500,
        header_merge_threshold: int = 100
    ):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.header_merge_threshold = header_merge_threshold
        
    def read_markdown_file(self, file_path: str) -> List[MarkdownChunk]:
        """
        Read markdown file and return intelligent chunks
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            List of MarkdownChunk objects
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Markdown file not found: {file_path}")
            
            logger.info(f"Reading markdown file: {file_path.name}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse markdown into sections
            sections = self._parse_markdown_sections(content)
            
            # Convert to chunks with intelligent splitting
            chunks = self._create_intelligent_chunks(sections, file_path.name)
            
            logger.info(f"Created {len(chunks)} chunks from {file_path.name}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error reading markdown file: {e}")
            raise
    
    def _parse_markdown_sections(self, content: str) -> List[Dict[str, Any]]:
        """Parse markdown content into hierarchical sections with parent header tracking"""
        lines = content.split('\n')
        sections = []
        current_section = None
        header_stack = []  # Track parent headers for hierarchy
        
        for line_num, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Check for standard markdown headers (# ## ###)
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line_stripped)
            
            # Check for bold text headers (**text**)
            bold_header_match = re.match(r'^\*\*(.+?)\*\*\s*$', line_stripped)
            
            # Check for questions/numbered sections (1. 2. etc.)
            numbered_match = re.match(r'^\*\*(\d+\.\s*.+?)\*\*\s*$', line_stripped)
            
            if header_match:
                # Save previous section
                if current_section:
                    current_section['end_line'] = line_num - 1
                    current_section['content'] = self._build_section_content_with_hierarchy(
                        lines, current_section, header_stack
                    )
                    sections.append(current_section)
                
                # Start new section
                level = len(header_match.group(1))
                header_text = header_match.group(2).strip()
                
                # Update header stack - remove headers at same or deeper level
                header_stack = [h for h in header_stack if h['level'] < level]
                
                # Add current header to stack
                header_info = {
                    'level': level,
                    'text': header_text,
                    'line': line_num,
                    'raw_line': line
                }
                header_stack.append(header_info)
                
                current_section = {
                    'header_level': level,
                    'header_text': header_text,
                    'start_line': line_num,
                    'end_line': None,
                    'content': None,
                    'parent_headers': header_stack.copy()
                }
            elif numbered_match and len(numbered_match.group(1).strip()) > 3:
                # Save previous section
                if current_section:
                    current_section['end_line'] = line_num - 1
                    current_section['content'] = self._build_section_content_with_hierarchy(
                        lines, current_section, header_stack
                    )
                    sections.append(current_section)
                
                # Start new section for numbered questions
                header_text = numbered_match.group(1).strip()
                level = 3  # Treat as H3
                
                # Update header stack
                header_stack = [h for h in header_stack if h['level'] < level]
                header_info = {
                    'level': level,
                    'text': header_text,
                    'line': line_num,
                    'raw_line': line
                }
                header_stack.append(header_info)
                
                current_section = {
                    'header_level': level,
                    'header_text': header_text,
                    'start_line': line_num,
                    'end_line': None,
                    'content': None,
                    'parent_headers': header_stack.copy()
                }
            elif bold_header_match and len(bold_header_match.group(1).strip()) > 3:
                # Save previous section  
                if current_section:
                    current_section['end_line'] = line_num - 1
                    current_section['content'] = self._build_section_content_with_hierarchy(
                        lines, current_section, header_stack
                    )
                    sections.append(current_section)
                
                # Start new section for bold headers
                header_text = bold_header_match.group(1).strip()
                level = 2  # Treat as H2
                
                # Update header stack
                header_stack = [h for h in header_stack if h['level'] < level]
                header_info = {
                    'level': level,
                    'text': header_text,
                    'line': line_num,
                    'raw_line': line
                }
                header_stack.append(header_info)
                
                current_section = {
                    'header_level': level,
                    'header_text': header_text,
                    'start_line': line_num,
                    'end_line': None,
                    'content': None,
                    'parent_headers': header_stack.copy()
                }
        
        # Handle last section
        if current_section:
            current_section['end_line'] = len(lines) - 1
            current_section['content'] = self._build_section_content_with_hierarchy(
                lines, current_section, header_stack
            )
            sections.append(current_section)
        
        # Handle content without headers (intro content)
        if sections and sections[0]['start_line'] > 0:
            intro_content = '\n'.join(lines[:sections[0]['start_line']])
            if intro_content.strip():
                intro_section = {
                    'header_level': 0,
                    'header_text': 'Document Introduction',
                    'start_line': 0,
                    'end_line': sections[0]['start_line'] - 1,
                    'content': intro_content,
                    'parent_headers': []
                }
                sections.insert(0, intro_section)
        
        return sections
    
    def _build_section_content_with_hierarchy(
        self,
        lines: List[str],
        section: Dict[str, Any],
        header_stack: List[Dict[str, Any]]
    ) -> str:
        """Build section content with parent headers included"""
        # Get parent headers (exclude current section header)
        parent_headers = [h for h in header_stack if h['line'] < section['start_line']]
        
        # Build content with hierarchy
        content_parts = []
        
        # Add parent headers
        for header in parent_headers:
            content_parts.append(header['raw_line'])
        
        # Add current section content (including current header)
        section_content = '\n'.join(
            lines[section['start_line']:section['end_line'] + 1]
        )
        content_parts.append(section_content)
        
        return '\n'.join(content_parts)
    
    def _create_intelligent_chunks(
        self, 
        sections: List[Dict[str, Any]], 
        filename: str
    ) -> List[MarkdownChunk]:
        """Create intelligent chunks from sections"""
        chunks = []
        skip_next = False
        
        for i, section in enumerate(sections):
            # Skip if this section was already processed as part of merge
            if skip_next:
                skip_next = False
                continue
                
            content = section['content'].strip()
            if not content:
                continue
            
            word_count = len(content.split())
            
            # Create base metadata
            metadata = {
                'source': filename,
                'parent_headers': [h['text'] for h in section.get('parent_headers', []) if h['line'] < section['start_line']]
            }
            
            # Handle small sections - try to merge with next if possible
            if word_count < self.min_chunk_size and i < len(sections) - 1:
                next_section = sections[i + 1]
                next_content = next_section['content'].strip()
                if next_content:  # Only merge if next section has content
                    combined_content = content + '\n\n' + next_content
                    combined_word_count = len(combined_content.split())
                    
                    if combined_word_count <= self.max_chunk_size:
                        # Create merged chunk
                        chunk = MarkdownChunk(
                            content=combined_content,
                            header_level=section['header_level'],
                            header_text=f"{section['header_text']} + {next_section['header_text']}",
                            start_line=section['start_line'],
                            end_line=next_section['end_line'],
                            word_count=combined_word_count,
                            metadata=metadata
                        )
                        chunks.append(chunk)
                        skip_next = True  # Skip next section since it's already merged
                        continue
            
            # Handle large sections - split if necessary
            if word_count > self.max_chunk_size:
                sub_chunks = self._split_large_section(section, metadata)
                chunks.extend(sub_chunks)
            else:
                # Create single chunk
                chunk = MarkdownChunk(
                    content=content,
                    header_level=section['header_level'],
                    header_text=section['header_text'],
                    start_line=section['start_line'],
                    end_line=section['end_line'],
                    word_count=word_count,
                    metadata=metadata
                )
                chunks.append(chunk)
        
        return chunks
    
    def _split_large_section(
        self, 
        section: Dict[str, Any], 
        base_metadata: Dict[str, Any]
    ) -> List[MarkdownChunk]:
        """Split large sections into smaller chunks"""
        content = section['content']
        lines = content.split('\n')
        
        chunks = []
        current_chunk_lines = []
        current_word_count = 0
        
        for line in lines:
            line_word_count = len(line.split())
            
            # Check if adding this line would exceed max size
            if current_word_count + line_word_count > self.max_chunk_size and current_chunk_lines:
                # Create chunk from accumulated lines
                chunk_content = '\n'.join(current_chunk_lines)
                chunk = MarkdownChunk(
                    content=chunk_content,
                    header_level=section['header_level'],
                    header_text=f"{section['header_text']} (Part {len(chunks) + 1})",
                    start_line=section['start_line'],
                    end_line=section['end_line'],
                    word_count=current_word_count,
                    metadata=base_metadata
                )
                chunks.append(chunk)
                
                # Start new chunk
                current_chunk_lines = [line]
                current_word_count = line_word_count
            else:
                current_chunk_lines.append(line)
                current_word_count += line_word_count
        
        # Handle remaining lines
        if current_chunk_lines:
            chunk_content = '\n'.join(current_chunk_lines)
            chunk = MarkdownChunk(
                content=chunk_content,
                header_level=section['header_level'],
                header_text=f"{section['header_text']} (Part {len(chunks) + 1})",
                start_line=section['start_line'],
                end_line=section['end_line'],
                word_count=current_word_count,
                metadata=base_metadata
            )
            chunks.append(chunk)
        
        return chunks