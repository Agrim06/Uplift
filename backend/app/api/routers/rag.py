from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.user_schema import UserProfile
from app.rag.retriever import RAGRetriever

router = APIRouter()
rag_retriever = RAGRetriever()

class RAGSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    profile: Optional[UserProfile] = Field(default_factory=UserProfile, description="User profile constraints")
    top_k: int = Field(default=10, ge=1, le=50, description="Max number of candidate schemes to retrieve")

class RAGSearchResponse(BaseModel):
    total_retrieved: int
    query: str
    schemes: List[Dict[str, Any]]

@router.post("/search", response_model=RAGSearchResponse, summary="Perform RAG hybrid vector search")
async def rag_search(request: RAGSearchRequest):
    try:
        results = rag_retriever.retrieve_candidates(
            query=request.query,
            profile=request.profile or UserProfile(),
            top_k=request.top_k
        )
        
        formatted_schemes = []
        for scheme, score in results:
            scheme_dict = scheme.model_dump()
            pct = max(50, min(99, int(score * 100))) if score > 0 else 80
            scheme_dict["match_score"] = pct
            scheme_dict["similarity_raw"] = round(score, 4)
            formatted_schemes.append(scheme_dict)

        return RAGSearchResponse(
            total_retrieved=len(formatted_schemes),
            query=request.query,
            schemes=formatted_schemes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG search failed: {str(e)}")

@router.post("/reindex", summary="Reindex scheme vector store")
async def rag_reindex():
    try:
        rag_retriever.reindex_from_schemes_json()
        total_schemes = len(rag_retriever.vector_store.schemes)
        return {
            "status": "success",
            "message": f"Successfully reindexed {total_schemes} schemes into vector store.",
            "vector_count": total_schemes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG reindexing failed: {str(e)}")
