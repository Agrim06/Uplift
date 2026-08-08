import os
import json
import re
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from app.schemas.scheme_schema import Scheme
from app.services.scheme_service import SCHEMES_FILE_PATH

class SchemeScraperService:
    """
    Automated Web Scraper & AI Structuring Service.
    Downloads webpage content from official government portals or URLs,
    extracts plain text, uses Gemini LLM to map attributes into Scheme JSON models,
    and updates the schemes database automatically.
    """

    @staticmethod
    async def fetch_webpage_text(url: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove noisy tags (scripts, styles, navbars, footers)
        for tag in soup(["script", "style", "nav", "footer", "header", "svg"]):
            tag.decompose()

        plain_text = soup.get_text(separator="\n", strip=True)
        # Limit text length to fit context cleanly
        return plain_text[:6000]

    @classmethod
    async def scrape_and_structure_scheme(cls, url: str) -> Dict[str, Any]:
        raw_text = await cls.fetch_webpage_text(url)
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing. Cannot run AI structuring.")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = f"""
        You are an expert government scheme data extraction AI.
        Analyze this scraped webpage content from an official government scheme portal and structure it into a JSON object matching our strict schema.

        Webpage Source URL: "{url}"
        Raw Webpage Text:
        ---
        {raw_text}
        ---

        Return ONLY a JSON object with these exact keys:
        - "id": a unique slug ID starting with "SCH-" (e.g., "SCH-CENTRAL-XYZ" or "SCH-MAH-ABC")
        - "name": full official scheme name
        - "description": clear summary of what the scheme offers
        - "scheme_type": category (e.g. "Scholarship", "Welfare", "Business Loan", "Subsidy")
        - "target_group": target audience (e.g. "Students", "Farmers", "Women", "Artisans")
        - "age_limit": age constraints as descriptive string (e.g. "18 - 35 years" or "No age limit")
        - "income_limit": maximum annual family income limit in INR as a float (e.g. 250000.0), or null if none
        - "education_requirement": educational criteria string
        - "occupation": primary target occupation (e.g. "Student", "Farmer", "Entrepreneur", "Artisan", "Self-Employed")
        - "state": state name (e.g. "Maharashtra", "Karnataka", "Delhi", "Uttar Pradesh") or "Central" for pan-India schemes
        - "category": array of allowed social categories, e.g. ["General", "OBC", "SC", "ST"]
        - "required_documents": array of document names required to apply (e.g. ["Aadhaar Card", "Income Certificate"])
        - "benefits": concise description of financial/non-financial benefits
        - "application_link": official URL where users can apply online (look for links on page or default to official portal)
        - "official_source": "{url}"
        - "deadline": application deadline date string (e.g. "2026-12-31") or "Ongoing"
        - "eligibility_rules": array of objects, each containing:
            - "attribute": user attribute name ("income", "state", "occupation", "category", "education", "gender")
            - "condition": comparison condition ("equals", "lte", "gte", "in")
            - "value": rule value (float, string, or list of strings)
            - "description": human-friendly rule description
        """

        response = model.generate_content(prompt)
        scheme_data = json.loads(response.text)

        # Enforce official source URL
        scheme_data["official_source"] = url
        if not scheme_data.get("application_link"):
            scheme_data["application_link"] = url

        return scheme_data

    @classmethod
    async def save_scheme_to_database(cls, scheme_input: Any) -> Any:
        # Handle dict, list, or envelope {"schemes": [...]}
        items_to_save = []
        if isinstance(scheme_input, list):
            items_to_save = scheme_input
        elif isinstance(scheme_input, dict):
            if "schemes" in scheme_input and isinstance(scheme_input["schemes"], list):
                items_to_save = scheme_input["schemes"]
            else:
                items_to_save = [scheme_input]

        validated_schemes = []
        for item in items_to_save:
            try:
                validated_schemes.append(Scheme(**item))
            except Exception as e:
                print(f"Skipping invalid scheme item: {e}")

        if not validated_schemes:
            raise ValueError("No valid scheme items could be parsed from input.")

        # Load existing database file
        existing_schemes = []
        if os.path.exists(SCHEMES_FILE_PATH):
            with open(SCHEMES_FILE_PATH, "r", encoding="utf-8") as f:
                try:
                    existing_schemes = json.load(f)
                except Exception:
                    existing_schemes = []

        saved_list = []
        for validated_scheme in validated_schemes:
            updated = False
            for idx, item in enumerate(existing_schemes):
                if item.get("id") == validated_scheme.id or item.get("name").strip().lower() == validated_scheme.name.strip().lower():
                    existing_schemes[idx] = validated_scheme.model_dump()
                    updated = True
                    break

            if not updated:
                existing_schemes.append(validated_scheme.model_dump())
            saved_list.append(validated_scheme)

        # Save back to schemes.json
        with open(SCHEMES_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(existing_schemes, f, indent=2, ensure_ascii=False)

        return saved_list[0] if len(saved_list) == 1 else saved_list

    @classmethod
    async def scrape_and_ingest(cls, url: str) -> Any:
        """Full pipeline: Scrapes URL -> AI Structures -> Saves to database."""
        scheme_dict = await cls.scrape_and_structure_scheme(url)
        saved_scheme = await cls.save_scheme_to_database(scheme_dict)
        return saved_scheme
