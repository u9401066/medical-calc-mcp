"""
E2E Tests for Glasgow Coma Scale (GCS) Calculator

Tests the GCS neurological assessment through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestGlasgowComaScaleE2E:
    """E2E tests for Glasgow Coma Scale Calculator"""
    
    ENDPOINT = "/api/v1/calculate/glasgow_coma_scale"
    
    def test_fully_conscious(self, test_client):
        """Test GCS 15 - fully conscious"""
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
    
    def test_mild_brain_injury(self, test_client):
        """Test GCS 13-14 - mild brain injury"""
        payload = {
            "params": {
                "eye_response": 4,
                "verbal_response": 4,
                "motor_response": 6
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 14
    
    def test_moderate_brain_injury(self, test_client):
        """Test GCS 9-12 - moderate brain injury"""
        payload = {
            "params": {
                "eye_response": 3,
                "verbal_response": 3,
                "motor_response": 5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 11
    
    def test_severe_brain_injury(self, test_client):
        """Test GCS ≤8 - severe brain injury (coma)"""
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
    
    def test_minimum_score(self, test_client):
        """Test GCS 3 - minimum score (deep coma)"""
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
    
    def test_intubated_patient(self, test_client):
        """Test intubated patient (verbal score not assessable)"""
        payload = {
            "params": {
                "eye_response": 4,
                "verbal_response": 1,
                "motor_response": 6,
                "is_intubated": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Score noted as "T" for tube
        assert data["result"]["value"] >= 3
    
    def test_decerebrate_posturing(self, test_client):
        """Test decerebrate posturing (extension)"""
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
    
    def test_decorticate_posturing(self, test_client):
        """Test decorticate posturing (abnormal flexion)"""
        payload = {
            "params": {
                "eye_response": 1,
                "verbal_response": 1,
                "motor_response": 3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 5
    
    def test_invalid_eye_response_too_high(self, test_client):
        """Test invalid eye response (>4)"""
        payload = {
            "params": {
                "eye_response": 5,
                "verbal_response": 5,
                "motor_response": 6
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
    
    def test_invalid_verbal_response_too_high(self, test_client):
        """Test invalid verbal response (>5)"""
        payload = {
            "params": {
                "eye_response": 4,
                "verbal_response": 6,
                "motor_response": 6
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
    
    def test_invalid_motor_response_too_high(self, test_client):
        """Test invalid motor response (>6)"""
        payload = {
            "params": {
                "eye_response": 4,
                "verbal_response": 5,
                "motor_response": 7
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {
                "eye_response": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
