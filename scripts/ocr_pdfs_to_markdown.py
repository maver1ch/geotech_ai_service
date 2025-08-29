#!/usr/bin/env python3
"""
Simple OCR Script: Convert PDF files to Markdown using Google GenAI
Chỉ làm một việc: PDF -> Markdown, không làm gì khác
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.loaders.pdf_to_markdown_ocr import PDFToMarkdownOCR
from app.core.config.settings import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

GEOTECH_PDFS = [
    "Settle3-CPT-Theory-Manual.pdf",
    "Settle3-Liquefaction-Theory-Manual.pdf", 
    "Settle3 Documentation _ Theory.pdf",
    "Settle3 Documentation _ Modelling.pdf",
    "Settle3 Documentation _ Settle3 FAQs.pdf"
]


class GeotechPDFOCRProcessor:
    """Simple OCR processor for geotech PDFs"""
    
    def __init__(self):
        self.settings = get_settings()
        self.ocr_processor = PDFToMarkdownOCR()
        self.data_dir = Path("data/knowledge_base")
        self.output_dir = self.data_dir / "markdown"
        
    async def ocr_all_pdfs(self):
        """OCR all geotech PDFs to markdown"""
        try:
            logger.info("Starting OCR conversion of all geotech PDFs...")
            
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            successful_conversions = []
            failed_conversions = []
            
            for pdf_name in GEOTECH_PDFS:
                pdf_path = self.data_dir / pdf_name
                
                if not pdf_path.exists():
                    logger.warning(f"PDF not found: {pdf_path}")
                    failed_conversions.append(pdf_name)
                    continue
                
                try:
                    logger.info(f"Converting: {pdf_name}")
                    
                    markdown_path = await self.ocr_processor.convert_pdf_to_markdown(
                        pdf_path=str(pdf_path),
                        output_dir=str(self.output_dir)
                    )
                    
                    successful_conversions.append({
                        "pdf": pdf_name,
                        "markdown": Path(markdown_path).name
                    })
                    
                    logger.info(f"✅ Successfully converted: {pdf_name}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to convert {pdf_name}: {e}")
                    failed_conversions.append(pdf_name)
                    continue
            
            # Print results
            self._print_results(successful_conversions, failed_conversions)
            
            return len(successful_conversions) > 0
            
        except Exception as e:
            logger.error(f"Error in OCR processing: {e}")
            return False
    
    def _print_results(self, successful, failed):
        """Print conversion results"""
        print("\n" + "="*60)
        print("OCR CONVERSION RESULTS")
        print("="*60)
        
        print(f"\n✅ SUCCESSFUL CONVERSIONS ({len(successful)}):")
        for item in successful:
            print(f"  • {item['pdf']} → {item['markdown']}")
        
        if failed:
            print(f"\n❌ FAILED CONVERSIONS ({len(failed)}):")
            for pdf_name in failed:
                print(f"  • {pdf_name}")
        
        print(f"\nOutput directory: {self.output_dir}")
        print("="*60 + "\n")


async def main():
    """Main function"""
    processor = GeotechPDFOCRProcessor()
    
    print("🚀 Starting PDF to Markdown OCR Conversion")
    print("This will convert all geotech PDFs to Markdown format using Google GenAI")
    print("Make sure GOOGLE_GENAI_API_KEY is set in your environment\n")
    
    try:
        success = await processor.ocr_all_pdfs()
        
        if success:
            print("🎉 OCR Conversion completed!")
            print("Check the 'data/knowledge_base/markdown/' directory for results")
        else:
            print("💥 OCR Conversion failed!")
            print("Please check the logs for error details")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ OCR interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())