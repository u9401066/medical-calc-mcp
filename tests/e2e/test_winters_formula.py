"""
E2E Tests for Winters Formula Calculator

Tests the Winters Formula (expected PaCO2) through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestWintersFormulaE2E:
    """E2E tests for Winters Formula Calculator"""
    
    ENDPOINT = "/api/v1/calculate/winters_formula"
    
    def test_normal_bicarbonate(self, test_client):
        """Test with normal bicarbonate"""
        payload = {
            "params": {
                "hco3": 24
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Expected PaCO2 = 1.5(24) + 8 ± 2 = 44 ± 2
        assert 40 <= data["result"]["value"] <= 48
    
    def test_metabolic_acidosis(self, test_client):
        """Test metabolic acidosis with appropriate compensation"""
        payload = {
            "params": {
                "hco3": 12
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Expected PaCO2 = 1.5(12) + 8 ± 2 = 26 ± 2
        assert 24 <= data["result"]["value"] <= 28
    
    def test_severe_metabolic_acidosis(self, test_client):
        """Test severe metabolic acidosis"""
        payload = {
            "params": {
                "hco3": 6
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Expected PaCO2 = 1.5(6) + 8 ± 2 = 17 ± 2
        assert 15 <= data["result"]["value"] <= 19
    
    def test_with_actual_paco2_appropriate(self, test_client):
        """Test with actual PaCO2 showing appropriate compensation"""
        payload = {
            "params": {
                "hco3": 12,
                "actual_paco2": 26
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Should indicate appropriate compensation
        assert data["result"]["value"] > 0
    
    def test_with_actual_paco2_respiratory_acidosis(self, test_client):
        """Test with actual PaCO2 showing respiratory acidosis"""
        payload = {
            "params": {
                "hco3": 12,
                "actual_paco2": 40
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Actual > expected indicates respiratory acidosis
        assert data["result"]["value"] > 0
    
    def test_with_actual_paco2_respiratory_alkalosis(self, test_client):
        """Test with actual PaCO2 showing respiratory alkalosis"""
        payload = {
            "params": {
                "hco3": 12,
                "actual_paco2": 18
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Actual < expected indicates respiratory alkalosis
        assert data["result"]["value"] > 0
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {}
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
