import os
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from app.schemas.scheme_schema import Scheme
from app.services.scheme_service import (
    get_all_schemes,
    get_cached_scheme_by_id,
    search_cached_schemes,
    reload_schemes_cache
)

router = APIRouter()

def load_schemes_from_json() -> List[Scheme]:
    """Provides backwards-compatible interface returning in-memory cached schemes."""
    return get_all_schemes()

@router.get("/", response_model=List[Scheme], summary="List all government schemes")
async def get_schemes(
    state: str = Query(None, description="Filter schemes by state (case-insensitive)"),
    search: str = Query(None, description="Search keyword in scheme title, description, category, state, etc."),
    limit: int = Query(100, description="Maximum number of schemes to return")
):
    """
    Returns filtered schemes directly from RAM memory index. Zero disk I/O.
    """
    return search_cached_schemes(state=state, search=search, limit=limit)

@router.get("/{scheme_id}", response_model=Scheme, summary="Get Specific scheme details")
async def get_scheme_by_id(scheme_id: str):
    """
    O(1) in-memory scheme lookup. Zero disk I/O.
    """
    scheme = get_cached_scheme_by_id(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme with ID '{scheme_id}' not found.")
    return scheme

from pydantic import BaseModel

class ScrapeRequest(BaseModel):
    url: str

@router.post("/scrape", response_model=Scheme, summary="Web scrape and ingest scheme from URL")
async def scrape_scheme_endpoint(request: ScrapeRequest):
    try:
        from app.services.scheme_scraper import SchemeScraperService
        scheme = await SchemeScraperService.scrape_and_ingest(request.url)
        return scheme
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Web scraping failed: {str(e)}")

from fastapi import UploadFile, File

@router.post("/ingest-pdf", response_model=Scheme, summary="Ingest government scheme from uploaded PDF document")
async def ingest_pdf_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files (.pdf) are supported.")
    try:
        from app.services.pdf_ingestion_service import PDFIngestionService
        contents = await file.read()
        scheme = await PDFIngestionService.ingest_pdf_bytes(contents, filename=file.filename)
        return scheme
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF ingestion failed: {str(e)}")