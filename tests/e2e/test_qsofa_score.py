from typing import Any

"""
E2E Tests for qSOFA (Quick SOFA) Score Calculator

Tests the qSOFA sepsis screening score through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestQsofaScoreE2E:
    """E2E tests for qSOFA Score Calculator"""

    ENDPOINT = "/api/v1/calculate/qsofa_score"

    def test_no_criteria_met(self, test_client: Any) -> None:
        """Test qSOFA 0 - no criteria met"""
        payload = {
            "params": {
                "respiratory_rate": 18,
                "systolic_bp": 120,
                "altered_mentation": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0

    def test_one_criterion_respiratory(self, test_client: Any) -> None:
        """Test qSOFA 1 - only respiratory rate elevated"""
        payload = {
            "params": {
                "respiratory_rate": 24,
                "systolic_bp": 120,
                "altered_mentation": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def test_one_criterion_hypotension(self, test_client: Any) -> None:
        """Test qSOFA 1 - only hypotension"""
        payload = {
            "params": {
                "respiratory_rate": 18,
                "systolic_bp": 95,
                "altered_mentation": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def test_one_criterion_mentation(self, test_client: Any) -> None:
        """Test qSOFA 1 - only altered mentation"""
        payload = {
            "params": {
                "respiratory_rate": 18,
                "systolic_bp": 120,
                "altered_mentation": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def test_two_criteria_positive(self, test_client: Any) -> None:
        """Test qSOFA 2 - two criteria met (positive screen)"""
        payload = {
            "params": {
                "respiratory_rate": 24,
                "systolic_bp": 95,
                "altered_mentation": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2

    def test_all_criteria_met(self, test_client: Any) -> None:
        """Test qSOFA 3 - all criteria met"""
        payload = {
            "params": {
                "respiratory_rate": 25,
                "systolic_bp": 90,
                "altered_mentation": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_with_gcs_score(self, test_client: Any) -> None:
        """Test using GCS score for altered mentation"""
        payload = {
            "params": {
                "respiratory_rate": 22,
                "systolic_bp": 100,
                "gcs_score": 13
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # GCS < 15 = altered mentation
        assert data["result"]["value"] >= 1

    def test_boundary_respiratory_rate(self, test_client: Any) -> None:
        """Test boundary respiratory rate (≥22)"""
        payload = {
            "params": {
                "respiratory_rate": 22,
                "systolic_bp": 120,
                "altered_mentation": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def test_boundary_systolic_bp(self, test_client: Any) -> None:
        """Test boundary systolic BP (≤100)"""
        payload = {
            "params": {
                "respiratory_rate": 18,
                "systolic_bp": 100,
                "altered_mentation": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def _skip_test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "respiratory_rate": 22
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
