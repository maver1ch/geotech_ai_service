"""
Simple PDF to Markdown OCR Processor
Sử dụng Google GenAI multimodal LLM để chuyển đổi PDF thành Markdown
"""

import logging
import asyncio
import aiofiles
from pathlib import Path
from typing import Optional

from app.core.config.settings import get_settings

logger = logging.getLogger(__name__)

OCR_SYSTEM_PROMPT = """# Chuyên Gia Chuyển Đổi Nội Dung File sang Markdown (FileToMD-Bot)

## I. Danh Tính và Nhiệm Vụ Cốt Lõi

Bạn là **FileToMD-Bot**, một trợ lý AI chuyên biệt cao cấp. Nhiệm vụ duy nhất và tối quan trọng của bạn là tiếp nhận một khối văn bản lớn – **đại diện cho TOÀN BỘ NỘI DUNG của một file** – và chuyển đổi nó **MỘT CÁCH TỈ MỈ VÀ CHÍNH XÁC** sang định dạng Markdown **TUÂN THỦ CHUẨN MỰC, CÓ CẤU TRÚC TỐT và DỄ ĐỌC**.

Hãy hình dung người dùng đã "đưa" cho bạn một file, và bạn đang đọc toàn bộ nội dung của nó để thực hiện chuyển đổi.

Mục tiêu của bạn là tạo ra tài liệu Markdown:
1. **Bảo toàn 100% nội dung gốc** từ file (văn bản, ý nghĩa, thứ tự).
2. **Sử dụng cú pháp Markdown chuẩn**, ưu tiên **GitHub Flavored Markdown (GFM)**.
3. **Tối đa hóa khả năng đọc** cả ở dạng mã nguồn Markdown và khi được hiển thị.
4. **Tuyệt đối tránh sử dụng HTML nội tuyến** trừ khi không có giải pháp Markdown tương đương.
5. **Bỏ qua những hình ảnh minh hoạ trong file PDF đó, không OCR**

## II. Quy Trình Xử Lý Đầu Vào và Đầu Ra

- **ĐẦU VÀO:** Bạn sẽ nhận được một file PDF chứa tài liệu kỹ thuật địa kỹ thuật.
- **ĐẦU RA:** **CHỈ VÀ CHỈ** trả về nội dung đã được chuyển đổi sang Markdown, **dưới dạng một khối văn bản thuần túy chứa mã Markdown.**
  - **KHÔNG** bao gồm bất kỳ lời chào, giải thích, bình luận, hay văn bản nào khác ngoài chính mã Markdown.
  - **KHÔNG** nói "Đây là bản Markdown của file:" hay bất cứ điều gì tương tự. Chỉ cần xuất ra mã Markdown.

## III. Đặc biệt quan trọng cho tài liệu địa kỹ thuật:
- Bảo toàn chính xác các công thức, phương trình
- Giữ nguyên cấu trúc bảng biểu, số liệu
- Đặc biệt chú ý đến các ký hiệu kỹ thuật (φ, γ, σ, etc.)
- Maintain proper heading hierarchy
"""


class PDFToMarkdownOCR:
    """Simple PDF to Markdown OCR processor using Google GenAI"""
    
    def __init__(self):
        self.settings = get_settings()
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google GenAI client"""
        try:
            from google import genai
            
            self.client = genai.Client(api_key=self.settings.GOOGLE_GENAI_API_KEY)
            logger.info("Google GenAI client initialized for OCR processing")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google GenAI client: {e}")
            raise
    
    async def convert_pdf_to_markdown(
        self, 
        pdf_path: str,
        output_dir: str = None
    ) -> str:
        """
        Convert PDF to Markdown using Google GenAI OCR
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save markdown file (optional)
            
        Returns:
            Path to generated markdown file
        """
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            logger.info(f"Starting OCR conversion: {pdf_path.name}")
            
            # Step 1: OCR PDF to Markdown using Google GenAI
            markdown_content = await self._ocr_pdf_to_markdown(str(pdf_path))
            
            if not markdown_content:
                raise ValueError("Failed to extract content from PDF")
            
            # Step 2: Save markdown file
            if output_dir is None:
                output_dir = pdf_path.parent
            
            output_path = await self._save_markdown_content(
                content=markdown_content,
                pdf_name=pdf_path.name,
                output_dir=output_dir
            )
            
            logger.info(f"OCR conversion completed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error in PDF to Markdown conversion: {e}")
            raise
    
    async def _ocr_pdf_to_markdown(self, pdf_path: str) -> str:
        """Use Google GenAI multimodal LLM to convert PDF to Markdown"""
        try:
            from google import genai
            from google.genai import types
            
            # Upload PDF file to Google GenAI
            uploaded_file = self.client.files.upload(file=pdf_path)
            
            # Generate markdown content using multimodal model
            for attempt in range(1, 4):  # Retry up to 3 times
                try:
                    if attempt > 1:
                        logger.info(f"Retry OCR attempt {attempt}")
                        
                    response = await asyncio.to_thread(
                        self.client.models.generate_content,
                        model=self.settings.GOOGLE_GENAI_MODEL_VISION,  # Use vision model
                        contents=[uploaded_file],
                        config=types.GenerateContentConfig(
                            system_instruction=OCR_SYSTEM_PROMPT,
                            max_output_tokens=65536,
                            temperature=0.1  # Low temperature for accuracy
                        )
                    )
                    
                    return response.text
                    
                except Exception as e:
                    logger.error(f"OCR attempt {attempt} failed: {e}")
                    if attempt == 3:
                        raise
                    await asyncio.sleep(attempt ** 2)  # Exponential backoff
                    
        except Exception as e:
            logger.error(f"Error in OCR PDF to markdown: {e}")
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