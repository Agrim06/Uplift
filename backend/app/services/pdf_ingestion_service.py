import os
import json
import io
from typing import Dict, Any, List
import pypdf
import google.generativeai as genai
from app.schemas.scheme_schema import Scheme
from app.services.scheme_scraper import SchemeScraperService

class PDFIngestionService:
    """
    Service to ingest government scheme guideline PDFs.
    Extracts text from PDF documents using pypdf, uses Gemini LLM to extract
    structured metadata & eligibility rules, and updates the schemes database.
    """

    @staticmethod
    def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
        """Extracts text content from raw PDF bytes."""
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        extracted_pages = []
        for idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_pages.append(text)
        
        full_text = "\n".join(extracted_pages)
        # Limit text size to stay comfortably within LLM context
        return full_text[:8000]

    @classmethod
    async def structure_scheme_from_pdf_text(cls, pdf_text: str, filename: str = "document.pdf") -> Dict[str, Any]:
        """Uses Gemini 2.5 Flash to convert raw PDF text into a structured Scheme model."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = f"""
        You are an expert government scheme data extraction AI.
        Analyze the extracted text from an official government scheme PDF document ("{filename}").
        
        If the document contains MULTIPLE schemes, return a JSON array of scheme objects: [ {{...}}, {{...}} ].
        If the document contains a SINGLE scheme, return a JSON array containing 1 scheme object: [ {{...}} ].

        PDF Content Text:
        ---
        {pdf_text}
        ---

        Each scheme object in the array must contain these exact keys:
        - "id": a unique slug ID starting with "SCH-" (e.g., "SCH-CENTRAL-XYZ" or "SCH-STATE-ABC")
        - "name": full official scheme name mentioned in the PDF
        - "description": clear summary of what the scheme offers
        - "scheme_type": category (e.g. "Scholarship", "Welfare", "Business Loan", "Subsidy", "Grant")
        - "target_group": target audience (e.g. "Students", "Farmers", "Women", "Artisans", "Entrepreneurs")
        - "age_limit": age constraints string (e.g. "18 - 35 years" or "No age limit")
        - "income_limit": maximum annual family income limit in INR as a float (e.g. 250000.0), or null if none
        - "education_requirement": educational qualification string
        - "occupation": primary target occupation (e.g. "Student", "Farmer", "Entrepreneur", "Artisan", "Self-Employed")
        - "state": state name (e.g. "Maharashtra", "Karnataka", "Delhi", "Uttar Pradesh") or "Central" for pan-India schemes
        - "category": array of allowed social categories, e.g. ["General", "OBC", "SC", "ST"]
        - "required_documents": array of document names required to apply
        - "benefits": concise description of financial/non-financial benefits
        - "application_link": official URL or portal mentioned in document for applying (e.g. "https://scholarships.gov.in/")
        - "official_source": filename or portal reference
        - "deadline": application deadline date string (e.g. "2026-12-31") or "Ongoing"
        - "eligibility_rules": array of objects, each containing:
            - "attribute": user attribute name ("income", "state", "occupation", "category", "education", "gender")
            - "condition": comparison condition ("equals", "lte", "gte", "in")
            - "value": rule value (float, string, or list of strings)
            - "description": human-friendly rule description
        """

        # Retry loop for Gemini API with backoff; fallback to heuristic parser if quota exceeded
        for attempt in range(2):
            try:
                response = model.generate_content(prompt)
                scheme_data = json.loads(response.text)
                return scheme_data
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower() or "rate" in err_str.lower():
                    import time
                    print(f"Gemini quota/rate limit encountered (Attempt {attempt+1}/2). Waiting 3s...")
                    time.sleep(3)
                else:
                    print(f"Gemini API error: {err_str}")
                    break

        print("Executing heuristic fallback extractor for PDF text chunk...")
        return cls._heuristic_pdf_extract(pdf_text, filename)

    @classmethod
    def _heuristic_pdf_extract(cls, pdf_text: str, filename: str) -> List[Dict[str, Any]]:
        import re
        schemes = []
        pattern = r'(?:\n|^)(\d+\.\d+)\s+([A-Z0-9\s\-\(\)\.\,\/]{4,80})(?=\n|\:)'
        matches = list(re.finditer(pattern, pdf_text))
        
        if not matches:
            slug = re.sub(r'[^A-Z0-9]', '', filename.upper())[:15]
            return [{
                "id": f"SCH-CENTRAL-{slug}",
                "name": f"Government Scheme ({filename})",
                "description": pdf_text[:300].strip(),
                "scheme_type": "Welfare",
                "target_group": "General Public",
                "age_limit": "No age limit",
                "income_limit": None,
                "education_requirement": "None",
                "occupation": "General",
                "state": "Central",
                "category": ["General", "OBC", "SC", "ST"],
                "required_documents": ["Aadhaar Card", "Bank Account Details"],
                "benefits": "Financial and welfare assistance as per government guidelines.",
                "application_link": "https://myscheme.gov.in/",
                "official_source": filename,
                "deadline": "Ongoing",
                "eligibility_rules": []
            }]

        for i, match in enumerate(matches):
            raw_title = match.group(2).strip()
            slug = re.sub(r'[^A-Z0-9]', '', raw_title)[:16]
            
            start_pos = match.end()
            end_pos = matches[i+1].start() if i + 1 < len(matches) else len(pdf_text)
            body = pdf_text[start_pos:end_pos].strip()
            
            state = "Central"
            for st in ["Maharashtra", "Karnataka", "Tamil Nadu", "Delhi", "Gujarat", "Uttar Pradesh", "Bihar"]:
                if st.lower() in body.lower():
                    state = st
                    break

            occupation = "General"
            if "student" in body.lower() or "scholarship" in body.lower():
                occupation = "Student"
            elif "farmer" in body.lower() or "krishi" in body.lower() or "agriculture" in body.lower():
                occupation = "Farmer"
            elif "women" in body.lower() or "girl" in body.lower() or "female" in body.lower():
                occupation = "Self-Employed"

            income_limit = None
            inc_m = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lakhs)', body.lower())
            if inc_m:
                income_limit = float(inc_m.group(1)) * 100000.0

            rules = [
                {
                    "attribute": "occupation",
                    "condition": "equals",
                    "value": occupation,
                    "description": f"Target occupation: {occupation}"
                },
                {
                    "attribute": "state",
                    "condition": "in",
                    "value": [state, "Central", "Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Gujarat", "Uttar Pradesh"],
                    "description": f"State residence must be {state} or Central."
                }
            ]
            if income_limit:
                rules.append({
                    "attribute": "income",
                    "condition": "lte",
                    "value": income_limit,
                    "description": f"Annual income limit: INR {income_limit}"
                })

            schemes.append({
                "id": f"SCH-{slug}",
                "name": raw_title.title(),
                "description": body[:250] if body else f"Official government scheme: {raw_title}",
                "scheme_type": "Welfare",
                "target_group": "Eligible Citizens",
                "age_limit": "No age limit",
                "income_limit": income_limit,
                "education_requirement": "As specified in guidelines",
                "occupation": occupation,
                "state": state,
                "category": ["General", "OBC", "SC", "ST"],
                "required_documents": ["Aadhaar Card", "Bank Details"],
                "benefits": body[:200] if body else "Financial support and benefits as outlined in official guidelines.",
                "application_link": "https://myscheme.gov.in/",
                "official_source": filename,
                "deadline": "Ongoing",
                "eligibility_rules": rules
            })

        return schemes

    @classmethod
    async def ingest_pdf_bytes(cls, pdf_bytes: bytes, filename: str = "document.pdf") -> Any:
        """Full pipeline: PDF bytes -> Text -> AI Structuring -> Save to Database."""
        pdf_text = cls.extract_text_from_pdf_bytes(pdf_bytes)
        if not pdf_text.strip():
            raise ValueError(f"Could not extract readable text from PDF: {filename}")
            
        scheme_data = await cls.structure_scheme_from_pdf_text(pdf_text, filename)
        saved_schemes = await SchemeScraperService.save_scheme_to_database(scheme_data)
        return saved_schemes

    @classmethod
    async def ingest_pdf_file(cls, file_path: str) -> Any:
        """Ingests a PDF file from a local disk filepath."""
        filename = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
        return await cls.ingest_pdf_bytes(pdf_bytes, filename)
