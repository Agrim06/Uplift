from fastapi import APIRouter

router = APIRouter()

@router.get("/", summary="Check App health")
async def health_check():
    return{
        "status":"healthy",
        "version":"1.0.0"
    }