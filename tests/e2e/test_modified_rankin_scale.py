"""
E2E Tests for Modified Rankin Scale (mRS) Calculator

Tests the Modified Rankin Scale for Functional Outcome through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestModifiedRankinScaleE2E:
    """E2E tests for Modified Rankin Scale Calculator"""
    
    ENDPOINT = "/api/v1/calculate/modified_rankin_scale"
    
    def test_score_0_no_symptoms(self, test_client):
        """Test mRS 0 - No symptoms at all"""
        payload = {
            "params": {
                "mrs_score": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0
    
    def test_score_1_no_significant_disability(self, test_client):
        """Test mRS 1 - No significant disability despite symptoms"""
        payload = {
            "params": {
                "mrs_score": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1
    
    def test_score_2_slight_disability(self, test_client):
        """Test mRS 2 - Slight disability"""
        payload = {
            "params": {
                "mrs_score": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2
    
    def test_score_3_moderate_disability(self, test_client):
        """Test mRS 3 - Moderate disability"""
        payload = {
            "params": {
                "mrs_score": 3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3
    
    def test_score_4_moderately_severe_disability(self, test_client):
        """Test mRS 4 - Moderately severe disability"""
        payload = {
            "params": {
                "mrs_score": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4
    
    def test_score_5_severe_disability(self, test_client):
        """Test mRS 5 - Severe disability"""
        payload = {
            "params": {
                "mrs_score": 5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 5
    
    def test_score_6_dead(self, test_client):
        """Test mRS 6 - Dead"""
        payload = {
            "params": {
                "mrs_score": 6
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 6
    
    def test_favorable_outcome_threshold(self, test_client):
        """Test favorable outcome (mRS 0-2)"""
        # mRS 2 is typically the threshold for favorable outcome
        payload = {
            "params": {
                "mrs_score": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] <= 2
    
    def test_unfavorable_outcome(self, test_client):
        """Test unfavorable outcome (mRS 3-6)"""
        payload = {
            "params": {
                "mrs_score": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] > 2
    
    def test_invalid_score_high(self, test_client):
        """Test invalid score above range"""
        payload = {
            "params": {
                "mrs_score": 7
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        # Should either error or clamp to valid range
        # Depending on implementation
        assert response.status_code in [200, 400, 422]
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {}
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
