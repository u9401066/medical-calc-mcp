"""
E2E Tests for SOFA-2 Score Calculator (JAMA 2025)

Tests the updated SOFA-2 score through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestSofa2ScoreE2E:
    """E2E tests for SOFA-2 Score Calculator"""
    
    ENDPOINT = "/api/v1/calculate/sofa2_score"
    
    def test_minimal_dysfunction(self, test_client):
        """Test minimal organ dysfunction"""
        payload = {
            "params": {
                "gcs_score": 15,
                "pao2_fio2_ratio": 400,
                "bilirubin": 0.8,
                "creatinine": 0.9,
                "platelets": 200,
                "map_value": 75
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] <= 2
    
    def test_with_sedation(self, test_client):
        """Test with sedation (affects GCS scoring)"""
        payload = {
            "params": {
                "gcs_score": 10,
                "pao2_fio2_ratio": 300,
                "bilirubin": 1.5,
                "creatinine": 1.2,
                "platelets": 150,
                "map_value": 70,
                "receiving_sedation_or_delirium_drugs": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0
    
    def test_on_ecmo(self, test_client):
        """Test patient on ECMO support"""
        payload = {
            "params": {
                "gcs_score": 8,
                "pao2_fio2_ratio": 80,
                "bilirubin": 3.0,
                "creatinine": 2.5,
                "platelets": 80,
                "map_value": 60,
                "on_ecmo": True,
                "advanced_ventilatory_support": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 8
    
    def test_on_rrt(self, test_client):
        """Test patient on renal replacement therapy"""
        payload = {
            "params": {
                "gcs_score": 14,
                "pao2_fio2_ratio": 250,
                "bilirubin": 2.0,
                "creatinine": 4.5,
                "platelets": 100,
                "map_value": 65,
                "on_rrt": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # RRT = maximum renal points
        assert data["result"]["value"] >= 4
    
    def test_with_vasopressors(self, test_client):
        """Test with vasopressor support"""
        payload = {
            "params": {
                "gcs_score": 13,
                "pao2_fio2_ratio": 200,
                "bilirubin": 1.8,
                "creatinine": 1.5,
                "platelets": 120,
                "map_value": 55,
                "norepinephrine_epinephrine_dose": 0.15
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 5
    
    def test_with_urine_output(self, test_client):
        """Test with various urine output periods"""
        payload = {
            "params": {
                "gcs_score": 15,
                "pao2_fio2_ratio": 350,
                "bilirubin": 1.0,
                "creatinine": 2.0,
                "platelets": 180,
                "map_value": 70,
                "urine_output_24h": 400
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0
    
    def test_severe_multi_organ_failure(self, test_client):
        """Test severe multi-organ failure"""
        payload = {
            "params": {
                "gcs_score": 6,
                "pao2_fio2_ratio": 80,
                "bilirubin": 10.0,
                "creatinine": 5.0,
                "platelets": 20,
                "map_value": 50,
                "norepinephrine_epinephrine_dose": 0.3,
                "advanced_ventilatory_support": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 15
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {
                "gcs_score": 15
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
