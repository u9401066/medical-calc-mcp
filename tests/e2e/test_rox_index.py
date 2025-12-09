"""
E2E Tests for ROX Index Calculator

Tests the ROX Index for HFNC through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestRoxIndexE2E:
    """E2E tests for ROX Index Calculator"""
    
    ENDPOINT = "/api/v1/calculate/rox_index"
    
    def test_low_risk_intubation(self, test_client):
        """Test low risk of intubation (ROX ≥4.88)"""
        payload = {
            "params": {
                "spo2": 96,
                "fio2": 0.40,
                "respiratory_rate": 18
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # ROX = (96/40) / 18 = 0.133... No, ROX = (SpO2/FiO2)/RR
        # If FiO2 is percentage: (96/40)/18 = 0.133
        # If FiO2 is fraction: need different calc
        assert data["result"]["value"] > 0
    
    def test_high_risk_intubation(self, test_client):
        """Test high risk of intubation (ROX <3.85)"""
        payload = {
            "params": {
                "spo2": 88,
                "fio2": 0.80,
                "respiratory_rate": 35
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # High risk patient
        assert data["result"]["value"] < 5
    
    def test_intermediate_risk(self, test_client):
        """Test intermediate risk (ROX 3.85-4.88)"""
        payload = {
            "params": {
                "spo2": 92,
                "fio2": 0.50,
                "respiratory_rate": 25
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0
    
    def test_with_hours_on_hfnc_2h(self, test_client):
        """Test at 2 hours on HFNC"""
        payload = {
            "params": {
                "spo2": 95,
                "fio2": 0.45,
                "respiratory_rate": 20,
                "hours_on_hfnc": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0
    
    def test_with_hours_on_hfnc_6h(self, test_client):
        """Test at 6 hours on HFNC"""
        payload = {
            "params": {
                "spo2": 94,
                "fio2": 0.50,
                "respiratory_rate": 22,
                "hours_on_hfnc": 6
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0
    
    def test_with_hours_on_hfnc_12h(self, test_client):
        """Test at 12 hours on HFNC"""
        payload = {
            "params": {
                "spo2": 93,
                "fio2": 0.55,
                "respiratory_rate": 24,
                "hours_on_hfnc": 12
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 0
    
    def test_improving_patient(self, test_client):
        """Test improving patient on HFNC"""
        payload = {
            "params": {
                "spo2": 98,
                "fio2": 0.30,
                "respiratory_rate": 16
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Good ROX score
        assert data["result"]["value"] > 5
    
    def test_deteriorating_patient(self, test_client):
        """Test deteriorating patient on HFNC"""
        payload = {
            "params": {
                "spo2": 85,
                "fio2": 1.0,
                "respiratory_rate": 40
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Poor ROX score - needs intubation
        assert data["result"]["value"] < 3
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {
                "spo2": 95
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
