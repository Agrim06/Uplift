import os
import sys
import pytest

# Adjust path to import app correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.user_schema import UserProfile
from app.schemas.scheme_schema import Scheme, EligibilityRule
from app.services.recommendation_service import EligibilityEvaluator

def test_evaluator_all_pass():
    profile = UserProfile(
        age=20,
        state="Karnataka",
        occupation="Student",
        education="Engineering",
        income=200000.0,
        gender="Male",
        category="General"
    )
    
    scheme = Scheme(
        id="SCH-TEST-1",
        name="Test Scheme 1",
        description="A test scheme description",
        scheme_type="Scholarship",
        target_group="Students",
        education_requirement="Student",
        occupation="Student",
        state="Karnataka",
        category=["General"],
        benefits="Test benefit",
        eligibility_rules=[
            EligibilityRule(
                attribute="income",
                condition="lte",
                value=250000.0,
                description="Annual family income must not exceed Rs. 2,50,000."
            ),
            EligibilityRule(
                attribute="state",
                condition="equals",
                value="Karnataka",
                description="Must be a permanent resident of Karnataka."
            ),
            EligibilityRule(
                attribute="category",
                condition="in",
                value=["General", "OBC"],
                description="Must belong to General or OBC category."
            )
        ]
    )
    
    evaluation = EligibilityEvaluator.evaluate_scheme(profile, scheme)
    assert evaluation.eligible is True
    assert len(evaluation.reason) == 3
    assert evaluation.missing_requirements == []

def test_evaluator_fails_one():
    profile = UserProfile(
        age=20,
        state="Maharashtra",  # Fails state check
        occupation="Student",
        education="Engineering",
        income=200000.0,
        gender="Male",
        category="General"
    )
    
    scheme = Scheme(
        id="SCH-TEST-2",
        name="Test Scheme 2",
        description="A test scheme description",
        scheme_type="Scholarship",
        target_group="Students",
        education_requirement="Student",
        occupation="Student",
        state="Karnataka",
        category=["General"],
        benefits="Test benefit",
        eligibility_rules=[
            EligibilityRule(
                attribute="state",
                condition="equals",
                value="Karnataka",
                description="Must be a permanent resident of Karnataka."
            )
        ]
    )
    
    evaluation = EligibilityEvaluator.evaluate_scheme(profile, scheme)
    assert evaluation.eligible is False
    assert any("does not match" in r for r in evaluation.reason)
    assert evaluation.missing_requirements == []

def test_evaluator_missing_info_unknown():
    profile = UserProfile(
        age=20,
        state="Karnataka",
        occupation="Student",
        education="Engineering",
        income=None,  # Missing income
        gender="Male",
        category=None  # Missing category
    )
    
    scheme = Scheme(
        id="SCH-TEST-3",
        name="Test Scheme 3",
        description="A test scheme description",
        scheme_type="Scholarship",
        target_group="Students",
        education_requirement="Student",
        occupation="Student",
        state="Karnataka",
        category=["General"],
        benefits="Test benefit",
        eligibility_rules=[
            EligibilityRule(
                attribute="income",
                condition="lte",
                value=250000.0,
                description="Annual family income must not exceed Rs. 2,50,000."
            ),
            EligibilityRule(
                attribute="state",
                condition="equals",
                value="Karnataka",
                description="Must be a permanent resident of Karnataka."
            ),
            EligibilityRule(
                attribute="category",
                condition="in",
                value=["General", "OBC"],
                description="Must belong to General or OBC category."
            )
        ]
    )
    
    evaluation = EligibilityEvaluator.evaluate_scheme(profile, scheme)
    assert evaluation.eligible == "unknown"
    assert set(evaluation.missing_requirements) == {"income", "category"}
    assert len(evaluation.reason) == 1  # only state rule evaluated and passed
    assert "matches" in evaluation.reason[0]

def test_evaluator_fails_override_missing():
    # If one check fails and another is missing, it should be FALSE (ineligible), not UNKNOWN
    profile = UserProfile(
        age=20,
        state="Maharashtra",  # Fails state check
        occupation="Student",
        education="Engineering",
        income=None,  # Missing income
        gender="Male",
        category="General"
    )
    
    scheme = Scheme(
        id="SCH-TEST-4",
        name="Test Scheme 4",
        description="A test scheme description",
        scheme_type="Scholarship",
        target_group="Students",
        education_requirement="Student",
        occupation="Student",
        state="Karnataka",
        category=["General"],
        benefits="Test benefit",
        eligibility_rules=[
            EligibilityRule(
                attribute="income",
                condition="lte",
                value=250000.0,
                description="Annual family income must not exceed Rs. 2,50,000."
            ),
            EligibilityRule(
                attribute="state",
                condition="equals",
                value="Karnataka",
                description="Must be a permanent resident of Karnataka."
            )
        ]
    )
    
    evaluation = EligibilityEvaluator.evaluate_scheme(profile, scheme)
    assert evaluation.eligible is False  # Failed state rule overrides missing income rule
    assert evaluation.missing_requirements == []
    assert any("does not match" in r for r in evaluation.reason)
