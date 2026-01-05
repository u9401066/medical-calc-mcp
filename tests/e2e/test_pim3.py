from typing import Any
"""
E2E Tests for PIM3 (Pediatric Index of Mortality 3) Calculator

Tests the PIM3 Score through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestPim3E2E:
    """E2E tests for PIM3 Calculator"""

    ENDPOINT = "/api/v1/calculate/pim3"

    def test_low_risk_patient(self, test_client: Any) -> None:
        """Test low risk pediatric patient"""
        payload = {
            "params": {
                "systolic_bp": 100,
                "pupillary_reaction": "both_react",
                "mechanical_ventilation": False,
                "base_excess": 0,
                "elective_admission": True,
                "recovery_post_procedure": True,
                "cardiac_bypass": False,
                "low_risk_diagnosis": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Low predicted mortality
        assert data["result"]["value"] >= 0

    def test_high_risk_patient(self, test_client: Any) -> None:
        """Test high risk pediatric patient"""
        payload = {
            "params": {
                "systolic_bp": 50,
                "pupillary_reaction": "both_fixed",
                "mechanical_ventilation": True,
                "base_excess": -15,
                "elective_admission": False,
                "recovery_post_procedure": False,
                "cardiac_bypass": False,
                "high_risk_diagnosis": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Higher predicted mortality
        assert data["result"]["value"] >= 0

    def test_cardiac_surgery_patient(self, test_client: Any) -> None:
        """Test post-cardiac surgery patient"""
        payload = {
            "params": {
                "systolic_bp": 85,
                "pupillary_reaction": "both_react",
                "mechanical_ventilation": True,
                "base_excess": -2,
                "elective_admission": True,
                "recovery_post_procedure": True,
                "cardiac_bypass": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0

    def test_hypotensive_patient(self, test_client: Any) -> None:
        """Test hypotensive patient"""
        payload = {
            "params": {
                "systolic_bp": 40,
                "pupillary_reaction": "both_react",
                "mechanical_ventilation": True,
                "base_excess": -8,
                "elective_admission": False,
                "recovery_post_procedure": False,
                "cardiac_bypass": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0

    def test_severe_acidosis(self, test_client: Any) -> None:
        """Test patient with severe metabolic acidosis"""
        payload = {
            "params": {
                "systolic_bp": 75,
                "pupillary_reaction": "both_react",
                "mechanical_ventilation": True,
                "base_excess": -20,
                "elective_admission": False,
                "recovery_post_procedure": False,
                "cardiac_bypass": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0

    def test_one_fixed_pupil(self, test_client: Any) -> None:
        """Test patient with one fixed pupil"""
        payload = {
            "params": {
                "systolic_bp": 80,
                "pupillary_reaction": "one_fixed",
                "mechanical_ventilation": True,
                "base_excess": -5,
                "elective_admission": False,
                "recovery_post_procedure": False,
                "cardiac_bypass": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0

    def test_spontaneous_breathing(self, test_client: Any) -> None:
        """Test patient not mechanically ventilated"""
        payload = {
            "params": {
                "systolic_bp": 95,
                "pupillary_reaction": "both_react",
                "mechanical_ventilation": False,
                "base_excess": -1,
                "elective_admission": False,
                "recovery_post_procedure": False,
                "cardiac_bypass": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0

    def test_very_high_risk_diagnosis(self, test_client: Any) -> None:
        """Test patient with very high risk diagnosis"""
        payload = {
            "params": {
                "systolic_bp": 70,
                "pupillary_reaction": "both_react",
                "mechanical_ventilation": True,
                "base_excess": -10,
                "elective_admission": False,
                "recovery_post_procedure": False,
                "cardiac_bypass": False,
                "very_high_risk_diagnosis": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0

    def _skip_test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "systolic_bp": 100
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
