"""
E2E Tests for Apfel PONV Score Calculator

Tests the Apfel Score for Post-Operative Nausea and Vomiting through the REST API.

Parameters:
    female_gender: bool - Female sex
    history_motion_sickness_or_ponv: bool - History of motion sickness or PONV
    non_smoker: bool - Non-smoking status
    postoperative_opioids: bool - Use of postoperative opioids planned
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestApfelPonvE2E:
    """E2E tests for Apfel PONV Score Calculator"""
    
    ENDPOINT = "/api/v1/calculate/apfel_ponv"
    
    def test_low_risk_score_0(self, test_client):
        """Test low risk patient (score 0) - ~10% PONV risk"""
        payload = {
            "params": {
                "female_gender": False,
                "non_smoker": False,
                "history_motion_sickness_or_ponv": False,
                "postoperative_opioids": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0
    
    def test_score_1(self, test_client):
        """Test score 1 - ~20% PONV risk"""
        payload = {
            "params": {
                "female_gender": True,
                "non_smoker": False,
                "history_motion_sickness_or_ponv": False,
                "postoperative_opioids": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1
    
    def test_score_2(self, test_client):
        """Test score 2 - ~40% PONV risk"""
        payload = {
            "params": {
                "female_gender": True,
                "non_smoker": True,
                "history_motion_sickness_or_ponv": False,
                "postoperative_opioids": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2
    
    def test_score_3(self, test_client):
        """Test score 3 - ~60% PONV risk"""
        payload = {
            "params": {
                "female_gender": True,
                "non_smoker": True,
                "history_motion_sickness_or_ponv": True,
                "postoperative_opioids": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3
    
    def test_high_risk_score_4(self, test_client):
        """Test high risk patient (score 4) - ~80% PONV risk"""
        payload = {
            "params": {
                "female_gender": True,
                "non_smoker": True,
                "history_motion_sickness_or_ponv": True,
                "postoperative_opioids": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4
    
    def test_male_nonsmoker_with_history(self, test_client):
        """Test male non-smoker with PONV history"""
        payload = {
            "params": {
                "female_gender": False,
                "non_smoker": True,
                "history_motion_sickness_or_ponv": True,
                "postoperative_opioids": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2
    
    def test_female_smoker_with_opioids(self, test_client):
        """Test female smoker receiving postop opioids"""
        payload = {
            "params": {
                "female_gender": True,
                "non_smoker": False,
                "history_motion_sickness_or_ponv": False,
                "postoperative_opioids": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2
    
    def test_male_smoker_no_risk_factors(self, test_client):
        """Test male smoker with no additional risk factors"""
        payload = {
            "params": {
                "female_gender": False,
                "non_smoker": False,
                "history_motion_sickness_or_ponv": False,
                "postoperative_opioids": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0
    
    def test_motion_sickness_history(self, test_client):
        """Test patient with motion sickness history (counts as PONV history)"""
        payload = {
            "params": {
                "female_gender": True,
                "non_smoker": True,
                "history_motion_sickness_or_ponv": True,
                "postoperative_opioids": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Maximum risk
        assert data["result"]["value"] == 4
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {
                "female_gender": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
