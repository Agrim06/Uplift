import os
import json
import logging
from typing import List, Dict, Any, Tuple, Optional
from app.schemas.scheme_schema import Scheme
from app.rag.embedder import SchemeEmbedder

logger = logging.getLogger(__name__)

DEFAULT_VECTOR_STORE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "vector_store.json")
)

class VectorStore:
    """
    In-memory and file-persisted vector store for government scheme embeddings.
    """

    def __init__(self, filepath: str = DEFAULT_VECTOR_STORE_PATH, embedder: Optional[SchemeEmbedder] = None):
        self.filepath = filepath
        self.embedder = embedder or SchemeEmbedder()
        self.schemes: List[Scheme] = []
        self.vectors: List[List[float]] = []

    def build_index(self, schemes: List[Scheme]) -> None:
        """
        Fits embedder vocabulary on scheme corpus, embeds all schemes, and stores index.
        """
        logger.info(f"Building RAG vector store index for {len(schemes)} schemes...")
        self.schemes = schemes
        self.embedder.fit(schemes)
        self.vectors = [self.embedder.embed_scheme(s) for s in schemes]
        logger.info("Vector store index build complete.")

    def similarity_search(self, query: str, top_k: int = 10) -> List[Tuple[Scheme, float]]:
        """
        Performs vector similarity search given a natural language query text.
        Returns a list of tuples: (Scheme, similarity_score).
        """
        if not self.schemes or not self.vectors:
            return []

        query_vec = self.embedder.embed_text(query)
        scored_results: List[Tuple[Scheme, float]] = []

        for scheme, scheme_vec in zip(self.schemes, self.vectors):
            score = self.embedder.cosine_similarity(query_vec, scheme_vec)
            scored_results.append((scheme, score))

        # Sort by similarity score descending
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:top_k]

    def save_to_disk(self) -> None:
        """
        Persists scheme embeddings and vocabulary index to disk.
        """
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        data = {
            "vocabulary": self.embedder.vocabulary,
            "idf": self.embedder.idf,
            "vector_dim": self.embedder.vector_dim,
            "schemes": [s.model_dump() for s in self.schemes],
            "vectors": self.vectors
        }
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Persisted vector store index to {self.filepath}")

    def load_from_disk(self) -> bool:
        """
        Loads vector store index and vocabulary from disk if it exists.
        Returns True if loaded successfully, False otherwise.
        """
        if not os.path.exists(self.filepath):
            return False

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.embedder.vocabulary = data.get("vocabulary", {})
            self.embedder.idf = data.get("idf", {})
            self.embedder.vector_dim = data.get("vector_dim", 256)
            self.embedder.is_fitted = True

            self.schemes = [Scheme(**s) for s in data.get("schemes", [])]
            self.vectors = data.get("vectors", [])
            logger.info(f"Loaded {len(self.schemes)} vector indexed schemes from {self.filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load vector store from disk: {e}")
            return False
