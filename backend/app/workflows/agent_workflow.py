import logging
from typing import List, Dict, Any, Optional
from app.schemas.user_schema import UserProfile
from app.services.profile_extractor import ProfileExtractionEngine
from app.services.scheme_service import SchemeRetrievalService
from app.services.recommendation_service import EligibilityEvaluator

logger = logging.getLogger(__name__)

# Initialize engine services
extractor_engine = ProfileExtractionEngine()
retrieval_service = SchemeRetrievalService()

# ── WORKFLOW STAGES (LANGGRAPH COMPATIBLE NODES) ─────────────────────────────

async def extract_profile_step(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 1: Profile Extraction
    Extracts user details from query and merges them with any existing profile.
    """
    profile, missing_fields = await extractor_engine.extract_profile(
        query=state["query"],
        existing_profile=state["profile"]
    )
    return {
        "profile": profile,
        "missing_fields": missing_fields
    }

def retrieve_schemes_step(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 2: Scheme Retrieval
    Retrieves candidate schemes pre-filtered by state, occupation, income, category.
    """
    candidates = retrieval_service.get_candidate_schemes(state["profile"])
    return {
        "candidate_schemes": candidates
    }

def evaluate_eligibility_step(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 3: Eligibility Evaluation
    Evaluates eligibility for each candidate and collects missing fields.
    """
    profile = state["profile"]
    eligible_schemes = []
    missing_info_set = set()
    evaluations = {}

    for scheme in state["candidate_schemes"]:
        evaluation = EligibilityEvaluator.evaluate_scheme(profile, scheme)
        evaluations[scheme.id] = evaluation
        
        if evaluation.eligible is True:
            eligible_schemes.append(scheme)
        elif evaluation.eligible == "unknown":
            missing_info_set.update(evaluation.missing_requirements)

    return {
        "eligible_schemes": eligible_schemes,
        "evaluations": evaluations,
        "missing_info": sorted(list(missing_info_set))
    }

def reflection_step(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 4: Reflection Step
    Performs consistency checks and compiles agent reasoning logs.
    """
    eligible_schemes = state["eligible_schemes"]
    missing_info = state["missing_info"]
    evaluations = state["evaluations"]
    reasons = []
    
    # Consistency Checks
    profile = state["profile"]
    if profile.age is not None and profile.age < 0:
        reasons.append("Logical Alert: User age is negative.")

    # Formulate Reasoning Scratchpad
    if eligible_schemes:
        reasons.append(f"Successfully matched {len(eligible_schemes)} eligible scheme(s).")
        for scheme in eligible_schemes:
            eval_details = evaluations[scheme.id]
            reasons.append(f"- {scheme.name}: {', '.join(eval_details.reason)}")
    else:
        reasons.append("No fully eligible schemes identified for this profile.")
        
    if missing_info:
        reasons.append(f"Potential schemes exist, but missing info: {', '.join(missing_info)}")

    return {
        "reasoning": "\n".join(reasons)
    }

def format_response_step(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 5: Response Formatting
    Extracts, de-duplicates documents and formats final output schema.
    """
    eligible_schemes = state["eligible_schemes"]
    
    # Extract and de-duplicate documents
    documents = set()
    for scheme in eligible_schemes:
        documents.update(scheme.required_documents)

    return {
        "profile": state["profile"].model_dump(),
        "eligible_schemes": [s.model_dump() for s in eligible_schemes],
        "missing_info": state["missing_info"],
        "documents": sorted(list(documents))
    }

# ── ORCHESTRATOR ─────────────────────────────────────────────────────────────

async def run_workflow(query: str, existing_profile: Optional[UserProfile] = None) -> Dict[str, Any]:
    """
    Sequences workflow nodes using basic function chaining.
    """
    # Initialize Master State
    state = {
        "query": query,
        "profile": existing_profile or UserProfile(),
        "missing_fields": [],
        "candidate_schemes": [],
        "eligible_schemes": [],
        "evaluations": {},
        "missing_info": [],
        "reasoning": "",
    }
    
    try:
        # 1. Profile Extraction
        state.update(await extract_profile_step(state))
        
        # 2. Scheme Retrieval
        state.update(retrieve_schemes_step(state))
        
        # 3. Eligibility Evaluation
        state.update(evaluate_eligibility_step(state))
        
        # 4. Reflection
        state.update(reflection_step(state))
        
        # 5. Format Response
        return format_response_step(state)
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
        # Error handling fallback response
        return {
            "profile": state["profile"].model_dump() if state.get("profile") else {},
            "eligible_schemes": [],
            "missing_info": [],
            "documents": [],
            "error": f"Workflow failed: {str(e)}"
        }