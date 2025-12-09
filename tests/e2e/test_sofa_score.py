"""
E2E Tests for SOFA (Sequential Organ Failure Assessment) Score Calculator

Tests the SOFA score through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestSofaScoreE2E:
    """E2E tests for SOFA Score Calculator"""
    
    ENDPOINT = "/api/v1/calculate/sofa_score"
    
    def test_minimal_organ_dysfunction(self, test_client):
        """Test minimal organ dysfunction - SOFA 0-1"""
        payload = {
            "params": {
                "pao2_fio2_ratio": 400,
                "platelets": 200,
                "bilirubin": 0.8,
                "gcs_score": 15,
                "creatinine": 0.9
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] <= 2
    
    def test_mild_organ_dysfunction(self, test_client):
        """Test mild organ dysfunction"""
        payload = {
            "params": {
                "pao2_fio2_ratio": 350,
                "platelets": 120,
                "bilirubin": 1.5,
                "gcs_score": 14,
                "creatinine": 1.5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 2
    
    def test_moderate_organ_dysfunction(self, test_client):
        """Test moderate multi-organ dysfunction"""
        payload = {
            "params": {
                "pao2_fio2_ratio": 200,
                "platelets": 80,
                "bilirubin": 3.0,
                "gcs_score": 12,
                "creatinine": 2.5
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 6
    
    def test_severe_organ_failure(self, test_client):
        """Test severe multi-organ failure"""
        payload = {
            "params": {
                "pao2_fio2_ratio": 100,
                "platelets": 30,
                "bilirubin": 8.0,
                "gcs_score": 6,
                "creatinine": 5.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 12
    
    def test_with_vasopressors(self, test_client):
        """Test with vasopressor support"""
        payload = {
            "params": {
                "pao2_fio2_ratio": 300,
                "platelets": 150,
                "bilirubin": 1.0,
                "gcs_score": 15,
                "creatinine": 1.0,
                "map_value": 65,
                "norepinephrine_dose": 0.1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Vasopressor use adds cardiovascular points
        assert data["result"]["value"] >= 0
    
    def test_mechanically_ventilated(self, test_client):
        """Test mechanically ventilated patient"""
        payload = {
            "params": {
                "pao2_fio2_ratio": 150,
                "platelets": 100,
                "bilirubin": 2.0,
                "gcs_score": 10,
                "creatinine": 1.8,
                "is_mechanically_ventilated": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 5
    
    def test_with_low_urine_output(self, test_client):
        """Test with low urine output (renal dysfunction)"""
        payload = {
            "params": {
                "pao2_fio2_ratio": 350,
                "platelets": 180,
                "bilirubin": 1.0,
                "gcs_score": 15,
                "creatinine": 3.0,
                "urine_output_24h": 300
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 2
    
    def test_septic_shock_patient(self, test_client):
        """Test typical septic shock patient"""
        payload = {
            "params": {
                "pao2_fio2_ratio": 180,
                "platelets": 60,
                "bilirubin": 2.5,
                "gcs_score": 11,
                "creatinine": 2.2,
                "map_value": 55,
                "norepinephrine_dose": 0.2,
                "is_mechanically_ventilated": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 8
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {
                "pao2_fio2_ratio": 300
                # Missing other required params
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
    
    def test_boundary_pf_ratio_low(self, test_client):
        """Test boundary P/F ratio (severe ARDS)"""
        payload = {
            "params": {
                "pao2_fio2_ratio": 50,
                "platelets": 150,
                "bilirubin": 1.0,
                "gcs_score": 15,
                "creatinine": 1.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Very low P/F = 3+ respiratory points
        assert data["result"]["value"] >= 3
