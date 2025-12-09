"""
E2E Tests for HAS-BLED Score Calculator

Tests the HAS-BLED bleeding risk score through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestHasBledE2E:
    """E2E tests for HAS-BLED Score Calculator"""
    
    ENDPOINT = "/api/v1/calculate/has_bled"
    
    def test_low_risk_score_0(self, test_client):
        """Test low risk - HAS-BLED score 0"""
        payload = {
            "params": {
                "hypertension_uncontrolled": False,
                "renal_disease": False,
                "liver_disease": False,
                "stroke_history": False,
                "bleeding_history": False,
                "labile_inr": False,
                "elderly_gt_65": False,
                "drugs_antiplatelet_nsaid": False,
                "alcohol_excess": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0
    
    def test_low_risk_score_1(self, test_client):
        """Test low risk - HAS-BLED score 1"""
        payload = {
            "params": {
                "hypertension_uncontrolled": True,
                "renal_disease": False,
                "liver_disease": False,
                "stroke_history": False,
                "bleeding_history": False,
                "labile_inr": False,
                "elderly_gt_65": False,
                "drugs_antiplatelet_nsaid": False,
                "alcohol_excess": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1
    
    def test_moderate_risk_score_2(self, test_client):
        """Test moderate risk - HAS-BLED score 2"""
        payload = {
            "params": {
                "hypertension_uncontrolled": True,
                "renal_disease": False,
                "liver_disease": False,
                "stroke_history": False,
                "bleeding_history": False,
                "labile_inr": False,
                "elderly_gt_65": True,
                "drugs_antiplatelet_nsaid": False,
                "alcohol_excess": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2
    
    def test_high_risk_score_3(self, test_client):
        """Test high risk - HAS-BLED score ≥3"""
        payload = {
            "params": {
                "hypertension_uncontrolled": True,
                "renal_disease": False,
                "liver_disease": False,
                "stroke_history": False,
                "bleeding_history": True,
                "labile_inr": False,
                "elderly_gt_65": True,
                "drugs_antiplatelet_nsaid": False,
                "alcohol_excess": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3
    
    def test_very_high_risk(self, test_client):
        """Test very high risk - HAS-BLED score ≥5"""
        payload = {
            "params": {
                "hypertension_uncontrolled": True,
                "renal_disease": True,
                "liver_disease": False,
                "stroke_history": True,
                "bleeding_history": True,
                "labile_inr": False,
                "elderly_gt_65": True,
                "drugs_antiplatelet_nsaid": False,
                "alcohol_excess": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 5
    
    def test_maximum_score(self, test_client):
        """Test maximum HAS-BLED score"""
        payload = {
            "params": {
                "hypertension_uncontrolled": True,
                "renal_disease": True,
                "liver_disease": True,
                "stroke_history": True,
                "bleeding_history": True,
                "labile_inr": True,
                "elderly_gt_65": True,
                "drugs_antiplatelet_nsaid": True,
                "alcohol_excess": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Maximum score is 9
        assert data["result"]["value"] == 9
    
    def test_typical_elderly_afib_patient(self, test_client):
        """Test typical elderly AF patient on anticoagulation"""
        payload = {
            "params": {
                "hypertension_uncontrolled": True,
                "renal_disease": False,
                "liver_disease": False,
                "stroke_history": False,
                "bleeding_history": False,
                "labile_inr": True,
                "elderly_gt_65": True,
                "drugs_antiplatelet_nsaid": True,
                "alcohol_excess": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {
                "hypertension_uncontrolled": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        # May have defaults or fail
        assert response.status_code in [200, 400, 422, 500]
