from typing import List, Dict, Any
from app.schemas.user_schema import UserProfile
from app.schemas.scheme_schema import Scheme

class ReflectionAgent:
    @staticmethod
    def detect_conflicts(profile: UserProfile) -> List[str]:
        conflicts = []

        if profile.age is not None and profile.age < 0:
            conflicts.append("Age cannot be negative.")
        if profile.income is not None and profile.income < 0:
            conflicts.append("Income cannot be negative.")
        
        if profile.age is not None and profile.education:
            edu_lower = profile.education.lower()
            if profile.age < 15 and any(term in edu_lower for term in ["engineering", "degree", "postgraduate"]):
                conflicts.append(f"Inconsistent profile: Age is {profile.age} but education is '{profile.education}'.")

        if profile.age is not None and profile.occupation:
            occ_lower = profile.occupation.lower()
            if profile.age < 14 and occ_lower in ["farmer", "retired", "officer"]:
                conflicts.append(f"Inconsistent profile: Age is {profile.age} but occupation is '{profile.occupation}'.")
                
        return conflicts

    @staticmethod
    def evaluate_confidence(query: str, profile: UserProfile) -> bool:
        clean_query = query.strip().lower()
        if len(clean_query) < 8:
            return True
        
        vals = [getattr(profile, f) for f in ["age", "state", "income", "occupation", "education"]]
        if all(v is None for v in vals):
            return True
        
        return False

    @classmethod
    def reflect(cls, query: str, profile: UserProfile, eligible_schemes: List[Scheme], missing_info: List[str]) -> Dict[str, Any]:
        conflicts = cls.detect_conflicts(profile)
        low_confidence = cls.evaluate_confidence(query, profile)
        need_more_info = len(conflicts) > 0 or len(missing_info) > 0

        reasons = []

        if conflicts:
            reasons.append(f"Conflicts: {'; '.join(conflicts)}")
        if low_confidence:
            reasons.append("Low extraction confidence (query too short or ambiguous).")
        if missing_info:
            reasons.append(f"Missing attributes: {', '.join(missing_info)}.")
        if eligible_schemes:
            reasons.append(f"Matched: {', '.join([s.name for s in eligible_schemes])}.")
        elif not need_more_info:
            reasons.append("No matching eligible schemes found.")

        return {
            "need_more_info": need_more_info,
            "missing": missing_info,
            "low_confidence": low_confidence,
            "conflicts": conflicts,
            "reasoning": " | ".join(reasons)
        }
