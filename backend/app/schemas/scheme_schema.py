from typing import List, Optional, Any
from pydantic import BaseModel, Field

class EligibilityRule(BaseModel):
    attribute: str = Field(..., description="The user profile attribute this rule targets.")
    condition: str = Field(..., description="The comparison condition: 'equals', 'lte', 'gte', 'in', etc.")
    value: Any = Field(..., description="The comparative value (e.g. threshold, state string, list of strings).")
    description: str = Field(..., description="Plain-text human-friendly explanation of the rule.")

class Scheme(BaseModel):
    id: str = Field(..., description="Unique identifier for the scheme.")
    name: str = Field(..., description="Official name of the government scheme.")
    description: str = Field(..., description="A brief summary of what the scheme provides.")
    scheme_type: str = Field(..., description="Type of the scheme (e.g. Scholarship, Welfare).")
    target_group: str = Field(..., description="Target group details.")
    age_limit: Optional[str] = Field(None, description="Age constraints represented as descriptive text.")
    income_limit: Optional[float] = Field(None, description="Maximum allowable annual family income in INR.")
    education_requirement: str = Field(..., description="Educational requirement details.")
    occupation: str = Field(..., description="Target occupation (e.g., Student, Farmer).")
    state: str = Field(..., description="State of origin/restriction (e.g., Karnataka, Central).")
    category: List[str] = Field(..., description="Social categories allowed (e.g. SC, ST, OBC, General).")
    required_documents: List[str] = Field(default_factory=list, description="List of documents needed to apply.")
    benefits: str = Field(..., description="Plain-text description of benefits.")
    application_link: Optional[str] = Field(None, description="Link to the official application portal.")
    official_source: Optional[str] = Field(None, description="Link to the official department source page.")
    deadline: Optional[str] = Field(None, description="Application deadline date, if applicable.")
    eligibility_rules: List[EligibilityRule] = Field(default_factory=list, description="Structured criteria for evaluation.")
