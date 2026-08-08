import os
import sys
import json
import asyncio
import pypdf
from dotenv import load_dotenv

load_dotenv()

# Ensure app package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.pdf_ingestion_service import PDFIngestionService

async def ingest_large_pdf(pdf_path: str, chunk_size: int = 4):
    if not os.path.exists(pdf_path):
        print(f"[*] PDF file not found at: {pdf_path}")
        return

    reader = pypdf.PdfReader(pdf_path)
    total_pages = len(reader.pages)
    filename = os.path.basename(pdf_path)

    print(f"[*] Starting multi-page ingestion for: '{filename}' ({total_pages} total pages)")
    print(f"[*] Chunk window size: {chunk_size} pages per AI processing pass.\n")

    total_ingested_schemes = 0

    # Process in page chunks (skipping table of contents pages 1-12 or starting from page 13)
    start_page = 12 # Start where Ministry scheme details begin (page 13)
    
    for page_num in range(start_page, total_pages, chunk_size):
        end_page = min(page_num + chunk_size, total_pages)
        print(f"[*] Extracting Pages {page_num+1} to {end_page} of {total_pages}...")

        chunk_text = ""
        for p in range(page_num, end_page):
            text = reader.pages[p].extract_text()
            if text:
                chunk_text += f"\n--- PAGE {p+1} ---\n" + text

        if not chunk_text.strip():
            continue

        try:
            scheme_data = await PDFIngestionService.structure_scheme_from_pdf_text(chunk_text, filename=f"{filename}_pages_{page_num+1}_{end_page}")
            schemes = await SchemeScraperService.save_scheme_to_database(scheme_data)
            if isinstance(schemes, list):
                count = len(schemes)
                total_ingested_schemes += count
                print(f"[OK] Ingested {count} schemes from Pages {page_num+1}-{end_page}:")
                for s in schemes:
                    print(f"     - '{s.name}' (ID: {s.id})")
            else:
                total_ingested_schemes += 1
                print(f"[OK] Ingested scheme: '{schemes.name}' (ID: {schemes.id})")
        except Exception as e:
            print(f"[ERROR] Failed extracting Pages {page_num+1}-{end_page}: {str(e)}")

        # Small pause to respect Gemini API rate limits
        await asyncio.sleep(1.5)

    print(f"\n[*] Large PDF Ingestion Complete! Successfully extracted {total_ingested_schemes} schemes into database.")

if __name__ == "__main__":
    pdf_file_path = os.path.join(os.path.dirname(__file__), "pdf_schemes", "Schemes-Volume-1-English.pdf")
    asyncio.run(ingest_large_pdf(pdf_file_path, chunk_size=4))
