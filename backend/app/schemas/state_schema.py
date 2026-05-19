from typing import List, Dict, Any, TypedDict, Annotated
from pydantic import BaseModel, Field
from .user_schema import UserProfile
from .scheme_schema import Scheme

class AgentStateSchema(TypedDict):
    query: str                      # The original user input
    profile: UserProfile            # The continually updated user profile
    missing_fields: List[str]       # Information missing but required for candidate schemes
    candidate_schemes: List[Scheme] # Schemes retrieved from the DB (pre-filtering)
    eligible_schemes: List[Scheme]  # Schemes the LLM has confirmed the user is eligible for
    reasoning: str                  # A scratchpad for the LLM's explanation of eligibility
    messages: List[Dict[str, Any]]
