import os
from typing import List, Dict, Any
import google.generativeai as genai
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

        # ── DYNAMIC CONVERSATIONAL REPLY GENERATION ──
        agent_reply = None
        api_key = os.getenv("GEMINI_API_KEY")

        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                prompt = f"""
                You are an empathetic, helpful government scheme advisor assistant called Uplift.
                
                Review the active user session data:
                - User Message: "{query}"
                - Current Verified Profile: {profile.model_dump()}
                - Matching Eligible Schemes: {[s.name for s in eligible_schemes]}
                - Missing Profile Requirements: {missing_info}
                - Profile Conflicts: {conflicts}
                
                Formulate a short, conversational response (2-3 sentences max) to guide the user:
                - If they have matching schemes, congratulate them and mention the best scheme names.
                - If profile attributes are missing, politely ask them to clarify (remind them they can use the clickable options below).
                - If conflicts exist, ask for clarification.
                - Be warm, encouraging, and clear. Do not make up any other scheme details.
                
                Response:
                """
                
                response = model.generate_content(prompt)
                agent_reply = response.text.strip()
            except Exception as e:
                print(f"Gemini Reflection generation failed: {str(e)}")

        # Heuristic-based fallback if API is not set or fails
        if not agent_reply:
            if conflicts:
                agent_reply = f"I noticed some inconsistencies in your profile details: {'; '.join(conflicts)}. Could you please clarify?"
            elif missing_info:
                fields_str = ", ".join([f.replace('_', ' ') for f in missing_info])
                agent_reply = f"I have registered your details! To verify your eligibility for scholarships or grants, could you please provide your: {fields_str}? You can select one of the choices below."
            elif eligible_schemes:
                schemes_str = ", ".join([s.name for s in eligible_schemes[:2]])
                agent_reply = f"Great news! Based on your profile, you may qualify for {schemes_str} and {len(eligible_schemes) - 2} other schemes. Check them out on the right-hand dashboard!"
            else:
                agent_reply = "I've updated your profile details, but we couldn't find any matching schemes yet. Try entering more details about your education, income, or category."

        return {
            "need_more_info": need_more_info,
            "missing": missing_info,
            "low_confidence": low_confidence,
            "conflicts": conflicts,
            "reasoning": " | ".join(reasons),
            "agent_reply": agent_reply
        }
