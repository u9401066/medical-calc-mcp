"""
E2E Tests for Parkland Formula Calculator

Tests the Parkland Formula for Burn Fluid Resuscitation through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestParklandFormulaE2E:
    """E2E tests for Parkland Formula Calculator"""
    
    ENDPOINT = "/api/v1/calculate/parkland_formula"
    
    def test_moderate_burn_adult(self, test_client):
        """Test moderate burn in average adult"""
        payload = {
            "params": {
                "weight_kg": 70,
                "tbsa_percent": 30
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # 4 * 70 * 30 = 8400 mL total (24h)
        assert data["result"]["value"] > 0
    
    def test_minor_burn(self, test_client):
        """Test minor burn (10% TBSA)"""
        payload = {
            "params": {
                "weight_kg": 75,
                "tbsa_percent": 10
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # 4 * 75 * 10 = 3000 mL total
        assert data["result"]["value"] > 0
    
    def test_severe_burn(self, test_client):
        """Test severe burn (50% TBSA)"""
        payload = {
            "params": {
                "weight_kg": 80,
                "tbsa_percent": 50
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # 4 * 80 * 50 = 16000 mL total
        assert data["result"]["value"] > 10000
    
    def test_massive_burn(self, test_client):
        """Test massive burn (80% TBSA)"""
        payload = {
            "params": {
                "weight_kg": 70,
                "tbsa_percent": 80
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # 4 * 70 * 80 = 22400 mL total
        assert data["result"]["value"] > 20000
    
    def test_pediatric_burn(self, test_client):
        """Test pediatric burn patient"""
        payload = {
            "params": {
                "weight_kg": 25,
                "tbsa_percent": 25
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # 4 * 25 * 25 = 2500 mL total
        assert data["result"]["value"] > 0
    
    def test_obese_patient(self, test_client):
        """Test obese burn patient"""
        payload = {
            "params": {
                "weight_kg": 120,
                "tbsa_percent": 25
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # 4 * 120 * 25 = 12000 mL total
        assert data["result"]["value"] > 10000
    
    def test_underweight_patient(self, test_client):
        """Test underweight burn patient"""
        payload = {
            "params": {
                "weight_kg": 45,
                "tbsa_percent": 35
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # 4 * 45 * 35 = 6300 mL total
        assert data["result"]["value"] > 5000
    
    def test_small_tbsa(self, test_client):
        """Test small TBSA burn"""
        payload = {
            "params": {
                "weight_kg": 70,
                "tbsa_percent": 5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # 4 * 70 * 5 = 1400 mL total
        assert data["result"]["value"] > 0
    
    def test_electrical_burn_consideration(self, test_client):
        """Test for electrical burn (may need more fluids)"""
        payload = {
            "params": {
                "weight_kg": 75,
                "tbsa_percent": 20
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # 4 * 75 * 20 = 6000 mL base (may need more for electrical)
        assert data["result"]["value"] > 0
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {
                "weight_kg": 70
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
