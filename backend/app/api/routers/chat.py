from fastapi import APIRouter, HTTPException 
from app.schemas.api_scheme import ChatRequest, ChatResponse, ReflectionResult
from app.schemas.user_schema import UserProfile
from app.schemas.scheme_schema import Scheme
from app.workflows.langgraph_workflow import run_langgraph_workflow

router = APIRouter()

@router.post("/", response_model=ChatResponse, summary="Process user query")
async def process_chat(request: ChatRequest):
    try:
        profile_dict = request.existing_profile.model_dump() if request.existing_profile else None
        
        result = await run_langgraph_workflow(
            message=request.message,
            existing_profile=profile_dict
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        verified_schemes = result.get("verified_schemes", [])
        missing_fields = result.get("missing_fields", [])
        profile_data = result.get("profile", {})
        agent_reply = result.get("response", "")
        
        # De-duplicate documents from matched schemes
        documents = set()
        formatted_schemes = []
        for s in verified_schemes:
            for doc in s.get("required_documents", []):
                documents.add(doc)
            valid_fields = {k: v for k, v in s.items() if k in Scheme.model_fields}
            formatted_schemes.append(Scheme(**valid_fields))

        is_low_conf = len(request.message.strip().split()) <= 4 or len(missing_fields) >= 4
        reflection = ReflectionResult(
            need_more_info=result.get("status") == "clarification" or len(missing_fields) > 0,
            missing=missing_fields,
            low_confidence=is_low_conf,
            conflicts=[],
            reasoning="LangGraph multi-agent execution completed.",
            agent_reply=agent_reply
        )
        
        return ChatResponse(
            profile=UserProfile(**profile_data),
            eligible_schemes=formatted_schemes,
            documents=sorted(list(documents)),
            missing_info=missing_fields,
            reflection=reflection
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))