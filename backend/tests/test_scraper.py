import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.scheme_scraper import SchemeScraperService
from app.schemas.scheme_schema import Scheme

MOCK_HTML = """
<html>
<body>
<h1>National Fellowship for Higher Education</h1>
<p>Provides financial assistance to SC students for pursuing M.Phil and Ph.D. courses.</p>
<p>Income limit: Annual family income must be below Rs 6,00,000.</p>
<a href="https://scholarships.gov.in/">Apply at National Scholarship Portal</a>
</body>
</html>
"""

MOCK_GEMINI_RESPONSE = """{
  "id": "SCH-CENTRAL-NFHE",
  "name": "National Fellowship for Higher Education",
  "description": "Financial assistance to SC students for pursuing M.Phil and Ph.D.",
  "scheme_type": "Scholarship",
  "target_group": "SC Higher Education Students",
  "age_limit": "No age limit",
  "income_limit": 600000.0,
  "education_requirement": "Postgraduate completed, pursuing M.Phil / Ph.D.",
  "occupation": "Student",
  "state": "Central",
  "category": ["SC"],
  "required_documents": ["Aadhaar Card", "Income Certificate", "Caste Certificate"],
  "benefits": "Monthly stipend and contingency grant.",
  "application_link": "https://scholarships.gov.in/",
  "official_source": "https://example.gov.in/nfhe",
  "deadline": "2026-12-31",
  "eligibility_rules": [
    {
      "attribute": "category",
      "condition": "equals",
      "value": "SC",
      "description": "Must belong to SC category."
    },
    {
      "attribute": "income",
      "condition": "lte",
      "value": 600000.0,
      "description": "Annual income must not exceed Rs. 6,00,000."
    }
  ]
}"""

@pytest.mark.anyio
async def test_scraper_service():
    with patch.object(SchemeScraperService, 'fetch_webpage_text', return_value="National Fellowship for Higher Education text..."):
        with patch('google.generativeai.GenerativeModel') as mock_model_cls:
            mock_model_inst = MagicMock()
            mock_model_inst.generate_content.return_value = MagicMock(text=MOCK_GEMINI_RESPONSE)
            mock_model_cls.return_value = mock_model_inst
            
            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                result = await SchemeScraperService.scrape_and_structure_scheme("https://example.gov.in/nfhe")
                
                assert result["name"] == "National Fellowship for Higher Education"
                assert result["income_limit"] == 600000.0
                assert result["official_source"] == "https://example.gov.in/nfhe"
                assert result["application_link"] == "https://scholarships.gov.in/"
                assert len(result["eligibility_rules"]) == 2
