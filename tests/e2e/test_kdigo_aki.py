from typing import Any
"""
E2E Tests for KDIGO AKI Calculator

Tests the KDIGO AKI staging calculator through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestKdigoAkiE2E:
    """E2E tests for KDIGO AKI Calculator"""

    ENDPOINT = "/api/v1/calculate/kdigo_aki"

    def test_no_aki_normal_creatinine(self, test_client: Any) -> None:
        """Test no AKI - normal creatinine"""
        payload = {
            "params": {
                "current_creatinine": 1.0,
                "baseline_creatinine": 1.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0

    def test_stage_1_creatinine_rise(self, test_client: Any) -> None:
        """Test Stage 1 - creatinine 1.5-1.9x baseline"""
        payload = {
            "params": {
                "current_creatinine": 1.7,
                "baseline_creatinine": 1.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def test_stage_1_absolute_increase(self, test_client: Any) -> None:
        """Test Stage 1 - absolute increase ≥0.3 mg/dL in 48h"""
        payload = {
            "params": {
                "current_creatinine": 1.4,
                "baseline_creatinine": 1.0,
                "creatinine_increase_48h": 0.4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 1

    def test_stage_2_creatinine_rise(self, test_client: Any) -> None:
        """Test Stage 2 - creatinine 2.0-2.9x baseline"""
        payload = {
            "params": {
                "current_creatinine": 2.5,
                "baseline_creatinine": 1.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2

    def test_stage_3_creatinine_rise(self, test_client: Any) -> None:
        """Test Stage 3 - creatinine ≥3.0x baseline"""
        payload = {
            "params": {
                "current_creatinine": 3.5,
                "baseline_creatinine": 1.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_stage_3_creatinine_gt_4(self, test_client: Any) -> None:
        """Test Stage 3 - creatinine ≥4.0 mg/dL"""
        payload = {
            "params": {
                "current_creatinine": 4.5,
                "baseline_creatinine": 2.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_stage_1_urine_output(self, test_client: Any) -> None:
        """Test Stage 1 - urine output <0.5 mL/kg/h for 6-12h"""
        payload = {
            "params": {
                "current_creatinine": 1.0,
                "baseline_creatinine": 1.0,
                "urine_output_ml_kg_h": 0.4,
                "urine_output_duration_hours": 8
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 1

    def test_stage_2_urine_output(self, test_client: Any) -> None:
        """Test Stage 2 - urine output <0.5 mL/kg/h for ≥12h"""
        payload = {
            "params": {
                "current_creatinine": 1.0,
                "baseline_creatinine": 1.0,
                "urine_output_ml_kg_h": 0.4,
                "urine_output_duration_hours": 14
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 2

    def test_on_rrt(self, test_client: Any) -> None:
        """Test Stage 3 - on renal replacement therapy"""
        payload = {
            "params": {
                "current_creatinine": 2.0,
                "baseline_creatinine": 1.0,
                "on_rrt": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "current_creatinine": 2.0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
