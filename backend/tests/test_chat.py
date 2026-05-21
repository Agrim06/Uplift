import os
import sys
import asyncio
import pytest
from fastapi.testclient import TestClient

# Adjust path to import app correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.schemas.user_schema import UserProfile
from app.services.profile_extractor import ProfileExtractionEngine

client = TestClient(app)

def test_mock_llm_extract():
    engine = ProfileExtractionEngine()
    
    async def run_test():
        # Test case 1: complete input
        profile, missing = await engine.extract_profile("I am a 20-year-old engineering student from Karnataka with annual family income of 2 lakh.")
        assert profile.age == 20
        assert profile.state == "Karnataka"
        assert profile.occupation == "Student"
        assert profile.education == "Engineering"
        assert profile.income == 200000.0
        assert missing == []

        # Test case 2: partial input ("I am 20")
        profile, missing = await engine.extract_profile("I am 20")
        assert profile.age == 20
        assert profile.state is None
        assert set(missing) == {"state", "income", "occupation", "education"}

        # Test case 3: partial input ("Karnataka farmer income 1 lakh")
        profile, missing = await engine.extract_profile("Karnataka farmer income 1 lakh")
        assert profile.state == "Karnataka"
        assert profile.occupation == "Farmer"
        assert profile.income == 100000.0
        assert set(missing) == {"age", "education"}

    asyncio.run(run_test())

def test_profile_merge():
    engine = ProfileExtractionEngine()
    
    existing = UserProfile(
        state="Karnataka",
        occupation="Farmer",
        education="Class 10",
        income=100000.0
    )
    
    async def run_test():
        profile, missing = await engine.extract_profile("I am 20", existing_profile=existing)
        assert profile.age == 20
        assert profile.state == "Karnataka"
        assert profile.occupation == "Farmer"
        assert profile.education == "Class 10"
        assert profile.income == 100000.0
        assert missing == []

    asyncio.run(run_test())

def test_chat_api_endpoint():
    # Test chat API with missing fields
    payload = {
        "query": "I am 20"
    }
    response = client.post("/api/v1/chat/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["profile_summary"]["age"] == 20
    assert set(data["missing_info"]) == {"state", "income", "occupation", "education"}
    assert "To help me recommend exact schemes, could you please provide your:" in data["system_message"]
    
    # Test chat API with complete fields
    payload_complete = {
        "query": "I am 20-year-old engineering student from Karnataka with family income of 2 lakh"
    }
    response_complete = client.post("/api/v1/chat/", json=payload_complete)
    assert response_complete.status_code == 200
    data_complete = response_complete.json()
    assert data_complete["profile_summary"]["age"] == 20
    assert data_complete["profile_summary"]["state"] == "Karnataka"
    assert data_complete["profile_summary"]["occupation"] == "Student"
    assert data_complete["profile_summary"]["education"] == "Engineering"
    assert data_complete["profile_summary"]["income"] == 200000.0
    assert data_complete["missing_info"] == []
    assert "Thank you! I have all details. Evaluating eligible schemes for you now..." in data_complete["system_message"]

    # Test chat API with merge
    payload_merge = {
        "query": "I am 20",
        "existing_profile": {
            "state": "Karnataka",
            "occupation": "Farmer",
            "education": "Class 10",
            "income": 100000.0
        }
    }
    response_merge = client.post("/api/v1/chat/", json=payload_merge)
    assert response_merge.status_code == 200
    data_merge = response_merge.json()
    assert data_merge["profile_summary"]["age"] == 20
    assert data_merge["profile_summary"]["state"] == "Karnataka"
    assert data_merge["profile_summary"]["occupation"] == "Farmer"
    assert data_merge["profile_summary"]["education"] == "Class 10"
    assert data_merge["profile_summary"]["income"] == 100000.0
    assert data_merge["missing_info"] == []
