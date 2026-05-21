from fastapi import APIRouter, HTTPException 
from app.schemas.api_scheme import SchemeRecommendationRequest, SchemeRecommendationResponse
from app.services.profile_extractor import ProfileExtractionEngine

router = APIRouter()
extractor_engine = ProfileExtractionEngine()

@router.post("/", response_model=SchemeRecommendationResponse, summary="Process user query")
async def process_chat(request: SchemeRecommendationRequest):
    try:
        
        profile, missing_fields = await extractor_engine.extract_profile(
            query=request.query, 
            existing_profile=request.existing_profile
        )
        

        if missing_fields:
            missing_str = ", ".join(missing_fields)
            system_message = f"I have updated your profile. To help me recommend exact schemes, could you please provide your: {missing_str}?"
        else:
            system_message = "Thank you! I have all details. Evaluating eligible schemes for you now..."
            
        return SchemeRecommendationResponse(
            profile_summary=profile,
            eligible_schemes=[],  
            documents_needed=[],
            missing_info=missing_fields,
            system_message=system_message
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))