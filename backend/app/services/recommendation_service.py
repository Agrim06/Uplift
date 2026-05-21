from typing import List, Dict, Any, Tuple
from app.schemas.user_schema import UserProfile
from app.schemas.scheme_schema import Scheme, EligibilityRule, EligibilityEvaluation

class EligibilityEvaluator:
    @staticmethod
    def evaluate_rule(user_val: Any, rule: EligibilityRule) -> Tuple[bool, str]:
        cond = rule.condition.lower()
        rule_val = rule.value

        if cond == "equals":
            if isinstance(user_val, str) and isinstance(rule_val, str):
                passed = user_val.strip().lower() == rule_val.strip().lower()
            else:
                passed = user_val == rule_val 

            suffix = "matches" if passed else "does not match"
            return passed, f"{rule.description} (User value '{user_val}' {suffix} requirement '{rule_val}')"

        elif cond == "lte":
            try:
                passed = float(user_val) <= float(rule_val)
                suffix = "within limit" if passed else "exceeds limit"
                return passed, f"{rule.description} (User value {user_val} {suffix} of {rule_val})"
            except (ValueError, TypeError):
                return False, f"Invalid type comparison for condition lte: User {user_val}, Rule {rule_val}"
        
        elif cond == "gte":
            try:
                passed = float(user_val) >= float(rule_val)
                suffix = "meets threshold" if passed else "is below threshold"
                return passed, f"{rule.description} (User value {user_val} {suffix} of {rule_val})"
            except (ValueError, TypeError):
                return False, f"Invalid type comparison for condition gte: User {user_val}, Rule {rule_val}"  
        
        elif cond == "in":
            if isinstance(rule_val, list):
                clean_list = [str(item).strip().lower() for item in rule_val]
                passed = str(user_val).strip().lower() in clean_list
                suffix = "is valid" if passed else "is invalid"
                return passed, f"{rule.description} (User value '{user_val}' {suffix} in {rule_val})"
            return False, f"Expected list for 'in' condition, got {type(rule_val)}"
        return False, f"Unknown condition: '{cond}'"
    @classmethod
    def evaluate_scheme(cls, profile: UserProfile, scheme: Scheme) -> EligibilityEvaluation:
        is_ineligible = False
        reasons = []
        missing_fields = []
        
        for rule in scheme.eligibility_rules:
            attr = rule.attribute
            user_val = getattr(profile, attr, None)
            
            # Handling missing profile data
            if user_val is None:
                missing_fields.append(attr)
                continue
                
            passed, desc = cls.evaluate_rule(user_val, rule)
            reasons.append(desc)
            if not passed:
                is_ineligible = True
                
        if is_ineligible:
            return EligibilityEvaluation(
                eligible=False,
                reason=reasons,
                missing_requirements=[]
            )
        elif missing_fields:
            return EligibilityEvaluation(
                eligible="unknown",
                reason=reasons,
                missing_requirements=missing_fields
            )
        else:
            if not reasons:
                reasons.append("No specific eligibility rules defined for this scheme.")
            return EligibilityEvaluation(
                eligible=True,
                reason=reasons,
                missing_requirements=[]
            )