import os
import sys
import pytest

# Adjust path to import app correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.user_schema import UserProfile
from app.agents.reflection_agent import ReflectionAgent

def test_detect_conflicts():
    # Negative age and income
    p1 = UserProfile(age=-5, income=-100)
    conflicts = ReflectionAgent.detect_conflicts(p1)
    assert "Age cannot be negative." in conflicts
    assert "Income cannot be negative." in conflicts

    # Age vs Education inconsistency (too young for college/engineering)
    p2 = UserProfile(age=10, education="Engineering Degree")
    conflicts = ReflectionAgent.detect_conflicts(p2)
    assert any("education is 'Engineering Degree'" in c for c in conflicts)

    # Age vs Occupation inconsistency (too young to be retired/officer)
    p3 = UserProfile(age=8, occupation="Retired")
    conflicts = ReflectionAgent.detect_conflicts(p3)
    assert any("occupation is 'Retired'" in c for c in conflicts)

    # Consistent profile
    p4 = UserProfile(age=20, education="Engineering", occupation="Student", income=10000.0)
    assert len(ReflectionAgent.detect_conflicts(p4)) == 0

def test_evaluate_confidence():
    # Short query is low confidence (len < 8)
    assert ReflectionAgent.evaluate_confidence("I am 20", UserProfile(age=20)) is True
    assert ReflectionAgent.evaluate_confidence("Hi", UserProfile()) is True

    # Longer query with zero extracted parameters is low confidence
    p_empty = UserProfile()
    assert ReflectionAgent.evaluate_confidence("hello checking government help system", p_empty) is True

    # Longer query with some extracted parameter is high confidence
    p_extracted = UserProfile(age=20, state="Karnataka")
    assert ReflectionAgent.evaluate_confidence("I am 20 year old student from Karnataka", p_extracted) is False

def test_reflect_logic():
    p = UserProfile(age=20, state="Karnataka") # missing income, education, occupation
    missing = ["income", "education", "occupation"]
    
    result = ReflectionAgent.reflect(
        query="I am 20 year old student from Karnataka",
        profile=p,
        eligible_schemes=[],
        missing_info=missing
    )
    
    assert result["need_more_info"] is True
    assert result["missing"] == missing
    assert result["low_confidence"] is False
    assert result["conflicts"] == []
    assert "Missing attributes:" in result["reasoning"]
