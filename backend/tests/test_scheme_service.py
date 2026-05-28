import os
import sys
import pytest

# Adjust path to import app correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.user_schema import UserProfile
from app.services.scheme_service import SchemeRetrievalService
from app.services.recommendation_service import RecommendationService

def test_scheme_retrieval_by_state():
    retrieval = SchemeRetrievalService()
    
    # Karnataka resident
    profile_kar = UserProfile(state="Karnataka")
    kar_candidates = retrieval.get_candidate_schemes(profile_kar)
    # Should include Central schemes + Karnataka schemes
    for scheme in kar_candidates:
        assert scheme.state.lower() in ["karnataka", "central"]
        
    # Delhi resident
    profile_delhi = UserProfile(state="Delhi")
    delhi_candidates = retrieval.get_candidate_schemes(profile_delhi)
    # Should ONLY include Central schemes (no Karnataka schemes)
    for scheme in delhi_candidates:
        assert scheme.state.lower() == "central"

def test_scheme_retrieval_by_income():
    retrieval = SchemeRetrievalService()
    
    # Low income (Rs. 1,00,000) - eligible for AICTE Pragati (limit 800k) and PwD (limit 250k)
    profile_low = UserProfile(income=100000.0)
    low_candidates = retrieval.get_candidate_schemes(profile_low)
    
    # High income (Rs. 9,00,000) - should filter out all schemes that have income limits <= 800k
    profile_high = UserProfile(income=900000.0)
    high_candidates = retrieval.get_candidate_schemes(profile_high)
    for scheme in high_candidates:
        if scheme.income_limit is not None:
            assert scheme.income_limit > 900000.0

def test_recommendation_and_ranking():
    recommendation_service = RecommendationService()
    
    # 20-year-old female engineering student from Karnataka, income 2 lakh
    # She matches:
    # 1. CSSS (Central, Student, income <= 4.5L, eligible) -> Eligible
    # 2. SSP SC (Karnataka, SC category - but category is General/None so category unknown) -> Unknown
    # 3. AICTE Pragati (Central, Student, Female, income <= 8L) -> Eligible
    # 4. SSP OBC (Karnataka, OBC category - category unknown) -> Unknown
    # Let's check matching and sorting order.
    profile = UserProfile(
        age=20,
        state="Karnataka",
        occupation="Student",
        education="Engineering",
        income=200000.0,
        gender="Female"
        # category is None -> unknown
    )
    
    recs = recommendation_service.get_recommendations(profile)
    
    assert len(recs) > 0
    
    # Check ranking: fully eligible (True) must come first, then unknown
    # Also verify that no ineligible (False) schemes are included
    last_status = True
    for rec in recs:
        status = rec["evaluation"].eligible
        assert status in [True, "unknown"]
        
        # Check ordering: if we transitioned to "unknown", we shouldn't see True again
        if last_status == "unknown":
            assert status == "unknown"
        last_status = status
