"""
E2E Tests for Mallampati Score Calculator

Tests the Mallampati airway classification through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestMallampatiScoreE2E:
    """E2E tests for Mallampati Score Calculator"""
    
    ENDPOINT = "/api/v1/calculate/mallampati_score"
    
    def test_mallampati_class_1(self, test_client):
        """Test Mallampati Class 1 - Easy intubation"""
        payload = {
            "params": {
                "mallampati_class": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1
    
    def test_mallampati_class_2(self, test_client):
        """Test Mallampati Class 2"""
        payload = {
            "params": {
                "mallampati_class": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2
    
    def test_mallampati_class_3(self, test_client):
        """Test Mallampati Class 3 - Difficult intubation likely"""
        payload = {
            "params": {
                "mallampati_class": 3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3
    
    def test_mallampati_class_4(self, test_client):
        """Test Mallampati Class 4 - Most difficult intubation"""
        payload = {
            "params": {
                "mallampati_class": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4
    
    def test_invalid_class_too_low(self, test_client):
        """Test invalid class (too low)"""
        payload = {
            "params": {
                "mallampati_class": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
    
    def test_invalid_class_too_high(self, test_client):
        """Test invalid class (too high)"""
        payload = {
            "params": {
                "mallampati_class": 5
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
