from typing import Any
"""
E2E Tests for Fisher Grade Calculator

Tests the Fisher Grade for Subarachnoid Hemorrhage through the REST API.
"""
from tests.e2e.conftest import assert_calculation_error, assert_successful_calculation


class TestFisherGradeE2E:
    """E2E tests for Fisher Grade Calculator"""

    ENDPOINT = "/api/v1/calculate/fisher_grade"

    def test_grade_1_no_blood(self, test_client: Any) -> None:
        """Test Grade 1 - No blood detected on CT"""
        payload: dict[str, Any] = {
            "params": {
                "no_blood": True,
                "thick_sah": False,
                "ivh_present": False,
                "use_modified": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 1

    def test_grade_2_diffuse_thin(self, test_client: Any) -> None:
        """Test Grade 2 - Diffuse thin layer (<1mm)"""
        payload: dict[str, Any] = {
            "params": {
                "no_blood": False,
                "thick_sah": False,
                "ivh_present": False,
                "use_modified": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 2

    def test_grade_3_thick_cisternal(self, test_client: Any) -> None:
        """Test Grade 3 - Localized clot/thick layer (>1mm)"""
        payload: dict[str, Any] = {
            "params": {
                "no_blood": False,
                "thick_sah": True,
                "ivh_present": False,
                "use_modified": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_grade_4_intracerebral_ivh(self, test_client: Any) -> None:
        """Test Grade 4 - Intracerebral or intraventricular blood"""
        payload: dict[str, Any] = {
            "params": {
                "no_blood": False,
                "thick_sah": False,
                "ivh_present": True,
                "use_modified": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 4

    def test_low_vasospasm_risk(self, test_client: Any) -> None:
        """Test low vasospasm risk (Grade 1-2)"""
        payload: dict[str, Any] = {
            "params": {
                "no_blood": True,
                "thick_sah": False,
                "ivh_present": False,
                "use_modified": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] <= 2

    def test_high_vasospasm_risk(self, test_client: Any) -> None:
        """Test high vasospasm risk (Grade 3)"""
        payload: dict[str, Any] = {
            "params": {
                "no_blood": False,
                "thick_sah": True,
                "ivh_present": False,
                "use_modified": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] == 3

    def test_modified_fisher_consideration(self, test_client: Any) -> None:
        """Test using modified Fisher scale"""
        payload: dict[str, Any] = {
            "params": {
                "no_blood": False,
                "thick_sah": True,
                "ivh_present": True,
                "use_modified": True
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 3

    def test_angiogram_negative_sah(self, test_client: Any) -> None:
        """Test angiogram-negative SAH (usually Grade 1-2)"""
        payload: dict[str, Any] = {
            "params": {
                "no_blood": False,
                "thick_sah": False,
                "ivh_present": False,
                "use_modified": False
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] <= 2

    def test_missing_required_params(self, test_client: Any) -> None:
        """Test missing required parameters"""
        payload: dict[str, Any] = {
            "params": {}
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
