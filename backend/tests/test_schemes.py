import os
import json
import pytest
from fastapi.testclient import TestClient

# Adjust path to import app correctly
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.schemas.scheme_schema import Scheme

client = TestClient(app)

def test_json_schema_validation():
    # Construct path to schemes.json relative to this test file
    json_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "schemes.json")
    )
    assert os.path.exists(json_path), f"schemes.json not found at {json_path}"
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert isinstance(data, list)
    assert len(data) >= 5, "Dataset must have at least 5-10 schemes"
    
    # Verify each scheme parses correctly into the updated Pydantic Scheme model
    for item in data:
        try:
            scheme = Scheme(**item)
            assert scheme.id is not None
            assert scheme.name is not None
            assert scheme.description is not None
            assert len(scheme.eligibility_rules) > 0
        except Exception as e:
            pytest.fail(f"Scheme validation failed for ID '{item.get('id')}': {str(e)}")

def test_get_schemes_api():
    response = client.get("/api/v1/schemes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_schemes_filtering():
    # Filter by Karnataka
    response = client.get("/api/v1/schemes/?state=Karnataka")
    assert response.status_code == 200
    karnataka_schemes = response.json()
    for s in karnataka_schemes:
        assert s["state"].lower() in ["karnataka", "central"]

    # Filter by a state with no specific schemes (should return only Central schemes)
    response = client.get("/api/v1/schemes/?state=Kerala")
    assert response.status_code == 200
    kerala_schemes = response.json()
    for s in kerala_schemes:
        assert s["state"].lower() == "central"

def test_get_scheme_by_id():
    # Get all schemes first
    response = client.get("/api/v1/schemes/")
    assert response.status_code == 200
    all_schemes = response.json()
    first_id = all_schemes[0]["id"]
    
    # Get by specific ID
    response_by_id = client.get(f"/api/v1/schemes/{first_id}")
    assert response_by_id.status_code == 200
    assert response_by_id.json()["id"] == first_id

    # Non-existent ID
    response_not_found = client.get("/api/v1/schemes/SCH-NON-EXISTENT")
    assert response_not_found.status_code == 404
