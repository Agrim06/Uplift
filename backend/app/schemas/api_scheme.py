from typing import List, Optional
from pydantic import BaseModel, Field
from .user_schema import UserProfile
from .scheme_schema import Scheme

class ChatRequest(BaseModel):
    message: str = Field(
        ..., 
        examples=["I am a 20-year-old engineering student from Karnataka with an annual family income of 2 lakh."]
    )
    existing_profile: Optional[UserProfile] = None

class ReflectionResult(BaseModel):
    need_more_info: bool = Field(..., description="True if the agent needs more information from the user.")
    missing: List[str] = Field(default_factory=list, description="List of profile fields that are missing.")
    low_confidence: bool = Field(..., description="True if the extraction confidence is low.")
    conflicts: List[str] = Field(default_factory=list, description="List of logical conflicts found.")
    reasoning: str = Field(..., description="Reasoning scratchpad summarizing reflection findings.")
    agent_reply: Optional[str] = Field(None, description="Empathic conversational response formulated by the AI.")

class ChatResponse(BaseModel):
    profile: UserProfile = Field(..., description="The user profile as understood by the system so far.")
    eligible_schemes: List[Scheme] = Field(..., description="List of schemes the user is eligible for.")
    documents: List[str] = Field(default_factory=list, description="De-duplicated list of required documents.")
    missing_info: List[str] = Field(default_factory=list, description="Fields the system needs the user next.")
    reflection: ReflectionResult = Field(..., description="The outcome of the reflection layer evaluation.")
