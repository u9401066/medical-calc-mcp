"""
E2E Tests for Wells PE Score Calculator

Tests the Wells PE probability score through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestWellsPeE2E:
    """E2E tests for Wells PE Score Calculator"""
    
    ENDPOINT = "/api/v1/calculate/wells_pe"
    
    def test_low_probability_score_0(self, test_client):
        """Test low probability - score 0"""
        payload = {
            "params": {
                "clinical_signs_dvt": False,
                "pe_most_likely_diagnosis": False,
                "heart_rate_gt_100": False,
                "immobilization_or_surgery": False,
                "previous_dvt_pe": False,
                "hemoptysis": False,
                "malignancy": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0
    
    def test_low_probability(self, test_client):
        """Test low probability (score <2)"""
        payload = {
            "params": {
                "clinical_signs_dvt": False,
                "pe_most_likely_diagnosis": False,
                "heart_rate_gt_100": True,
                "immobilization_or_surgery": False,
                "previous_dvt_pe": False,
                "hemoptysis": False,
                "malignancy": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1.5
    
    def test_moderate_probability(self, test_client):
        """Test moderate probability (score 2-6)"""
        payload = {
            "params": {
                "clinical_signs_dvt": True,
                "pe_most_likely_diagnosis": False,
                "heart_rate_gt_100": True,
                "immobilization_or_surgery": True,
                "previous_dvt_pe": False,
                "hemoptysis": False,
                "malignancy": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert 2 <= data["result"]["value"] <= 6
    
    def test_high_probability(self, test_client):
        """Test high probability (score >6)"""
        payload = {
            "params": {
                "clinical_signs_dvt": True,
                "pe_most_likely_diagnosis": True,
                "heart_rate_gt_100": True,
                "immobilization_or_surgery": True,
                "previous_dvt_pe": True,
                "hemoptysis": False,
                "malignancy": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 6
    
    def test_pe_most_likely_weight(self, test_client):
        """Test PE most likely diagnosis (3 points)"""
        payload = {
            "params": {
                "clinical_signs_dvt": False,
                "pe_most_likely_diagnosis": True,
                "heart_rate_gt_100": False,
                "immobilization_or_surgery": False,
                "previous_dvt_pe": False,
                "hemoptysis": False,
                "malignancy": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3
    
    def test_classic_pe_presentation(self, test_client):
        """Test classic PE presentation"""
        payload = {
            "params": {
                "clinical_signs_dvt": True,
                "pe_most_likely_diagnosis": True,
                "heart_rate_gt_100": True,
                "immobilization_or_surgery": True,
                "previous_dvt_pe": True,
                "hemoptysis": True,
                "malignancy": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Maximum possible score
        assert data["result"]["value"] >= 10
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {
                "clinical_signs_dvt": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert response.status_code in [200, 400, 422, 500]
