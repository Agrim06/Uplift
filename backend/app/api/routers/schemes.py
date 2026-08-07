import os
import json
from typing import List
from fastapi import APIRouter, Query, HTTPException
from app.schemas.scheme_schema import Scheme

router = APIRouter()

# Construct path to schemes.json relative to this file
SCHEMES_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "schemes.json")
)

def load_schemes_from_json() -> List[Scheme]:
    if not os.path.exists(SCHEMES_FILE_PATH):
        raise HTTPException(
            status_code=500,
            detail=f"Schemes database file not found at: {SCHEMES_FILE_PATH}"
        )
    try:
        with open(SCHEMES_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Scheme(**item) for item in data]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading schemes database: {str(e)}"
        )

@router.get("/", response_model=List[Scheme], summary="List all government schemes")
async def get_schemes(
    state: str = Query(None, description="Filter schemes by state (case-insensitive)"),
    search: str = Query(None, description="Search keyword in scheme title, description, category, state, etc."),
    limit: int = Query(100, description="Maximum number of schemes to return")
):
    schemes = load_schemes_from_json()
    
    if state:
        # Filter by state (case-insensitive)
        # Central schemes apply nationally and are returned for any state filter.
        state_lower = state.lower()
        schemes = [
            s for s in schemes 
            if s.state.lower() == "central" or s.state.lower() == state_lower
        ]
        
    if search and search.strip():
        q = search.strip().lower()
        filtered = []
        for s in schemes:
            cat_str = " ".join(s.category).lower() if isinstance(s.category, list) else str(s.category).lower()
            text_blob = f"{s.name} {s.description} {s.scheme_type} {s.target_group} {s.state} {s.occupation} {s.education_requirement} {s.benefits} {cat_str}".lower()
            if q in text_blob:
                filtered.append(s)
        schemes = filtered

    return schemes[:limit]

@router.get("/{scheme_id}", response_model=Scheme, summary="Get Specific scheme details")
async def get_scheme_by_id(scheme_id: str):
    schemes = load_schemes_from_json()
    for s in schemes:
        if s.id.lower() == scheme_id.lower():
            return s
    raise HTTPException(status_code=404, detail=f"Scheme with ID '{scheme_id}' not found.")

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