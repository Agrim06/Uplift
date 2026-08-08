import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.pdf_ingestion_service import PDFIngestionService

MOCK_PDF_GEMINI_RESPONSE = """{
  "id": "SCH-STATE-SMARTFARM",
  "name": "Smart Farmer Solar Pump Subsidy",
  "description": "80% subsidy for installation of solar agricultural pumpsets for farmers.",
  "scheme_type": "Subsidy",
  "target_group": "Farmers",
  "age_limit": "18 - 70 years",
  "income_limit": 500000.0,
  "education_requirement": "No educational bar",
  "occupation": "Farmer",
  "state": "Maharashtra",
  "category": ["General", "OBC", "SC", "ST"],
  "required_documents": ["7/12 Land Extract", "Aadhaar Card", "Electricity Bill", "Bank Details"],
  "benefits": "80% subsidy on 3HP / 5HP / 7.5HP solar pumpsets.",
  "application_link": "https://mahadiscom.in/solar",
  "official_source": "solar_pump_guidelines.pdf",
  "deadline": "2026-12-31",
  "eligibility_rules": [
    {
      "attribute": "state",
      "condition": "equals",
      "value": "Maharashtra",
      "description": "Must be a resident farmer in Maharashtra."
    },
    {
      "attribute": "occupation",
      "condition": "equals",
      "value": "Farmer",
      "description": "Must own agricultural land."
    }
  ]
}"""

@pytest.mark.anyio
async def test_pdf_ingestion_service():
    with patch.object(PDFIngestionService, 'extract_text_from_pdf_bytes', return_value="Smart Farmer Solar Pump Subsidy text..."):
        with patch('google.generativeai.GenerativeModel') as mock_model_cls:
            mock_model_inst = MagicMock()
            mock_model_inst.generate_content.return_value = MagicMock(text=MOCK_PDF_GEMINI_RESPONSE)
            mock_model_cls.return_value = mock_model_inst
            
            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                result = await PDFIngestionService.structure_scheme_from_pdf_text("Dummy PDF content", "solar_pump_guidelines.pdf")
                
                assert result["name"] == "Smart Farmer Solar Pump Subsidy"
                assert result["occupation"] == "Farmer"
                assert result["state"] == "Maharashtra"
                assert result["income_limit"] == 500000.0
                assert len(result["eligibility_rules"]) == 2
