import logging
from typing import List, Dict, Any, Optional
from app.schemas.user_schema import UserProfile
from app.services.profile_extractor import ProfileExtractionEngine
from app.rag.retriever import RAGRetriever
from app.services.recommendation_service import EligibilityEvaluator
from app.agents.reflection_agent import ReflectionAgent

logger = logging.getLogger(__name__)

# Initialize engine services
extractor_engine = ProfileExtractionEngine()
rag_retriever = RAGRetriever()

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
    Stage 2: Scheme Retrieval via RAG (Vector Similarity Search + Profile Hard Filtering)
    """
    query = state.get("query", "")
    profile = state.get("profile", UserProfile())
    
    # Execute RAG hybrid retrieval
    scored_candidates = rag_retriever.retrieve_candidates(query=query, profile=profile, top_k=15)
    
    candidates = [scheme for scheme, _ in scored_candidates]
    match_scores = {scheme.id: round(score, 4) for scheme, score in scored_candidates}

    return {
        "candidate_schemes": candidates,
        "match_scores": match_scores
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
    Performs consistency checks and compiles RAG-grounded agent reasoning logs via ReflectionAgent.
    """
    reflection_data = ReflectionAgent.reflect(
        query=state["query"],
        profile=state["profile"],
        eligible_schemes=state["eligible_schemes"],
        missing_info=state["missing_info"],
        match_scores=state.get("match_scores", {})
    )
    return {
        "reflection": reflection_data
    }

def format_response_step(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 5: Response Formatting
    Extracts, de-duplicates documents and formats final output schema with RAG match scores.
    """
    eligible_schemes = state["eligible_schemes"]
    match_scores = state.get("match_scores", {})
    
    # Extract and de-duplicate documents
    documents = set()
    formatted_schemes = []
    
    for scheme in eligible_schemes:
        documents.update(scheme.required_documents)
        scheme_dict = scheme.model_dump()
        score = match_scores.get(scheme.id, 0.0)
        # Convert float similarity score to match percentage (e.g. 0.85 -> 85%)
        pct = max(50, min(99, int(score * 100))) if score > 0 else 80
        scheme_dict["match_score"] = pct
        scheme_dict["similarity_raw"] = score
        formatted_schemes.append(scheme_dict)

    return {
        "profile": state["profile"].model_dump(),
        "eligible_schemes": formatted_schemes,
        "missing_info": state["missing_info"],
        "documents": sorted(list(documents)),
        "reflection": state["reflection"]
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
        "reflection": None,
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
            "reflection": {
                "need_more_info": False,
                "missing": [],
                "low_confidence": True,
                "conflicts": [],
                "reasoning": f"Workflow failed: {str(e)}"
            },
            "error": f"Workflow failed: {str(e)}"
        }