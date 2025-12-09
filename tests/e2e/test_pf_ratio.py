"""
E2E Tests for P/F Ratio Calculator

Tests the PaO2/FiO2 ratio calculator through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestPfRatioE2E:
    """E2E tests for P/F Ratio Calculator"""
    
    ENDPOINT = "/api/v1/calculate/pf_ratio"
    
    def test_normal_pf_ratio(self, test_client):
        """Test normal P/F ratio (>400)"""
        payload = {
            "params": {
                "pao2": 95,
                "fio2": 0.21
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # P/F = 95/0.21 = ~452
        assert data["result"]["value"] > 400
    
    def test_mild_ards(self, test_client):
        """Test mild ARDS (P/F 200-300)"""
        payload = {
            "params": {
                "pao2": 100,
                "fio2": 0.40
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # P/F = 100/0.40 = 250
        assert 200 <= data["result"]["value"] <= 300
    
    def test_moderate_ards(self, test_client):
        """Test moderate ARDS (P/F 100-200)"""
        payload = {
            "params": {
                "pao2": 80,
                "fio2": 0.60
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # P/F = 80/0.60 = ~133
        assert 100 <= data["result"]["value"] <= 200
    
    def test_severe_ards(self, test_client):
        """Test severe ARDS (P/F <100)"""
        payload = {
            "params": {
                "pao2": 55,
                "fio2": 1.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # P/F = 55/1.0 = 55
        assert data["result"]["value"] < 100
    
    def test_with_peep(self, test_client):
        """Test with PEEP level (Berlin criteria require PEEP ≥5)"""
        payload = {
            "params": {
                "pao2": 75,
                "fio2": 0.50,
                "peep": 10
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0
    
    def test_on_mechanical_ventilation(self, test_client):
        """Test mechanically ventilated patient"""
        payload = {
            "params": {
                "pao2": 60,
                "fio2": 0.80,
                "on_mechanical_ventilation": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # P/F = 60/0.80 = 75
        assert data["result"]["value"] < 100
    
    def test_high_fio2_good_pao2(self, test_client):
        """Test high FiO2 with good PaO2"""
        payload = {
            "params": {
                "pao2": 250,
                "fio2": 0.60
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # P/F = 250/0.60 = ~417
        assert data["result"]["value"] > 400
    
    def test_room_air_hypoxemia(self, test_client):
        """Test hypoxemia on room air"""
        payload = {
            "params": {
                "pao2": 55,
                "fio2": 0.21
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # P/F = 55/0.21 = ~262
        assert data["result"]["value"] < 300
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {
                "pao2": 95
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
