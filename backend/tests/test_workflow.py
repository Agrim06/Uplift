import os
import sys
import pytest

# Adjust path to import app correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.user_schema import UserProfile
from app.workflows.agent_workflow import run_workflow

@pytest.mark.anyio
async def test_run_workflow_complete_profile():
    # 20-year-old female engineering student from Karnataka, income 2 lakh
    # She should match CSSS and AICTE Pragati (Fully Eligible)
    query = "I am a 20-year-old female engineering student from Karnataka with family income of 2 lakh."
    result = await run_workflow(query=query)
    
    assert "profile" in result
    assert result["profile"]["age"] == 20
    assert result["profile"]["state"] == "Karnataka"
    assert result["profile"]["occupation"] == "Student"
    assert result["profile"]["education"] == "Engineering"
    assert result["profile"]["income"] == 200000.0
    assert result["profile"]["gender"] == "Female"
    
    assert len(result["eligible_schemes"]) > 0
    # Pragati and PwD are eligible
    eligible_ids = [s["id"] for s in result["eligible_schemes"]]
    assert "SCH-CENTRAL-PRAGATI" in eligible_ids
    assert "SCH-CENTRAL-PWD" in eligible_ids
    
    # Documents should be aggregated and de-duplicated
    assert len(result["documents"]) > 0
    assert "Income Certificate" in result["documents"]
    assert "Disability Certificate (minimum 40% disability)" in result["documents"]

@pytest.mark.anyio
async def test_run_workflow_partial_profile():
    # Only "I am 20" is provided. Other mandatory fields (state, income, occupation, education) are missing.
    query = "I am 20"
    result = await run_workflow(query=query)
    
    assert "profile" in result
    assert result["profile"]["age"] == 20
    assert result["eligible_schemes"] == []
    
    # Missing fields should be aggregated
    assert "state" in result["missing_info"]
    assert "income" in result["missing_info"]
    assert "occupation" in result["missing_info"]
    assert "education" in result["missing_info"]

@pytest.mark.anyio
async def test_run_workflow_error_fallback():
    # Trigger error handling by passing an invalid query parameter type (e.g., None)
    # which should raise an exception during profile extraction stage.
    result = await run_workflow(query=None)
    
    assert "profile" in result
    assert result["eligible_schemes"] == []
    assert result["missing_info"] == []
    assert "error" in result
    assert "Workflow failed" in result["error"]
