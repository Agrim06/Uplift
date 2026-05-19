from fastapi import APIRouter, HTTPException 
from app.schemas.api_scheme import SchemeRecommendationRequest, SchemeRecommendationResponse
from app.schemas.user_schema import UserProfile

router = APIRouter()

@router.post("/", response_model=SchemeRecommendationResponse, summary="Process user query")
async def process_chat(request: SchemeRecommendationRequest):

    #Hardcoded dummy for testing
    try:
        mock_profile = UserProfile(
            age=20,
            state="Karnataka",
            occupation="Student",
            education=None,
            income=200000.0,
            gender=None,
            category=None
       )
       
        return SchemeRecommendationResponse(
            profile_summary=mock_profile,
            eligible_schemes=[], # Empty for now
            documents_needed=[],
            missing_info=["education", "category"],
            system_message="I see you are a student from Karnataka. Could you please specify your current education level and social category so I can find exact schemes for you?"
       )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail= str(e))