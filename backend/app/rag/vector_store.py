import os
import json
import logging
from typing import List, Dict, Any, Tuple, Optional
import chromadb
from app.schemas.scheme_schema import Scheme
from app.rag.embedder import SchemeEmbedder

logger = logging.getLogger(__name__)

DEFAULT_CHROMA_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma_db")
)

class VectorStore:
    """
    ChromaDB-backed vector store for government scheme embeddings and hybrid retrieval.
    """

    def __init__(self, db_path: str = DEFAULT_CHROMA_DB_PATH, embedder: Optional[SchemeEmbedder] = None):
        self.db_path = db_path
        self.embedder = embedder or SchemeEmbedder()
        
        os.makedirs(self.db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(
            name="schemes_collection",
            metadata={"hnsw:space": "cosine"}
        )
        self._cached_schemes: Optional[List[Scheme]] = None

    @property
    def schemes(self) -> List[Scheme]:
        """
        Retrieves all currently indexed schemes from ChromaDB collection.
        """
        if self._cached_schemes is not None:
            return self._cached_schemes

        try:
            stored = self.collection.get(include=["metadatas"])
            if stored and stored.get("metadatas"):
                result_schemes = []
                for meta in stored["metadatas"]:
                    if meta and "scheme_json" in meta:
                        try:
                            scheme_dict = json.loads(meta["scheme_json"])
                            result_schemes.append(Scheme(**scheme_dict))
                        except Exception as parse_err:
                            logger.warning(f"Error parsing scheme metadata: {parse_err}")
                self._cached_schemes = result_schemes
                return result_schemes
        except Exception as e:
            logger.error(f"Error fetching schemes from ChromaDB: {e}")
        
        return []

    def build_index(self, schemes: List[Scheme]) -> None:
        """
        Fits vector embedder on schemes corpus and upserts all schemes into ChromaDB.
        """
        logger.info(f"Building ChromaDB vector store index for {len(schemes)} schemes...")
        if not schemes:
            return

        self.embedder.fit(schemes)

        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for scheme in schemes:
            doc_text = self.embedder.extract_text(scheme)
            vec = self.embedder.embed_scheme(scheme)
            
            ids.append(scheme.id)
            documents.append(doc_text)
            embeddings.append(vec)
            
            # Store metadata attributes and full scheme JSON string
            meta = {
                "id": scheme.id,
                "name": scheme.name,
                "state": scheme.state or "Central",
                "occupation": scheme.occupation or "General",
                "income_limit": float(scheme.income_limit) if scheme.income_limit is not None else -1.0,
                "scheme_type": scheme.scheme_type,
                "scheme_json": json.dumps(scheme.model_dump())
            }
            metadatas.append(meta)

        # Upsert into ChromaDB collection
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        self._cached_schemes = schemes
        logger.info(f"Successfully indexed {len(schemes)} schemes into ChromaDB collection.")

    def similarity_search(self, query: str, top_k: int = 10) -> List[Tuple[Scheme, float]]:
        """
        Executes vector similarity search against ChromaDB collection given a natural language query text.
        Returns a list of tuples: (Scheme, similarity_score).
        """
        if self.collection.count() == 0:
            return []

        # Make sure embedder is fitted if not already
        if not self.embedder.is_fitted:
            all_schemes = self.schemes
            if all_schemes:
                self.embedder.fit(all_schemes)

        query_vec = self.embedder.embed_text(query)
        
        # Query ChromaDB collection
        n_results = min(top_k, self.collection.count())
        query_results = self.collection.query(
            query_embeddings=[query_vec],
            n_results=n_results,
            include=["metadatas", "distances"]
        )

        scored_results: List[Tuple[Scheme, float]] = []

        if query_results and query_results.get("metadatas") and query_results.get("distances"):
            metas = query_results["metadatas"][0]
            distances = query_results["distances"][0]

            for meta, dist in zip(metas, distances):
                if meta and "scheme_json" in meta:
                    try:
                        scheme_dict = json.loads(meta["scheme_json"])
                        scheme = Scheme(**scheme_dict)
                        # Cosine distance to similarity: similarity = max(0, 1 - distance)
                        similarity = max(0.0, 1.0 - float(dist))
                        scored_results.append((scheme, round(similarity, 4)))
                    except Exception as e:
                        logger.error(f"Error parsing Chroma query result item: {e}")

        # Sort descending by similarity score
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results

    def save_to_disk(self) -> None:
        """
        ChromaDB PersistentClient automatically persists data to disk.
        """
        pass

    def load_from_disk(self) -> bool:
        """
        ChromaDB PersistentClient automatically loads data from disk on initialization.
        Returns True if collection contains indexed items.
        """
        count = self.collection.count()
        if count > 0:
            logger.info(f"Loaded ChromaDB collection with {count} indexed schemes.")
            return True
        return False
