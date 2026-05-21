import os
import sys
import unittest
import asyncio

# Adjust path to import app correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.api.routers.schemes import load_schemes_from_json, get_schemes, get_scheme_by_id

class TestSchemesLogic(unittest.TestCase):
    
    def test_json_loading_and_pydantic_parsing(self):
        """Verify that schemes.json exists and all schemes parse into the Pydantic Scheme model."""
        schemes = load_schemes_from_json()
        self.assertGreaterEqual(len(schemes), 5, "Dataset should contain at least 5-10 schemes.")
        
        for scheme in schemes:
            self.assertIsNotNone(scheme.id)
            self.assertIsNotNone(scheme.name)
            self.assertIsNotNone(scheme.description)
            self.assertIsNotNone(scheme.scheme_type)
            self.assertIsNotNone(scheme.target_group)
            self.assertIsNotNone(scheme.education_requirement)
            self.assertIsNotNone(scheme.state)
            self.assertIsNotNone(scheme.category)
            self.assertIsNotNone(scheme.benefits)
            self.assertGreater(len(scheme.eligibility_rules), 0, f"Scheme {scheme.id} must have rules.")
            
            # Check structure of eligibility rules
            for rule in scheme.eligibility_rules:
                self.assertIsNotNone(rule.attribute)
                self.assertIsNotNone(rule.condition)
                self.assertIsNotNone(rule.value)
                self.assertIsNotNone(rule.description)

    def test_router_get_schemes_filtering(self):
        """Test the state filtering logic in the schemes router."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # 1. No filter
            all_schemes = loop.run_until_complete(get_schemes(state=None, limit=10))
            self.assertGreater(len(all_schemes), 0)
            
            # 2. Filter by Karnataka (should return Karnataka + Central schemes)
            karnataka_schemes = loop.run_until_complete(get_schemes(state="Karnataka", limit=10))
            self.assertGreater(len(karnataka_schemes), 0)
            for s in karnataka_schemes:
                self.assertIn(s.state.lower(), ["karnataka", "central"])
                
            # 3. Filter by random state (should return ONLY Central schemes)
            other_schemes = loop.run_until_complete(get_schemes(state="Gujarat", limit=10))
            for s in other_schemes:
                self.assertEqual(s.state.lower(), "central")
        finally:
            loop.close()

    def test_router_get_scheme_by_id(self):
        """Test retrieving a scheme by ID and handling of non-existent IDs."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            all_schemes = load_schemes_from_json()
            first_scheme = all_schemes[0]
            
            # Test success path
            retrieved = loop.run_until_complete(get_scheme_by_id(first_scheme.id))
            self.assertEqual(retrieved.id, first_scheme.id)
            self.assertEqual(retrieved.name, first_scheme.name)
            
            # Test 404 path
            from fastapi import HTTPException
            with self.assertRaises(HTTPException) as context:
                loop.run_until_complete(get_scheme_by_id("SCH-INVALID-ID"))
            self.assertEqual(context.exception.status_code, 404)
        finally:
            loop.close()

if __name__ == "__main__":
    unittest.main()
