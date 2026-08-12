import logging
from typing import List, Dict, Any, Tuple, Optional
from app.schemas.user_schema import UserProfile
from app.schemas.scheme_schema import Scheme
from app.rag.vector_store import VectorStore
from app.services.scheme_service import SCHEMES_FILE_PATH, SchemeRetrievalService

logger = logging.getLogger(__name__)

class RAGRetriever:
    """
    Hybrid RAG Retriever combining dense semantic vector search 
    with hard metadata profile constraint filtering.
    """

    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.vector_store = vector_store or VectorStore()
        # Initialize index if empty
        if not self.vector_store.schemes:
            loaded = self.vector_store.load_from_disk()
            if not loaded:
                self.reindex_from_schemes_json()

    def reindex_from_schemes_json(self) -> None:
        """
        Re-indexes all schemes from data/schemes.json into the vector store.
        """
        service = SchemeRetrievalService()
        schemes = service._load_all_schemes()
        self.vector_store.build_index(schemes)
        self.vector_store.save_to_disk()

    def retrieve_candidates(
        self, query: str, profile: UserProfile, top_k: int = 15
    ) -> List[Tuple[Scheme, float]]:
        """
        Executes hybrid retrieval:
        1. Dense semantic search based on query.
        2. Filters out schemes violating explicit hard constraints (state, occupation, category, income).
        Returns list of (Scheme, vector_similarity_score).
        """
        # Search vector store
        vector_results = self.vector_store.similarity_search(query=query, top_k=len(self.vector_store.schemes) or 50)
        
        filtered_candidates: List[Tuple[Scheme, float]] = []

        for scheme, score in vector_results:
            # Metadata filtering
            if profile.state and scheme.state:
                if scheme.state.lower() != "central" and scheme.state.lower() != profile.state.lower():
                    continue

            if profile.occupation and scheme.occupation:
                if scheme.occupation.lower() != profile.occupation.lower():
                    continue

            if profile.income is not None and scheme.income_limit is not None:
                if profile.income > scheme.income_limit:
                    continue

            if profile.category and scheme.category:
                clean_categories = [c.lower() for c in scheme.category]
                if profile.category.lower() not in clean_categories:
                    continue

            filtered_candidates.append((scheme, score))

        # Sort by similarity score descending
        filtered_candidates.sort(key=lambda x: x[1], reverse=True)
        return filtered_candidates[:top_k]
