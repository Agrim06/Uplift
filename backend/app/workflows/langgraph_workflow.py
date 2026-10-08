import os
import asyncio
from typing import Annotated, Dict, List, Any, Optional
from typing_extensions import TypedDict

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from app.schemas.user_schema import UserProfile
from app.schemas.scheme_schema import Scheme
from app.rag.retriever import RAGRetriever
from app.services.profile_extractor import ProfileExtractionEngine
from app.services.recommendation_service import EligibilityEvaluator


class UpliftGraphState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    profile: Dict[str, Any]
    missing_fields: List[str]
    candidate_schemes: List[Dict[str, Any]]
    verified_schemes: List[Dict[str, Any]]
    query_text: str
    iteration_count: int
    final_response: str


api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=api_key or "placeholder_key",
    temperature=0.2,
    max_retries=0,
    timeout=5.0
)

rag_retriever = RAGRetriever()
extraction_engine = ProfileExtractionEngine()


async def extractor_node(state: UpliftGraphState) -> Dict[str, Any]:
    latest_message = ""
    if state.get("messages"):
        last_msg = state["messages"][-1]
        latest_message = getattr(last_msg, "content", "") or ""

    current_profile_dict = dict(state.get("profile") or {})
    
    existing_profile = None
    if current_profile_dict:
        try:
            existing_profile = UserProfile(**current_profile_dict)
        except Exception:
            existing_profile = None

    profile_obj, _ = await extraction_engine.extract_profile(
        query=latest_message,
        existing_profile=existing_profile
    )

    updated_profile = profile_obj.model_dump()

    return {
        "profile": updated_profile,
        "query_text": latest_message
    }


async def retriever_node(state: UpliftGraphState) -> Dict[str, Any]:
    profile_dict = state.get("profile", {})
    query = state.get("query_text", "")

    try:
        profile_obj = UserProfile(**profile_dict)
    except Exception:
        profile_obj = UserProfile()

    candidates_with_scores = await asyncio.to_thread(
        rag_retriever.retrieve_candidates,
        query=query,
        profile=profile_obj,
        top_k=15
    )

    candidate_dicts = []
    for scheme, score in candidates_with_scores:
        scheme_data = scheme.model_dump()
        scheme_data["rag_score"] = round(score * 100, 1)
        candidate_dicts.append(scheme_data)

    return {"candidate_schemes": candidate_dicts}


async def evaluator_node(state: UpliftGraphState) -> Dict[str, Any]:
    candidates = state.get("candidate_schemes", [])
    profile_dict = state.get("profile", {})

    try:
        profile_obj = UserProfile(**profile_dict)
    except Exception:
        profile_obj = UserProfile()

    verified = []
    missing_info_set = set()

    for scheme_data in candidates:
        try:
            valid_fields = {k: v for k, v in scheme_data.items() if k in Scheme.model_fields}
            scheme_obj = Scheme(**valid_fields)
            evaluation = EligibilityEvaluator.evaluate_scheme(profile_obj, scheme_obj)

            if evaluation.eligible is True:
                verified.append(scheme_data)
            elif evaluation.eligible == "unknown":
                missing_info_set.update(evaluation.missing_requirements)
        except Exception:
            pass

    if verified:
        missing = []
    else:
        missing = sorted(list(missing_info_set))

    iteration = state.get("iteration_count", 0) + 1
    return {
        "verified_schemes": verified,
        "missing_fields": missing,
        "iteration_count": iteration
    }


async def clarification_node(state: UpliftGraphState) -> Dict[str, Any]:
    missing = state.get("missing_fields", [])
    friendly_field_names = {
        "state": "your home State or UT",
        "occupation": "your current occupation (e.g., student, farmer, self-employed)",
        "income": "your approximate annual family income",
        "category": "your social category (e.g., General, OBC, SC, ST)",
        "education": "your highest education level",
        "gender": "your gender"
    }
    needed = [friendly_field_names.get(f, f) for f in missing[:2]]
    current_profile = state.get("profile", {})

    prompt = f"""
    The citizen wants to find eligible government welfare schemes, but we need more details: {', '.join(needed)}.
    Current profile known so far: {current_profile}
    
    Write a warm, concise 1-2 sentence response asking for this missing information 
    so we can accurately find the right government schemes for them.
    """
    try:
        response = await asyncio.wait_for(llm.ainvoke([HumanMessage(content=prompt)]), timeout=4.0)
        content = response.content
    except Exception:
        content = f"Could you please share {', '.join(needed)} so I can find the best matching welfare schemes for you?"

    return {
        "messages": [AIMessage(content=content)],
        "final_response": content
    }


async def query_rewriter_node(state: UpliftGraphState) -> Dict[str, Any]:
    original_query = state.get("query_text", "")
    profile = state.get("profile", {})

    prompt = f"""
    A search for government schemes with query '{original_query}' returned no eligible matches.
    User profile: {profile}
    
    Generate an expanded, broader alternative search query (under 10 words) to find related welfare programs or financial aid.
    Output ONLY the new query string, nothing else.
    """
    try:
        rewritten = await asyncio.wait_for(llm.ainvoke([HumanMessage(content=prompt)]), timeout=3.0)
        new_query = rewritten.content.strip()
    except Exception:
        new_query = f"government financial assistance welfare {original_query}".strip()

    return {"query_text": new_query}


async def recommender_node(state: UpliftGraphState) -> Dict[str, Any]:
    verified = state.get("verified_schemes", [])
    profile = state.get("profile", {})

    if not verified:
        content = (
            "I could not find exact matching government schemes for your current profile. "
            "Please check if you qualify for general central welfare initiatives or provide more specific details."
        )
    else:
        cleaned_summaries = []
        for s in verified[:4]:
            name = s.get("name", "Scheme")
            desc = s.get("description", "")
            benefits = s.get("benefits", "")
            docs = s.get("required_documents", [])
            
            if not desc or "not available" in desc.lower():
                desc = f"Government welfare program designed to support {s.get('target_group', 'eligible citizens')}."
            if not benefits or "not detailed" in benefits.lower():
                benefits = "Direct subsidies, financial aid, or capacity development support as per government guidelines."
            docs_str = ", ".join(docs) if docs else "Aadhaar Card, Bank Account, Address Proof"
            
            cleaned_summaries.append({
                "name": name,
                "desc": desc,
                "benefits": benefits,
                "docs": docs_str
            })
            
        scheme_summaries = "\n".join([
            f"- **{cs['name']}**: {cs['desc']} (Benefits: {cs['benefits']})"
            for cs in cleaned_summaries
        ])

        prompt = f"""
        You are an expert government welfare advisor.
        User profile: {profile}
        
        Top verified schemes found:
        {scheme_summaries}
        
        Generate a clear, encouraging response:
        1. Summarize the top matching schemes and explain why the user qualifies.
        2. Mention next steps and required documents.
        Keep the response clear, structured with markdown, and supportive.
        """
        try:
            response = await asyncio.wait_for(llm.ainvoke([HumanMessage(content=prompt)]), timeout=5.0)
            content = response.content
        except Exception:
            top_schemes_text = "\n\n".join([
                f"### {cs['name']}\n{cs['desc']}\n- **Benefits**: {cs['benefits']}\n- **Required Documents**: {cs['docs']}"
                for cs in cleaned_summaries[:3]
            ])
            content = (
                f"Based on your profile, here are the top matching government schemes you qualify for:\n\n"
                f"{top_schemes_text}\n\n"
                f"**Next Steps**: Please keep the required documents ready and apply through the official state or national portals."
            )

    return {
        "messages": [AIMessage(content=content)],
        "final_response": content
    }


def route_after_evaluation(state: UpliftGraphState) -> str:
    verified = state.get("verified_schemes", [])
    missing = state.get("missing_fields", [])
    iteration = state.get("iteration_count", 0)

    if not verified and len(missing) >= 3:
        return "clarification"
    if not verified and iteration < 2:
        return "rewriter"
    return "recommender"


def create_uplift_graph():
    workflow = StateGraph(UpliftGraphState)

    workflow.add_node("extractor", extractor_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("clarification", clarification_node)
    workflow.add_node("rewriter", query_rewriter_node)
    workflow.add_node("recommender", recommender_node)

    workflow.add_edge(START, "extractor")
    workflow.add_edge("extractor", "retriever")
    workflow.add_edge("retriever", "evaluator")

    workflow.add_conditional_edges(
        "evaluator",
        route_after_evaluation,
        {
            "clarification": "clarification",
            "rewriter": "rewriter",
            "recommender": "recommender"
        }
    )

    workflow.add_edge("rewriter", "retriever")
    workflow.add_edge("clarification", END)
    workflow.add_edge("recommender", END)

    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)


uplift_agent = create_uplift_graph()


async def run_langgraph_workflow(
    message: str,
    thread_id: str = "default_session",
    existing_profile: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    config = {"configurable": {"thread_id": thread_id}}

    initial_input = {
        "messages": [HumanMessage(content=message)],
        "profile": existing_profile or {},
        "missing_fields": [],
        "candidate_schemes": [],
        "verified_schemes": [],
        "query_text": message,
        "iteration_count": 0,
        "final_response": ""
    }

    result = await uplift_agent.ainvoke(initial_input, config=config)

    missing = result.get("missing_fields", [])
    is_clarification = len(result.get("verified_schemes", [])) == 0 and len(missing) > 0
    status = "clarification" if is_clarification else "success"

    return {
        "response": result.get("final_response", ""),
        "profile": result.get("profile", {}),
        "missing_fields": missing,
        "verified_schemes": result.get("verified_schemes", []),
        "status": status,
        "thread_id": thread_id
    }