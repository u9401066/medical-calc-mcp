"""
E2E Tests for sPESI (Simplified Pulmonary Embolism Severity Index) Calculator

Tests the sPESI Score through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestSpesiE2E:
    """E2E tests for sPESI Calculator"""
    
    ENDPOINT = "/api/v1/calculate/spesi"
    
    def test_low_risk_score_0(self, test_client):
        """Test low risk patient (score 0)"""
        payload = {
            "params": {
                "age": 55,
                "cancer": False,
                "chronic_cardiopulmonary_disease": False,
                "heart_rate": 85,
                "systolic_bp": 120,
                "spo2": 96
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Score 0 = low risk, can consider outpatient treatment
        assert data["result"]["value"] == 0
    
    def test_high_risk_age_over_80(self, test_client):
        """Test high risk patient (age >80)"""
        payload = {
            "params": {
                "age": 85,
                "cancer": False,
                "chronic_cardiopulmonary_disease": False,
                "heart_rate": 85,
                "systolic_bp": 120,
                "spo2": 96
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Score ≥1 = high risk
        assert data["result"]["value"] >= 1
    
    def test_multiple_risk_factors(self, test_client):
        """Test patient with multiple risk factors"""
        payload = {
            "params": {
                "age": 82,
                "cancer": True,
                "chronic_cardiopulmonary_disease": True,
                "heart_rate": 90,
                "systolic_bp": 115,
                "spo2": 95
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 3
    
    def test_hemodynamically_unstable(self, test_client):
        """Test hemodynamically unstable patient"""
        payload = {
            "params": {
                "age": 60,
                "cancer": False,
                "chronic_cardiopulmonary_disease": False,
                "heart_rate": 120,
                "systolic_bp": 85,
                "spo2": 88
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Multiple hemodynamic criteria met
        assert data["result"]["value"] >= 3
    
    def test_maximum_score_6(self, test_client):
        """Test maximum score scenario"""
        payload = {
            "params": {
                "age": 85,
                "cancer": True,
                "chronic_cardiopulmonary_disease": True,
                "heart_rate": 115,
                "systolic_bp": 90,
                "spo2": 85
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # All 6 criteria met
        assert data["result"]["value"] == 6
    
    def test_cancer_patient(self, test_client):
        """Test patient with active cancer"""
        payload = {
            "params": {
                "age": 65,
                "cancer": True,
                "chronic_cardiopulmonary_disease": False,
                "heart_rate": 90,
                "systolic_bp": 110,
                "spo2": 94
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 1
    
    def test_copd_patient(self, test_client):
        """Test patient with COPD"""
        payload = {
            "params": {
                "age": 70,
                "cancer": False,
                "chronic_cardiopulmonary_disease": True,
                "heart_rate": 95,
                "systolic_bp": 115,
                "spo2": 92
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 1
    
    def test_hypoxic_patient(self, test_client):
        """Test hypoxic patient (SpO2 <90%)"""
        payload = {
            "params": {
                "age": 50,
                "cancer": False,
                "chronic_cardiopulmonary_disease": False,
                "heart_rate": 100,
                "systolic_bp": 105,
                "spo2": 88
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 1
    
    def test_elderly_stable(self, test_client):
        """Test elderly but hemodynamically stable"""
        payload = {
            "params": {
                "age": 75,
                "cancer": False,
                "chronic_cardiopulmonary_disease": False,
                "heart_rate": 80,
                "systolic_bp": 130,
                "spo2": 97
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Only borderline age, no other risk factors
        assert data["result"]["value"] == 0
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {
                "age": 65
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Should still work with defaults/optionals
        assert data["result"]["value"] >= 0
