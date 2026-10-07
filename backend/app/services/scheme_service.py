import os
import json
import logging
from typing import List, Dict, Tuple, Optional
from app.schemas.user_schema import UserProfile
from app.schemas.scheme_schema import Scheme

logger = logging.getLogger(__name__)

SCHEMES_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "schemes.json")
)

# ── GLOBAL IN-MEMORY SCHEME CACHE ──────────────────────────────────────────
# Keeps all 172+ schemes resident in RAM to eliminate physical disk reads on HTTP GETs
_CACHE_SCHEMES: List[Scheme] = []
_CACHE_BY_ID: Dict[str, Scheme] = {}
_CACHE_SEARCH_INDEX: List[Tuple[Scheme, str]] = []

def reload_schemes_cache(filepath: str = SCHEMES_FILE_PATH) -> List[Scheme]:
    """
    Reads schemes.json from disk and updates in-memory RAM caches and lookup indexes.
    """
    global _CACHE_SCHEMES, _CACHE_BY_ID, _CACHE_SEARCH_INDEX
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Schemes database file not found at: {filepath}")
        
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    schemes = [Scheme(**item) for item in data]
    by_id = {s.id.lower(): s for s in schemes}
    
    # Pre-build lowercase search blobs once in memory to avoid string allocation per request
    search_index = []
    for s in schemes:
        cat_str = " ".join(s.category).lower() if isinstance(s.category, list) else str(s.category).lower()
        blob = f"{s.name} {s.description} {s.scheme_type} {s.target_group} {s.state} {s.occupation} {s.education_requirement} {s.benefits} {cat_str}".lower()
        search_index.append((s, blob))

    _CACHE_SCHEMES = schemes
    _CACHE_BY_ID = by_id
    _CACHE_SEARCH_INDEX = search_index
    logger.info(f"Loaded and cached {len(schemes)} schemes into RAM memory.")
    return _CACHE_SCHEMES

def get_all_schemes() -> List[Scheme]:
    """Returns the cached schemes in memory. Performs 0 disk I/O."""
    if not _CACHE_SCHEMES:
        return reload_schemes_cache()
    return _CACHE_SCHEMES

def get_cached_scheme_by_id(scheme_id: str) -> Optional[Scheme]:
    """O(1) in-memory scheme lookup by ID with 0 disk I/O."""
    if not _CACHE_BY_ID:
        reload_schemes_cache()
    return _CACHE_BY_ID.get(scheme_id.lower())

def search_cached_schemes(
    state: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100
) -> List[Scheme]:
    """
    In-memory filtering and search with pre-indexed search blobs. Zero disk I/O.
    """
    if not _CACHE_SEARCH_INDEX:
        reload_schemes_cache()

    results = []
    state_lower = state.lower() if state else None
    q = search.strip().lower() if search and search.strip() else None

    for scheme, blob in _CACHE_SEARCH_INDEX:
        # State filter
        if state_lower:
            s_state = scheme.state.lower()
            if s_state != "central" and s_state != state_lower:
                continue
                
        # Keyword search against pre-computed blob
        if q and q not in blob:
            continue
            
        results.append(scheme)
        if len(results) >= limit:
            break

    return results

class SchemeRetrievalService:
    def __init__(self, filepath: str = SCHEMES_FILE_PATH):
        self.filepath = filepath
    
    def _load_all_schemes(self) -> List[Scheme]:
        return get_all_schemes()
    
    def get_candidate_schemes(self, profile: UserProfile) -> List[Scheme]:
        all_schemes = self._load_all_schemes()
        candidates = []

        for scheme in all_schemes:
            if profile.state and scheme.state:
                if scheme.state.lower() != "central" and scheme.state.lower() != profile.state.lower():
                    continue
        
            if profile.occupation and scheme.occupation:
                if scheme.occupation.lower() != profile.occupation.lower():
                    continue
            
            if profile.income is not None and scheme.income_limit is not None:
                if profile.income > scheme.income_limit:
                    continue

            if profile.category and scheme.category:
                clean_categories = [c.lower() for c in scheme.category]
                if profile.category.lower() not in clean_categories:
                    continue
            candidates.append(scheme)
        return candidates