from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

class Scheme(BaseModel):
    scheme_id: str = Field(..., description="Unique identifier for the scheme.")
    scheme_name: str = Field(..., description="Official name of the government scheme.")
    description: str = Field(..., description="A brief summary of what the scheme provides.")
    
    income_limit: Optional[float] = Field(None, description="Maximum allowable annual family income to be eligible.")
    age_limit_min: Optional[int] = Field(None, description="Minimum age required.")
    age_limit_max: Optional[int] = Field(None, description="Maximum age allowed.")
    state_restriction: Optional[str] = Field(None, description="Specific state this scheme applies to. None if central/national.")
    
    eligibility_criteria: List[str] = Field(default_factory=list, description="List of textual criteria for LLM evaluation.") 
    required_documents: List[str] = Field(default_factory=list, description="List of documents needed to apply.")
    benefits: List[str] = Field(default_factory=list, description="List of financial or material benefits provided.")
    official_link: Optional[HttpUrl] = Field(None, description="Link to the official application portal.")
    deadline: Optional[str] = Field(None, description="Application deadline date, if applicable.")

