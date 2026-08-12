import math
import re
from typing import List, Dict
from app.schemas.scheme_schema import Scheme

class SchemeEmbedder:
    """
    Generates text document representations and normalized dense vector embeddings 
    for government schemes and natural language user queries.
    """
    
    def __init__(self, vector_dim: int = 256):
        self.vector_dim = vector_dim
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.is_fitted = False

    @staticmethod
    def extract_text(scheme: Scheme) -> str:
        """
        Combines key scheme attributes into a rich searchable document text.
        """
        rule_texts = " ".join([r.description for r in scheme.eligibility_rules])
        category_text = " ".join(scheme.category) if scheme.category else ""
        docs_text = " ".join(scheme.required_documents) if scheme.required_documents else ""
        
        parts = [
            f"Scheme Name: {scheme.name}",
            f"Description: {scheme.description}",
            f"Type: {scheme.scheme_type}",
            f"Target Group: {scheme.target_group}",
            f"Education: {scheme.education_requirement}",
            f"Occupation: {scheme.occupation}",
            f"State: {scheme.state}",
            f"Category: {category_text}",
            f"Benefits: {scheme.benefits}",
            f"Eligibility Rules: {rule_texts}",
            f"Required Documents: {docs_text}"
        ]
        return " | ".join(parts)

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenizes text into normalized lower-case unigrams and bigrams for rich semantic matching.
        """
        clean_text = re.sub(r"[^\w\s]", " ", text.lower())
        words = [w for w in clean_text.split() if len(w) > 1]
        
        tokens = list(words)
        # Add bigrams for context binding (e.g. 'girl child', 'post matric', 'farmer loan')
        for i in range(len(words) - 1):
            tokens.append(f"{words[i]}_{words[i+1]}")
        return tokens

    def fit(self, schemes: List[Scheme]) -> None:
        """
        Fits vocabulary and IDF dictionary across all scheme corpus documents.
        """
        doc_count = len(schemes)
        if doc_count == 0:
            return

        df: Dict[str, int] = {}
        
        for scheme in schemes:
            text = self.extract_text(scheme)
            tokens = set(self._tokenize(text))
            for t in tokens:
                df[t] = df.get(t, 0) + 1
        
        # Sort terms by document frequency to form vocabulary dictionary up to vector_dim
        sorted_terms = sorted(df.keys(), key=lambda t: df[t], reverse=True)[: self.vector_dim]
        self.vocabulary = {term: idx for idx, term in enumerate(sorted_terms)}
        
        # Calculate Inverse Document Frequency (IDF)
        self.idf = {
            term: math.log((1.0 + doc_count) / (1.0 + df[term])) + 1.0
            for term in self.vocabulary
        }
        self.is_fitted = True

    def embed_text(self, text: str) -> List[float]:
        """
        Converts text into an L2-normalized vector embedding based on fitted vocabulary.
        """
        if not self.is_fitted or not self.vocabulary:
            return [0.0] * self.vector_dim

        tokens = self._tokenize(text)
        term_freqs: Dict[str, int] = {}
        for t in tokens:
            if t in self.vocabulary:
                term_freqs[t] = term_freqs.get(t, 0) + 1

        vec = [0.0] * len(self.vocabulary)
        for term, count in term_freqs.items():
            idx = self.vocabulary[term]
            tf = 1.0 + math.log(count) if count > 0 else 0.0
            vec[idx] = tf * self.idf.get(term, 1.0)

        # L2 Normalization
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
            
        return vec

    def embed_scheme(self, scheme: Scheme) -> List[float]:
        """
        Embeds a Scheme instance into a normalized vector.
        """
        text = self.extract_text(scheme)
        return self.embed_text(text)

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """
        Calculates cosine similarity between two float vectors.
        """
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)
