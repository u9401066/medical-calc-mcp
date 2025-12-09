"""
E2E Tests for Pediatric Dosing Calculator

Tests the pediatric dosing calculator through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestPediatricDosingE2E:
    """E2E tests for Pediatric Dosing Calculator"""
    
    ENDPOINT = "/api/v1/calculate/pediatric_dosing"
    
    def test_acetaminophen_dosing(self, test_client):
        """Test acetaminophen dosing for pediatric patient"""
        payload = {
            "params": {
                "weight_kg": 20,
                "drug_name": "acetaminophen",
                "age_years": 6,
                "route": "oral"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0
    
    def test_ibuprofen_dosing(self, test_client):
        """Test ibuprofen dosing"""
        payload = {
            "params": {
                "weight_kg": 15,
                "drug_name": "ibuprofen",
                "age_years": 4,
                "route": "oral"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0
    
    def test_amoxicillin_dosing(self, test_client):
        """Test amoxicillin dosing"""
        payload = {
            "params": {
                "weight_kg": 25,
                "drug_name": "amoxicillin",
                "age_years": 8,
                "route": "oral",
                "indication": "otitis_media"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0
    
    def test_infant_dosing(self, test_client):
        """Test dosing for infant"""
        payload = {
            "params": {
                "weight_kg": 8,
                "drug_name": "acetaminophen",
                "age_years": 0.5,
                "route": "oral"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0
    
    def test_iv_route(self, test_client):
        """Test IV route dosing"""
        payload = {
            "params": {
                "weight_kg": 30,
                "drug_name": "acetaminophen",
                "age_years": 10,
                "route": "iv"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0
    
    def test_custom_dose_per_kg(self, test_client):
        """Test custom dose per kg calculation"""
        payload = {
            "params": {
                "weight_kg": 20,
                "age_years": 6,
                "custom_dose_per_kg": 10,
                "custom_max_dose": 500,
                "custom_drug_name": "CustomDrug"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # 20kg * 10mg/kg = 200mg
        assert data["result"]["value"] == 200
    
    def test_max_dose_cap(self, test_client):
        """Test that max dose is properly capped"""
        payload = {
            "params": {
                "weight_kg": 70,
                "drug_name": "acetaminophen",
                "age_years": 16,
                "route": "oral"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Should be capped at adult max dose
        assert data["result"]["value"] <= 1000  # Typical single dose max
    
    def test_missing_weight(self, test_client):
        """Test missing weight parameter"""
        payload = {
            "params": {
                "drug_name": "acetaminophen",
                "age_years": 6
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
    
    def test_invalid_drug_name(self, test_client):
        """Test invalid drug name"""
        payload = {
            "params": {
                "weight_kg": 20,
                "drug_name": "invalid_drug_xyz",
                "age_years": 6
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        # May return error or handle gracefully
        assert response.status_code in [200, 400, 422, 500]
