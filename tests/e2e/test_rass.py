"""
E2E Tests for RASS (Richmond Agitation-Sedation Scale) Calculator

Tests the RASS sedation scale through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestRassE2E:
    """E2E tests for RASS Calculator"""
    
    ENDPOINT = "/api/v1/calculate/rass"
    
    def test_combative(self, test_client):
        """Test RASS +4 - Combative"""
        payload = {
            "params": {
                "rass_score": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4
    
    def test_very_agitated(self, test_client):
        """Test RASS +3 - Very agitated"""
        payload = {
            "params": {
                "rass_score": 3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3
    
    def test_agitated(self, test_client):
        """Test RASS +2 - Agitated"""
        payload = {
            "params": {
                "rass_score": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2
    
    def test_restless(self, test_client):
        """Test RASS +1 - Restless"""
        payload = {
            "params": {
                "rass_score": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1
    
    def test_alert_calm(self, test_client):
        """Test RASS 0 - Alert and calm"""
        payload = {
            "params": {
                "rass_score": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0
    
    def test_drowsy(self, test_client):
        """Test RASS -1 - Drowsy"""
        payload = {
            "params": {
                "rass_score": -1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == -1
    
    def test_light_sedation(self, test_client):
        """Test RASS -2 - Light sedation"""
        payload = {
            "params": {
                "rass_score": -2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == -2
    
    def test_moderate_sedation(self, test_client):
        """Test RASS -3 - Moderate sedation"""
        payload = {
            "params": {
                "rass_score": -3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == -3
    
    def test_deep_sedation(self, test_client):
        """Test RASS -4 - Deep sedation"""
        payload = {
            "params": {
                "rass_score": -4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == -4
    
    def test_unarousable(self, test_client):
        """Test RASS -5 - Unarousable"""
        payload = {
            "params": {
                "rass_score": -5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == -5
    
    def test_invalid_score_too_high(self, test_client):
        """Test invalid score (too high)"""
        payload = {
            "params": {
                "rass_score": 5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
    
    def test_invalid_score_too_low(self, test_client):
        """Test invalid score (too low)"""
        payload = {
            "params": {
                "rass_score": -6
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {}
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
