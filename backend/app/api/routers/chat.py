from fastapi import APIRouter, HTTPException 
from app.schemas.api_scheme import ChatRequest, ChatResponse
from app.workflows.agent_workflow import run_workflow

router = APIRouter()

@router.post("/", response_model=ChatResponse, summary="Process user query")
async def process_chat(request: ChatRequest):
    try:
        result = await run_workflow(
            query=request.message,
            existing_profile=request.existing_profile
        )
        
        # Handle workflow errors
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))