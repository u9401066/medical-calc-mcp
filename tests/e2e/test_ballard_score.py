"""
E2E Tests for Ballard Score Calculator

Tests the Ballard Score for Neonatal Maturity through the REST API.
"""
import pytest
from tests.e2e.conftest import assert_successful_calculation, assert_calculation_error


class TestBallardScoreE2E:
    """E2E tests for Ballard Score Calculator"""
    
    ENDPOINT = "/api/v1/calculate/ballard_score"
    
    def test_preterm_infant(self, test_client):
        """Test preterm infant (score suggesting <37 weeks)"""
        payload = {
            "params": {
                "posture": -1,
                "square_window": -1,
                "arm_recoil": -1,
                "popliteal_angle": -1,
                "scarf_sign": -1,
                "heel_to_ear": -1,
                "skin": -1,
                "lanugo": -1,
                "plantar_surface": -1,
                "breast": -1,
                "eye_ear": -1,
                "genitals": -1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Low score indicates preterm
        assert data["result"]["value"] < 30
    
    def test_term_infant(self, test_client):
        """Test term infant (score suggesting 38-40 weeks)"""
        payload = {
            "params": {
                "posture": 3,
                "square_window": 3,
                "arm_recoil": 3,
                "popliteal_angle": 3,
                "scarf_sign": 3,
                "heel_to_ear": 3,
                "skin": 3,
                "lanugo": 3,
                "plantar_surface": 3,
                "breast": 3,
                "eye_ear": 3,
                "genitals": 3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # Score around 30-35 for term
        assert data["result"]["value"] >= 30
    
    def test_post_term_infant(self, test_client):
        """Test post-term infant (score suggesting >42 weeks)"""
        payload = {
            "params": {
                "posture": 4,
                "square_window": 4,
                "arm_recoil": 4,
                "popliteal_angle": 4,
                "scarf_sign": 4,
                "heel_to_ear": 4,
                "skin": 4,
                "lanugo": 4,
                "plantar_surface": 4,
                "breast": 4,
                "eye_ear": 4,
                "genitals": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        # High score indicates post-term
        assert data["result"]["value"] >= 40
    
    def test_early_preterm(self, test_client):
        """Test early preterm infant (<32 weeks)"""
        payload = {
            "params": {
                "posture": 0,
                "square_window": 0,
                "arm_recoil": 0,
                "popliteal_angle": 0,
                "scarf_sign": 0,
                "heel_to_ear": 0,
                "skin": 0,
                "lanugo": 0,
                "plantar_surface": 0,
                "breast": 0,
                "eye_ear": 0,
                "genitals": 0
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0
    
    def test_late_preterm(self, test_client):
        """Test late preterm infant (34-36 weeks)"""
        payload = {
            "params": {
                "posture": 2,
                "square_window": 2,
                "arm_recoil": 2,
                "popliteal_angle": 2,
                "scarf_sign": 2,
                "heel_to_ear": 2,
                "skin": 2,
                "lanugo": 2,
                "plantar_surface": 2,
                "breast": 2,
                "eye_ear": 2,
                "genitals": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 20
    
    def test_neuromuscular_component(self, test_client):
        """Test with focus on neuromuscular maturity"""
        payload = {
            "params": {
                "posture": 3,
                "square_window": 4,
                "arm_recoil": 4,
                "popliteal_angle": 4,
                "scarf_sign": 3,
                "heel_to_ear": 4,
                "skin": 2,
                "lanugo": 2,
                "plantar_surface": 2,
                "breast": 2,
                "eye_ear": 2,
                "genitals": 2
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 25
    
    def test_physical_maturity_component(self, test_client):
        """Test with focus on physical maturity"""
        payload = {
            "params": {
                "posture": 2,
                "square_window": 2,
                "arm_recoil": 2,
                "popliteal_angle": 2,
                "scarf_sign": 2,
                "heel_to_ear": 2,
                "skin": 4,
                "lanugo": 4,
                "plantar_surface": 4,
                "breast": 4,
                "eye_ear": 4,
                "genitals": 4
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 25
    
    def test_discordant_maturity(self, test_client):
        """Test infant with discordant maturity features"""
        payload = {
            "params": {
                "posture": 4,
                "square_window": 1,
                "arm_recoil": 4,
                "popliteal_angle": 1,
                "scarf_sign": 4,
                "heel_to_ear": 1,
                "skin": 3,
                "lanugo": 1,
                "plantar_surface": 3,
                "breast": 1,
                "eye_ear": 3,
                "genitals": 1
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        data = assert_successful_calculation(response)
        assert data["result"]["value"] >= 0
    
    def test_missing_required_params(self, test_client):
        """Test missing required parameters"""
        payload = {
            "params": {
                "posture": 3,
                "square_window": 3,
                "arm_recoil": 3
            }
        }
        response = test_client.post(self.ENDPOINT, json=payload)
        assert_calculation_error(response)
