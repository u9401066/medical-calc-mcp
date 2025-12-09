"""
E2E Tests for AIMS65 Score Calculator

Tests the AIMS65 Score for Upper GI Bleeding Mortality through the REST API.

Parameters:
    albumin_lt_3: bool - Albumin < 3 g/dL
    inr_gt_1_5: bool - INR > 1.5
    altered_mental_status: bool - Altered mental status
    sbp_lte_90: bool - Systolic BP ≤ 90 mmHg
    age_gte_65: bool - Age ≥ 65 years
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestAims65E2E:
    """E2E tests for AIMS65 Score Calculator"""
    
    ENDPOINT = "/api/v1/calculate/aims65"
    
    def test_low_risk_score_0(self, test_client):
        """Test low mortality risk (score 0)"""
        payload = {
            "params": {
                "albumin_lt_3": False,
                "inr_gt_1_5": False,
                "altered_mental_status": False,
                "sbp_lte_90": False,
                "age_gte_65": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Score 0 = 0.3% mortality
        assert data["result"]["value"] == 0
    
    def test_score_1(self, test_client):
        """Test score 1 - ~1% mortality"""
        payload = {
            "params": {
                "albumin_lt_3": True,
                "inr_gt_1_5": False,
                "altered_mental_status": False,
                "sbp_lte_90": False,
                "age_gte_65": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1
    
    def test_score_2(self, test_client):
        """Test score 2 - ~3% mortality"""
        payload = {
            "params": {
                "albumin_lt_3": True,
                "inr_gt_1_5": True,
                "altered_mental_status": False,
                "sbp_lte_90": False,
                "age_gte_65": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2
    
    def test_score_3(self, test_client):
        """Test score 3 - ~10% mortality"""
        payload = {
            "params": {
                "albumin_lt_3": True,
                "inr_gt_1_5": True,
                "altered_mental_status": True,
                "sbp_lte_90": False,
                "age_gte_65": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3
    
    def test_score_4(self, test_client):
        """Test score 4 - ~20% mortality"""
        payload = {
            "params": {
                "albumin_lt_3": True,
                "inr_gt_1_5": True,
                "altered_mental_status": True,
                "sbp_lte_90": True,
                "age_gte_65": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4
    
    def test_maximum_score_5(self, test_client):
        """Test maximum score 5 - ~25% mortality"""
        payload = {
            "params": {
                "albumin_lt_3": True,
                "inr_gt_1_5": True,
                "altered_mental_status": True,
                "sbp_lte_90": True,
                "age_gte_65": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 5
    
    def test_elderly_patient_only(self, test_client):
        """Test elderly patient with no other risk factors"""
        payload = {
            "params": {
                "albumin_lt_3": False,
                "inr_gt_1_5": False,
                "altered_mental_status": False,
                "sbp_lte_90": False,
                "age_gte_65": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1
    
    def test_hypotensive_confused(self, test_client):
        """Test hypotensive patient with altered mental status"""
        payload = {
            "params": {
                "albumin_lt_3": False,
                "inr_gt_1_5": False,
                "altered_mental_status": True,
                "sbp_lte_90": True,
                "age_gte_65": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2
    
    def test_coagulopathic_patient(self, test_client):
        """Test coagulopathic patient (elevated INR)"""
        payload = {
            "params": {
                "albumin_lt_3": False,
                "inr_gt_1_5": True,
                "altered_mental_status": False,
                "sbp_lte_90": False,
                "age_gte_65": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {
                "albumin_lt_3": True,
                "inr_gt_1_5": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
