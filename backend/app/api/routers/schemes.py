from typing import List
from fastapi import APIRouter, Query
from app.schemas.scheme_schema import Scheme

router= APIRouter()

@router.get("/", response_model = List[Scheme],  summary="List all government schemes")
async def get_schemes(
    state: str = Query(None, description="Filter schemes by state"),
    limit: int = Query(10, description="Maximum number of schemes to return")
):

    #Future query for database mock data for testing

    mock_scheme = Scheme(
        scheme_id="SCH-001",
        scheme_name="Post Matric Scholarship",
        description="Scholarship for students pursuing higher education.",
        income_limit=250000.0,
        age_limit_min=18,
        age_limit_max=None,
        state_restriction="Karnataka",
        eligibility_criteria=["Must be a resident of Karnataka", "Must be pursuing a degree"],
        required_documents=["Aadhar Card", "Income Certificate", "Bonafide Certificate"],
        benefits=["Financial assistance for tuition fees"],
        official_link=None,
        deadline=None
    )

    if state and state.lower() != "karnataka":
        return []
    return [mock_scheme]


@router.get("/{scheme_id}", response_model=Scheme, summary="Get Specific scheme details")
async def get_scheme_by_id(scheme_id:str):
    #return it from db in future
    pass