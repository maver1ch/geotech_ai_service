#!/usr/bin/env python3
"""
Script to split all PDFs in the data directory
"""

import fitz  # PyMuPDF
from pathlib import Path

def split_pdf(pdf_path, pages_per_chunk=8):
    """Split a PDF into smaller parts"""
    try:
        # Open PDF
        doc = fitz.open(str(pdf_path))
        total_pages = len(doc)
        
        if total_pages <= pages_per_chunk:
            print(f"⏭️  {pdf_path.name}: Only {total_pages} pages, no need to split")
            doc.close()
            return []
        
        print(f"✂️  {pdf_path.name}: {total_pages} pages → split into {pages_per_chunk}-page chunks")
        
        # Create output directory
        output_dir = pdf_path.parent / f"{pdf_path.stem}_chunks"
        output_dir.mkdir(exist_ok=True)
        
        chunk_paths = []
        chunk_count = 0
        
        # Split into chunks
        for start_page in range(0, total_pages, pages_per_chunk):
            end_page = min(start_page + pages_per_chunk - 1, total_pages - 1)
            chunk_count += 1
            
            # Create new PDF for this chunk
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
            
            # Chunk filename
            chunk_name = f"{pdf_path.stem}_chunk_{chunk_count:02d}_pages_{start_page+1}-{end_page+1}.pdf"
            chunk_path = output_dir / chunk_name
            
            # Save chunk
            new_doc.save(str(chunk_path))
            new_doc.close()
            
            chunk_paths.append(chunk_path)
            print(f"   ✅ Chunk {chunk_count}: Pages {start_page+1}-{end_page+1}")
        
        doc.close()
        return chunk_paths
        
    except Exception as e:
        print(f"❌ Error splitting {pdf_path.name}: {e}")
        return []

def main():
    # Find all PDFs in data directory
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ Directory 'data' does not exist")
        return
    
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in data directory")
        return
    
    print(f"🔍 Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"   📄 {pdf.name}")
    
    print("\n" + "="*60)
    print("START SPLITTING PDFS")
    print("="*60)
    
    total_chunks = 0
    
    for pdf_file in pdf_files:
        chunks = split_pdf(pdf_file, pages_per_chunk=8)
        total_chunks += len(chunks)
        print()
    
    print("="*60)
    print(f"🎉 COMPLETE!")
    print(f"📊 Total {total_chunks} chunks created from {len(pdf_files)} PDF files")
    print("="*60)

if __name__ == "__main__":
    main()