import os
import json 
import re
from typing import Optional, List, Any, Tuple, Dict
import google.generativeai as genai
from app.schemas.user_schema import UserProfile

MANDATORY_FIELDS = ["age", "state", "income", "occupation", "education"]

VALID_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", 
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", 
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", 
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi"
]

class ProfileExtractionEngine:

    @staticmethod
    def normalize_state(row_state: Optional[str]) -> Optional[str]:
        if not row_state:
            return None
        clean_state = row_state.strip().lower()
        for state in VALID_STATES:
            if clean_state == state.lower() or clean_state in state.lower():
                return state
        return row_state
    
    @staticmethod
    def validate_and_normalize(profile_dict: Dict[str, Any]) -> Dict[str, Any]:
        normalized = profile_dict.copy()
        if "state" in normalized:
            normalized["state"] = ProfileExtractionEngine.normalize_state(normalized["state"])
        
        if "income" in normalized and normalized["income"] is not None:
            try:
                val = float(normalized["income"])
                normalized["income"] = max(0.0, val)
            except (ValueError, TypeError):
                normalized["income"] = None
                
        if "age" in normalized and normalized["age"] is not None:
            try:
                val = int(normalized["age"])
                if 0 <= val <= 120:
                    normalized["age"] = val
                else:
                    normalized["age"] = None
            except (ValueError, TypeError):
                normalized["age"] = None
        return normalized

    @staticmethod
    def merge_profiles(existing: Optional[UserProfile], extracted: Dict[str, Any]) -> UserProfile:
        if not existing:
            return UserProfile(**{k: extracted.get(k) for k in UserProfile.model_fields.keys()})
        merged_data = existing.model_dump()
        for key, val in extracted.items():
            if val is not None:
                merged_data[key] = val
        return UserProfile(**merged_data)

    @staticmethod
    def detect_missing_fields(profile: UserProfile) -> List[str]:
        missing = []
        for field in MANDATORY_FIELDS:
            val = getattr(profile, field, None)
            if val is None or val == "":
                missing.append(field)
        return missing
    
    async def extract_profile(self, query: str, existing_profile: Optional[UserProfile] = None) -> Tuple[UserProfile, List[str]]:
        raw_extraction = self._gemini_extract(query)
        normalized_data = self.validate_and_normalize(raw_extraction)
        final_profile = self.merge_profiles(existing_profile, normalized_data)
        missing_fields = self.detect_missing_fields(final_profile)
        return final_profile, missing_fields

    def _gemini_extract(self, query: str) -> Dict[str, Any]:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # Resilient fallback if no key is configured
            return self._mock_llm_extract(query)

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config={"response_mime_type": "application/json"}
            )
            
            prompt = f"""
            You are an expert profile extraction AI. Analyze the user's natural language input and extract their profile attributes into a JSON object.
            
            Strictly extract ONLY the following fields. If a field is not mentioned or cannot be inferred, set it to null:
            - age (integer, representing age in years)
            - state (string, Indian state of residence, e.g. "Karnataka", "Maharashtra")
            - occupation (string, e.g. "Student", "Farmer")
            - education (string, e.g. "Engineering", "Class 10")
            - income (float, annual family income in INR. Convert expressions like "2 Lakh" to 200000.0)
            - gender (string, e.g. "Male", "Female", "Other")
            - category (string, social/caste category: "General", "OBC", "SC", "ST")
            
            User Input: "{query}"
            
            Output JSON:
            """
            
            response = model.generate_content(prompt)
            data = json.loads(response.text)
            
            return {
                "age": data.get("age"),
                "state": data.get("state"),
                "occupation": data.get("occupation"),
                "education": data.get("education"),
                "income": data.get("income"),
                "gender": data.get("gender"),
                "category": data.get("category")
            }
        except Exception as e:
            # Fall back to mock extract on network or rate limit failure
            print(f"Gemini API call failed: {str(e)}. Falling back to mock extractor.")
            return self._mock_llm_extract(query)

    def _mock_llm_extract(self, query: str) -> Dict[str, Any]:
        """Mock LLM parsing logic for iteration 1 testing."""
        result = {
            "age": None, "state": None, "occupation": None, 
            "education": None, "income": None, "gender": None, "category": None
        }
        query_lower = query.lower()
        
        age_match = re.search(r'\b(\d{1,2})\s*(?:-|year|yr|age|old)', query_lower)
        if not age_match:
            age_match = re.search(r'\b(?:am|im|i\'m)\s*(?:a\s+)?(\d{1,2})\b', query_lower)
        if not age_match:
            age_match = re.search(r'\bage\s*(?:is|:)?\s*(\d{1,2})\b', query_lower)
        if age_match:
            result["age"] = int(age_match.group(1))
            
        for state in VALID_STATES:
            if state.lower() in query_lower:
                result["state"] = state
                break
        if not result["state"]:
            if "kar" in query_lower:
                result["state"] = "Karnataka"
            
        if "student" in query_lower:
            result["occupation"] = "Student"
        elif "farmer" in query_lower:
            result["occupation"] = "Farmer"
            
        if "engineering" in query_lower:
            result["education"] = "Engineering"
        elif "class 10" in query_lower or "10th" in query_lower:
            result["education"] = "Class 10"
            
        income_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(?:lakh|l)\b', query_lower)
        if income_match:
            result["income"] = float(income_match.group(1)) * 100000.0
        else:
            income_match = re.search(r'\bincome\s*(?:of|is)?\s*(\d+)\b', query_lower)
            if income_match:
                result["income"] = float(income_match.group(1))
        
        if re.search(r'\bfemale\b|\bgirl\b|\bwoman\b', query_lower):
            result["gender"] = "Female"
        elif re.search(r'\bmale\b|\bboy\b|\bman\b', query_lower):
            result["gender"] = "Male"
        elif re.search(r'\bother\b', query_lower):
            result["gender"] = "Other"

        if re.search(r'\bsc\b', query_lower):
            result["category"] = "SC"
        elif re.search(r'\bst\b', query_lower):
            result["category"] = "ST"
        elif re.search(r'\bobc\b', query_lower):
            result["category"] = "OBC"
        elif re.search(r'\bgeneral\b', query_lower):
            result["category"] = "General"
        return result
