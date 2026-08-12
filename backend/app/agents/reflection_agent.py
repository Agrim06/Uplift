import os
from typing import List, Dict, Any, Optional
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
    def reflect(
        cls, 
        query: str, 
        profile: UserProfile, 
        eligible_schemes: List[Scheme], 
        missing_info: List[str],
        match_scores: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        conflicts = cls.detect_conflicts(profile)
        low_confidence = cls.evaluate_confidence(query, profile)
        need_more_info = len(conflicts) > 0 or len(missing_info) > 0
        match_scores = match_scores or {}

        reasons = []
        if conflicts:
            reasons.append(f"Conflicts: {'; '.join(conflicts)}")
        if low_confidence:
            reasons.append("Low extraction confidence (query too short or ambiguous).")
        if missing_info:
            reasons.append(f"Missing attributes: {', '.join(missing_info)}.")
        if eligible_schemes:
            reasons.append(f"Matched {len(eligible_schemes)} RAG schemes.")
        elif not need_more_info:
            reasons.append("No matching eligible schemes found.")

        # Build RAG Context snippets
        rag_passages = []
        for s in eligible_schemes[:3]:
            score = match_scores.get(s.id, 0.0)
            passage = f"• {s.name} (RAG Match Score: {int(score * 100)}%): {s.description}. Benefits: {s.benefits}"
            rag_passages.append(passage)
        rag_context_text = "\n".join(rag_passages) if rag_passages else "No relevant schemes retrieved."

        # ── DYNAMIC RAG CONVERSATIONAL REPLY GENERATION ──
        agent_reply = None
        api_key = os.getenv("GEMINI_API_KEY")

        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                prompt = f"""
                You are an empathetic, grounded government scheme advisor assistant called Uplift.
                
                Review the active user query and RAG retrieved context:
                - User Query: "{query}"
                - Current Verified User Profile: {profile.model_dump()}
                - RAG Retrieved Schemes & Passages:
                {rag_context_text}
                - Missing Profile Attributes Needed: {missing_info}
                - Next Missing Attribute Needed: {missing_info[0] if missing_info else 'None'}
                - Profile Inconsistencies: {conflicts}
                
                Formulate a clear, helpful response (2-3 sentences max):
                - Ground your statements ONLY in the retrieved RAG scheme context provided above.
                - If profile attributes are missing, guide the user to provide the NEXT missing attribute: "{missing_info[0] if missing_info else ''}".
                - If eligible schemes are found, highlight the top scheme and mention its benefit.
                - Be warm, encouraging, and accurate. Do not invent ungrounded details.
                
                Response:
                """
                
                response = model.generate_content(prompt)
                agent_reply = response.text.strip()
            except Exception as e:
                print(f"Gemini RAG Reflection generation failed: {str(e)}")

        # Heuristic-based fallback if API is not set or fails
        if not agent_reply:
            if conflicts:
                agent_reply = f"I noticed some inconsistencies in your profile details: {'; '.join(conflicts)}. Could you please clarify?"
            elif missing_info:
                first_missing = missing_info[0].replace('_', ' ')
                agent_reply = f"I have registered your details! To help match you with eligible schemes, could you please tell me your {first_missing}? You can select one of the choices below."
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
