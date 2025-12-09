"""
E2E Tests for Pediatric GCS Calculator

Tests the Pediatric Glasgow Coma Scale through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestPediatricGcsE2E:
    """E2E tests for Pediatric GCS Calculator"""
    
    ENDPOINT = "/api/v1/calculate/pediatric_gcs"
    
    def test_fully_conscious_score_15(self, test_client):
        """Test fully conscious child (score 15)"""
        payload = {
            "params": {
                "eye_response": 4,
                "verbal_response": 5,
                "motor_response": 6
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 15
    
    def test_mild_impairment_score_13_14(self, test_client):
        """Test mild neurological impairment (13-14)"""
        payload = {
            "params": {
                "eye_response": 4,
                "verbal_response": 4,
                "motor_response": 5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert 13 <= data["result"]["value"] <= 14
    
    def test_moderate_impairment_score_9_12(self, test_client):
        """Test moderate neurological impairment (9-12)"""
        payload = {
            "params": {
                "eye_response": 3,
                "verbal_response": 3,
                "motor_response": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert 9 <= data["result"]["value"] <= 12
    
    def test_severe_impairment_score_3_8(self, test_client):
        """Test severe neurological impairment (3-8)"""
        payload = {
            "params": {
                "eye_response": 2,
                "verbal_response": 2,
                "motor_response": 3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert 3 <= data["result"]["value"] <= 8
    
    def test_minimum_score_3(self, test_client):
        """Test minimum score (3)"""
        payload = {
            "params": {
                "eye_response": 1,
                "verbal_response": 1,
                "motor_response": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3
    
    def test_intubated_child_threshold(self, test_client):
        """Test intubated child (verbal score modified)"""
        payload = {
            "params": {
                "eye_response": 4,
                "verbal_response": 1,  # Intubated
                "motor_response": 6
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Motor and eye preserved
        assert data["result"]["value"] == 11
    
    def test_sedated_post_op_child(self, test_client):
        """Test sedated post-operative child"""
        payload = {
            "params": {
                "eye_response": 2,
                "verbal_response": 2,
                "motor_response": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 8
    
    def test_posturing_response(self, test_client):
        """Test child with posturing (motor 2-3)"""
        payload = {
            "params": {
                "eye_response": 1,
                "verbal_response": 1,
                "motor_response": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4
    
    def test_localizing_pain_only(self, test_client):
        """Test child localizing to pain"""
        payload = {
            "params": {
                "eye_response": 2,
                "verbal_response": 2,
                "motor_response": 5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 9
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {
                "eye_response": 4,
                "verbal_response": 5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
