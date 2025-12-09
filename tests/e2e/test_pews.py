"""
E2E Tests for PEWS (Pediatric Early Warning Score) Calculator

Tests the PEWS through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestPewsE2E:
    """E2E tests for PEWS Calculator"""
    
    ENDPOINT = "/api/v1/calculate/pews"
    
    def test_stable_child_score_0(self, test_client):
        """Test stable child (score 0)"""
        payload = {
            "params": {
                "behavior_score": 0,
                "cardiovascular_score": 0,
                "respiratory_score": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0
    
    def test_mild_concern_score_2(self, test_client):
        """Test mild clinical concern (score 2)"""
        payload = {
            "params": {
                "behavior_score": 1,
                "cardiovascular_score": 0,
                "respiratory_score": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2
    
    def test_moderate_concern_score_4(self, test_client):
        """Test moderate clinical concern (score 4)"""
        payload = {
            "params": {
                "behavior_score": 1,
                "cardiovascular_score": 1,
                "respiratory_score": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4
    
    def test_high_concern_score_6_plus(self, test_client):
        """Test high clinical concern (score ≥6)"""
        payload = {
            "params": {
                "behavior_score": 2,
                "cardiovascular_score": 2,
                "respiratory_score": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 6
    
    def test_critical_child(self, test_client):
        """Test critically ill child (maximum score)"""
        payload = {
            "params": {
                "behavior_score": 3,
                "cardiovascular_score": 3,
                "respiratory_score": 3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 9
    
    def test_respiratory_distress(self, test_client):
        """Test child with isolated respiratory distress"""
        payload = {
            "params": {
                "behavior_score": 1,
                "cardiovascular_score": 0,
                "respiratory_score": 3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 4
    
    def test_cardiovascular_compromise(self, test_client):
        """Test child with cardiovascular compromise"""
        payload = {
            "params": {
                "behavior_score": 2,
                "cardiovascular_score": 3,
                "respiratory_score": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 5
    
    def test_altered_behavior_only(self, test_client):
        """Test child with altered behavior only"""
        payload = {
            "params": {
                "behavior_score": 2,
                "cardiovascular_score": 0,
                "respiratory_score": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2
    
    def test_trigger_threshold_score_3(self, test_client):
        """Test at trigger threshold (score 3)"""
        payload = {
            "params": {
                "behavior_score": 1,
                "cardiovascular_score": 1,
                "respiratory_score": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Score 3 often triggers nursing intervention
        assert data["result"]["value"] == 3
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {
                "behavior_score": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
