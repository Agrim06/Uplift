import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.workflows.langgraph_workflow import run_langgraph_workflow

@pytest.mark.anyio
async def test_run_langgraph_workflow_complete_profile():
    query = "I am a 20-year-old female engineering student from Karnataka with family income of 2 lakh."
    result = await run_langgraph_workflow(message=query, thread_id="test_wf_complete")
    
    assert "profile" in result
    assert result["profile"]["age"] == 20
    assert result["profile"]["state"] == "Karnataka"
    assert result["profile"]["occupation"] == "Student"
    assert result["profile"]["education"] == "Engineering"
    assert result["profile"]["income"] == 200000.0
    assert result["profile"]["gender"] == "Female"
    
    assert len(result["verified_schemes"]) > 0
    assert result["status"] == "success"
    assert len(result["response"]) > 0

@pytest.mark.anyio
async def test_run_langgraph_workflow_partial_profile():
    query = "I am 20"
    result = await run_langgraph_workflow(message=query, thread_id="test_wf_partial")
    
    assert "profile" in result
    assert result["profile"]["age"] == 20
    assert result["status"] == "clarification"
    
    # Missing fields should be identified
    assert "state" in result["missing_fields"]
    assert "income" in result["missing_fields"]
    assert "occupation" in result["missing_fields"]

@pytest.mark.anyio
async def test_run_langgraph_workflow_merge():
    query = "I am 20"
    existing = {
        "state": "Karnataka",
        "occupation": "Farmer",
        "education": "Class 10",
        "income": 100000.0
    }
    result = await run_langgraph_workflow(
        message=query, 
        existing_profile=existing,
        thread_id="test_wf_merge"
    )
    
    assert "profile" in result
    assert result["profile"]["age"] == 20
    assert result["profile"]["state"] == "Karnataka"
    assert result["profile"]["occupation"] == "Farmer"
    assert len(result["verified_schemes"]) > 0
