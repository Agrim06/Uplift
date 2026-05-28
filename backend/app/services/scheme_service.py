import os
import json
from typing import List, Optional
from app.schemas.user_schema import UserProfile
from app.schemas.scheme_schema import Scheme

SCHEMES_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "schemes.json")
)

class SchemeRetrievalService:
    def __init__(self, filepath: str = SCHEMES_FILE_PATH):
        self.filepath = filepath
        self._cache_schemes: Optional[List[Scheme]] = None
    
    def _load_all_schemes(self) -> List[Scheme]:
        if self._cache_schemes is not None:
            return self._cache_schemes
        
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Schemes database file not found at: {self.filepath}")
        
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            self._cache_schemes = [Scheme(**item) for item in data]
        
        return self._cache_schemes
    
    def get_candidate_schemes(self, profile: UserProfile) -> List[Scheme]:
        all_schemes = self._load_all_schemes()
        candidates = []

        for scheme in all_schemes:
            if profile.state and scheme.state:
                if scheme.state.lower() != "central" and scheme.state.lower() !=  profile.state.lower():
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