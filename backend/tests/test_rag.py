import pytest
from app.schemas.scheme_schema import Scheme, EligibilityRule
from app.schemas.user_schema import UserProfile
from app.rag.embedder import SchemeEmbedder
from app.rag.vector_store import VectorStore
from app.rag.retriever import RAGRetriever

@pytest.fixture
def sample_schemes():
    return [
        Scheme(
            id="SCH-1",
            name="PM Kisan Samman Nidhi",
            description="Direct income support of 6000 per year for small and marginal farmers.",
            scheme_type="Financial Support",
            target_group="Farmers",
            age_limit="18 - 70 years",
            income_limit=300000.0,
            education_requirement="None",
            occupation="Farmer",
            state="Central",
            category=["General", "OBC", "SC", "ST"],
            required_documents=["Aadhaar Card", "Land Ownership Records"],
            benefits="Rs 6000 financial assistance per year",
            eligibility_rules=[
                EligibilityRule(attribute="occupation", condition="equals", value="Farmer", description="Must be a farmer")
            ]
        ),
        Scheme(
            id="SCH-2",
            name="Post Matric Scholarship for SC Students",
            description="Financial support for SC category post matric higher education students.",
            scheme_type="Scholarship",
            target_group="SC Students",
            age_limit="15 - 30 years",
            income_limit=250000.0,
            education_requirement="10th Pass",
            occupation="Student",
            state="Maharashtra",
            category=["SC"],
            required_documents=["Caste Certificate", "Income Certificate", "Marksheet"],
            benefits="Full tuition fee reimbursement and monthly stipend",
            eligibility_rules=[
                EligibilityRule(attribute="occupation", condition="equals", value="Student", description="Must be a student"),
                EligibilityRule(attribute="category", condition="in", value=["SC"], description="Must belong to SC category")
            ]
        )
    ]

def test_scheme_embedder(sample_schemes):
    embedder = SchemeEmbedder(vector_dim=128)
    embedder.fit(sample_schemes)
    assert embedder.is_fitted is True
    assert len(embedder.vocabulary) > 0

    vec_query = embedder.embed_text("scholarship for college student in maharashtra")
    vec_farmer = embedder.embed_text("financial help for agriculture farmers")
    
    assert len(vec_query) == 128
    assert len(vec_farmer) == 128

    sim_student = embedder.cosine_similarity(vec_query, embedder.embed_scheme(sample_schemes[1]))
    sim_farmer = embedder.cosine_similarity(vec_query, embedder.embed_scheme(sample_schemes[0]))
    
    # Query about scholarship should score higher similarity to student scheme than farmer scheme
    assert sim_student > sim_farmer

def test_vector_store_in_memory(sample_schemes):
    store = VectorStore()
    store.build_index(sample_schemes)
    
    results = store.similarity_search("farming income assistance", top_k=2)
    assert len(results) == 2
    top_scheme, top_score = results[0]
    assert top_scheme.id == "SCH-1"
    assert top_score > 0.0

def test_rag_retriever_hybrid_filtering(sample_schemes):
    store = VectorStore()
    store.build_index(sample_schemes)
    
    retriever = RAGRetriever(vector_store=store)
    
    # Profile as Student, SC category, Maharashtra state
    profile = UserProfile(occupation="Student", category="SC", state="Maharashtra")
    candidates = retriever.retrieve_candidates(query="college fee assistance", profile=profile)
    
    assert len(candidates) == 1
    matched_scheme, score = candidates[0]
    assert matched_scheme.id == "SCH-2"
