from typing import Any
"""
E2E Tests for Centor Score Calculator

Tests the Centor Score for Strep Pharyngitis through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestCentorScoreE2E:
    """E2E tests for Centor Score Calculator"""

    ENDPOINT = "/api/v1/calculate/centor_score"

    def test_low_risk_score_0(self, test_client: Any) -> None:
        """Test low risk patient (score 0)"""
        payload = {
            "params": {
                "tonsillar_exudates": 0,
                "tender_anterior_cervical_nodes": 0,
                "fever": 0,
                "absence_of_cough": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 0

    def test_low_risk_score_1(self, test_client: Any) -> None:
        """Test low risk patient (score 1)"""
        payload = {
            "params": {
                "tonsillar_exudates": 1,
                "tender_anterior_cervical_nodes": 0,
                "fever": 0,
                "absence_of_cough": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def test_moderate_risk_score_2(self, test_client: Any) -> None:
        """Test moderate risk patient (score 2)"""
        payload = {
            "params": {
                "tonsillar_exudates": 1,
                "tender_anterior_cervical_nodes": 1,
                "fever": 0,
                "absence_of_cough": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Score 2 = ~15% probability of GAS
        assert data["result"]["value"] == 2

    def test_moderate_high_risk_score_3(self, test_client: Any) -> None:
        """Test moderate-high risk patient (score 3)"""
        payload = {
            "params": {
                "tonsillar_exudates": 1,
                "tender_anterior_cervical_nodes": 1,
                "fever": 1,
                "absence_of_cough": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Score 3 = ~32% probability of GAS
        assert data["result"]["value"] == 3

    def test_high_risk_score_4(self, test_client: Any) -> None:
        """Test high risk patient (score 4)"""
        payload = {
            "params": {
                "tonsillar_exudates": 1,
                "tender_anterior_cervical_nodes": 1,
                "fever": 1,
                "absence_of_cough": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Score 4 = ~56% probability of GAS
        assert data["result"]["value"] == 4

    def test_classic_strep_presentation(self, test_client: Any) -> None:
        """Test classic strep pharyngitis presentation"""
        payload = {
            "params": {
                "tonsillar_exudates": 1,
                "tender_anterior_cervical_nodes": 1,
                "fever": 1,
                "absence_of_cough": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4

    def test_viral_pharyngitis_likely(self, test_client: Any) -> None:
        """Test likely viral pharyngitis (with cough)"""
        payload = {
            "params": {
                "tonsillar_exudates": 1,
                "tender_anterior_cervical_nodes": 0,
                "fever": 1,
                "absence_of_cough": 0  # Cough present
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Cough suggests viral
        assert data["result"]["value"] == 2

    def test_fever_and_lymphadenopathy(self, test_client: Any) -> None:
        """Test fever with lymphadenopathy only"""
        payload = {
            "params": {
                "tonsillar_exudates": 0,
                "tender_anterior_cervical_nodes": 1,
                "fever": 1,
                "absence_of_cough": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2

    def test_exudates_only(self, test_client: Any) -> None:
        """Test tonsillar exudates only"""
        payload = {
            "params": {
                "tonsillar_exudates": 1,
                "tender_anterior_cervical_nodes": 0,
                "fever": 0,
                "absence_of_cough": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def _skip_test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload = {
            "params": {
                "tonsillar_exudates": 1,
                "tender_anterior_cervical_nodes": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
