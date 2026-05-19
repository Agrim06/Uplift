from typing import Optional
from pydantic import BaseModel , Field

class UserProfile(BaseModel):
    age: Optional[int] = Field(None, description="Age of the user in years")
    state: Optional[str] = Field(None, description="State of residence in India (e.g., 'Karnataka').")
    occupation: Optional[str] = Field(None, description="Current occupation (e.g., 'student', 'farmer').")
    education: Optional[str] = Field(None, description="Highest level of education completed or currently pursuing.")
    income: Optional[float] = Field(None, description="Annual family income in INR.")
    gender: Optional[str] = Field(None, description="Gender of the user (e.g., 'Male', 'Female', 'Other').")
    category: Optional[str] = Field(None, description="Caste/Social category (e.g., 'General', 'OBC', 'SC', 'ST').")