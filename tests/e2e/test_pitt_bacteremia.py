"""
E2E Tests for Pitt Bacteremia Score Calculator

Tests the Pitt Bacteremia Score through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestPittBacteremiaE2E:
    """E2E tests for Pitt Bacteremia Score Calculator"""
    
    ENDPOINT = "/api/v1/calculate/pitt_bacteremia"
    
    def test_low_mortality_score_0_3(self, test_client):
        """Test low mortality risk (score 0-3)"""
        payload = {
            "params": {
                "temperature_category": "low_mild",
                "hypotension": False,
                "mechanical_ventilation": False,
                "cardiac_arrest": False,
                "mental_status": "alert"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] <= 3
    
    def test_intermediate_mortality_score_4_5(self, test_client):
        """Test intermediate mortality risk (score 4-5)"""
        payload = {
            "params": {
                "temperature_category": "extreme",
                "hypotension": True,
                "mechanical_ventilation": False,
                "cardiac_arrest": False,
                "mental_status": "disoriented"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 4
    
    def test_high_mortality_score_6_plus(self, test_client):
        """Test high mortality risk (score ≥6)"""
        payload = {
            "params": {
                "temperature_category": "extreme",
                "hypotension": True,
                "mechanical_ventilation": True,
                "cardiac_arrest": False,
                "mental_status": "stuporous"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 6
    
    def test_critical_patient_with_arrest(self, test_client):
        """Test critical patient with cardiac arrest"""
        payload = {
            "params": {
                "temperature_category": "extreme",
                "hypotension": True,
                "mechanical_ventilation": True,
                "cardiac_arrest": True,
                "mental_status": "comatose"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Maximum score scenario
        assert data["result"]["value"] >= 10
    
    def test_stable_febrile_patient(self, test_client):
        """Test stable febrile patient"""
        payload = {
            "params": {
                "temperature_category": "normal",
                "hypotension": False,
                "mechanical_ventilation": False,
                "cardiac_arrest": False,
                "mental_status": "alert"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0
    
    def test_septic_shock_patient(self, test_client):
        """Test patient with septic shock"""
        payload = {
            "params": {
                "temperature_category": "extreme",
                "hypotension": True,
                "mechanical_ventilation": True,
                "cardiac_arrest": False,
                "mental_status": "disoriented"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 6
    
    def test_altered_mental_status_only(self, test_client):
        """Test patient with isolated altered mental status"""
        payload = {
            "params": {
                "temperature_category": "normal",
                "hypotension": False,
                "mechanical_ventilation": False,
                "cardiac_arrest": False,
                "mental_status": "comatose"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Comatose = 4 points
        assert data["result"]["value"] == 4
    
    def test_hypothermic_patient(self, test_client):
        """Test hypothermic bacteremia patient"""
        payload = {
            "params": {
                "temperature_category": "extreme",
                "hypotension": True,
                "mechanical_ventilation": False,
                "cardiac_arrest": False,
                "mental_status": "disoriented"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 5
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {
                "temperature_category": "normal"
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
