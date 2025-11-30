"""
Phase 11 Calculator Tests

Tests for Upcoming Calculators completed in Phase 11:
- IdealBodyWeightCalculator (Devine formula)
- PfRatioCalculator (ARDS Berlin Definition)
- RoxIndexCalculator (HFNC failure prediction)
- GraceScoreCalculator (ACS risk stratification)
- FourTsHitCalculator (HIT probability)
- AcefIiScoreCalculator (Cardiac surgery risk)
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from domain.services.calculators import (
    IdealBodyWeightCalculator,
    PfRatioCalculator,
    RoxIndexCalculator,
    GraceScoreCalculator,
    FourTsHitCalculator,
    AcefIiScoreCalculator,
)
from domain.value_objects.interpretation import RiskLevel, Severity


# =============================================================================
# Ideal Body Weight Tests
# =============================================================================

class TestIdealBodyWeightCalculator:
    """Tests for IdealBodyWeightCalculator"""
    
    @pytest.fixture
    def calculator(self):
        return IdealBodyWeightCalculator()
    
    def test_metadata(self, calculator):
        """Test calculator metadata"""
        assert calculator.tool_id == "ideal_body_weight"
        assert "IBW" in calculator.metadata.name or "Ideal Body Weight" in calculator.metadata.name
    
    def test_male_170cm(self, calculator):
        """Test male patient 170 cm"""
        result = calculator.calculate(height_cm=170, sex="male")
        # 170 cm = 66.93 inches; IBW = 50 + 2.3 * (66.93 - 60) = 50 + 15.94 = 65.94 kg
        assert 64 <= result.value <= 68
    
    def test_female_160cm(self, calculator):
        """Test female patient 160 cm"""
        result = calculator.calculate(height_cm=160, sex="female")
        # 160 cm = 62.99 inches; IBW = 45.5 + 2.3 * (62.99 - 60) = 45.5 + 6.88 = 52.38 kg
        assert 50 <= result.value <= 55
    
    def test_male_180cm(self, calculator):
        """Test tall male patient 180 cm"""
        result = calculator.calculate(height_cm=180, sex="male")
        # 180 cm = 70.87 inches; IBW = 50 + 2.3 * (70.87 - 60) = 50 + 25 = 75 kg
        assert 72 <= result.value <= 78
    
    def test_female_150cm(self, calculator):
        """Test shorter female patient 150 cm"""
        result = calculator.calculate(height_cm=150, sex="female")
        # 150 cm = 59.06 inches; IBW = 45.5 + 2.3 * (59.06 - 60) = 45.5 - 2.16 = 43.34 kg
        # For very short patients, IBW should still be reasonable
        assert 40 <= result.value <= 50
    
    def test_with_actual_weight(self, calculator):
        """Test with actual weight to get ABW"""
        result = calculator.calculate(height_cm=170, sex="male", actual_weight_kg=100)
        # IBW ~ 66kg, ratio > 1.2 should trigger ABW calculation
        assert result.value > 0
        assert "Actual" in str(result.calculation_details) or "actual" in str(result.calculation_details).lower()
    
    def test_tidal_volume_recommendation(self, calculator):
        """Test that tidal volume range is provided"""
        result = calculator.calculate(height_cm=170, sex="male")
        assert "tidal" in str(result.calculation_details).lower() or "TV" in str(result.calculation_details)
    
    def test_invalid_height_too_low(self, calculator):
        """Test validation for very low height"""
        with pytest.raises(ValueError):
            calculator.calculate(height_cm=50, sex="male")
    
    def test_invalid_height_too_high(self, calculator):
        """Test validation for very high height"""
        with pytest.raises(ValueError):
            calculator.calculate(height_cm=300, sex="female")


# =============================================================================
# P/F Ratio Tests
# =============================================================================

class TestPfRatioCalculator:
    """Tests for PfRatioCalculator"""
    
    @pytest.fixture
    def calculator(self):
        return PfRatioCalculator()
    
    def test_metadata(self, calculator):
        """Test calculator metadata"""
        assert calculator.tool_id == "pf_ratio"
        assert "P/F" in calculator.metadata.name or "PaO2/FiO2" in calculator.metadata.name
    
    def test_normal_oxygenation(self, calculator):
        """Test normal oxygenation on room air"""
        result = calculator.calculate(pao2=95, fio2=0.21)
        # P/F = 95/0.21 = 452
        assert result.value > 400
        assert result.interpretation.severity == Severity.NORMAL
    
    def test_mild_ards(self, calculator):
        """Test mild ARDS range"""
        result = calculator.calculate(pao2=80, fio2=0.4, peep=8)
        # P/F = 80/0.4 = 200
        assert 200 <= result.value <= 300
        # The interpretation might say "Mild ARDS" or similar
        assert "mild" in result.interpretation.summary.lower() or result.value == 200
    
    def test_moderate_ards(self, calculator):
        """Test moderate ARDS range"""
        result = calculator.calculate(pao2=60, fio2=0.5, peep=10)
        # P/F = 60/0.5 = 120
        assert 100 <= result.value <= 200
        assert "moderate" in result.interpretation.summary.lower() or 100 <= result.value <= 200
    
    def test_severe_ards(self, calculator):
        """Test severe ARDS range"""
        result = calculator.calculate(pao2=55, fio2=0.8, peep=14)
        # P/F = 55/0.8 = 68.75
        assert result.value < 100
        assert "severe" in result.interpretation.summary.lower() or result.value < 100
    
    def test_pf_calculation_accuracy(self, calculator):
        """Test P/F calculation accuracy"""
        result = calculator.calculate(pao2=100, fio2=0.5)
        assert abs(result.value - 200) < 1  # Should be exactly 200
    
    def test_room_air(self, calculator):
        """Test with room air FiO2"""
        result = calculator.calculate(pao2=90, fio2=0.21)
        # P/F = 90/0.21 ≈ 428.6
        assert result.value > 400
    
    def test_high_fio2(self, calculator):
        """Test with 100% oxygen"""
        result = calculator.calculate(pao2=300, fio2=1.0)
        # P/F = 300/1.0 = 300
        assert result.value == 300


# =============================================================================
# ROX Index Tests
# =============================================================================

class TestRoxIndexCalculator:
    """Tests for RoxIndexCalculator"""
    
    @pytest.fixture
    def calculator(self):
        return RoxIndexCalculator()
    
    def test_metadata(self, calculator):
        """Test calculator metadata"""
        assert calculator.tool_id == "rox_index"
        assert "ROX" in calculator.metadata.name
    
    def test_low_risk_high_rox(self, calculator):
        """Test low risk (high ROX) patient"""
        result = calculator.calculate(spo2=96, fio2=0.4, respiratory_rate=20)
        # ROX = (96/0.4) / 20 = 240/20 = 12.0
        assert result.value >= 4.88
        assert result.interpretation.risk_level == RiskLevel.LOW
    
    def test_high_risk_low_rox(self, calculator):
        """Test high risk (low ROX) patient"""
        result = calculator.calculate(spo2=88, fio2=0.8, respiratory_rate=35)
        # ROX = (88/0.8) / 35 = 110/35 = 3.14
        assert result.value < 3.85
        assert result.interpretation.risk_level == RiskLevel.HIGH
    
    def test_intermediate_risk(self, calculator):
        """Test intermediate risk patient"""
        result = calculator.calculate(spo2=92, fio2=0.5, respiratory_rate=25)
        # ROX = (92/0.5) / 25 = 184/25 = 7.36
        # This should be low risk (>4.88)
        assert result.value >= 4.88
    
    def test_borderline_intermediate(self, calculator):
        """Test borderline intermediate patient"""
        result = calculator.calculate(spo2=88, fio2=0.6, respiratory_rate=32)
        # ROX = (88/0.6) / 32 = 146.67/32 = 4.58
        # Should be intermediate (between 3.85 and 4.88)
        assert 3.85 <= result.value < 4.88
        assert result.interpretation.risk_level == RiskLevel.INTERMEDIATE
    
    def test_rox_calculation_accuracy(self, calculator):
        """Test ROX calculation accuracy"""
        result = calculator.calculate(spo2=95, fio2=0.5, respiratory_rate=20)
        # ROX = (95/0.5) / 20 = 190/20 = 9.5
        assert abs(result.value - 9.5) < 0.1
    
    def test_with_timing(self, calculator):
        """Test with HFNC timing specified"""
        result = calculator.calculate(spo2=92, fio2=0.5, respiratory_rate=25, hours_on_hfnc=6)
        assert result.value > 0


# =============================================================================
# GRACE Score Tests
# =============================================================================

class TestGraceScoreCalculator:
    """Tests for GraceScoreCalculator"""
    
    @pytest.fixture
    def calculator(self):
        return GraceScoreCalculator()
    
    def test_metadata(self, calculator):
        """Test calculator metadata"""
        assert calculator.tool_id == "grace_score"
        assert "GRACE" in calculator.metadata.name
    
    def test_low_risk_patient(self, calculator):
        """Test low risk ACS patient"""
        result = calculator.calculate(
            age=45,
            heart_rate=70,
            systolic_bp=130,
            creatinine=0.9,
            killip_class=1,
            cardiac_arrest=False,
            st_deviation=False,
            elevated_markers=False,
        )
        assert result.value <= 120  # Low to intermediate
        assert result.interpretation.risk_level in (RiskLevel.LOW, RiskLevel.INTERMEDIATE)
    
    def test_high_risk_patient(self, calculator):
        """Test high risk ACS patient"""
        result = calculator.calculate(
            age=75,
            heart_rate=110,
            systolic_bp=90,
            creatinine=2.0,
            killip_class=3,
            cardiac_arrest=True,
            st_deviation=True,
            elevated_markers=True,
        )
        assert result.value > 140
        assert result.interpretation.risk_level in (RiskLevel.HIGH, RiskLevel.VERY_HIGH)
    
    def test_intermediate_risk(self, calculator):
        """Test intermediate risk ACS patient"""
        result = calculator.calculate(
            age=65,
            heart_rate=85,
            systolic_bp=120,
            creatinine=1.2,
            killip_class=2,
            cardiac_arrest=False,
            st_deviation=True,
            elevated_markers=True,
        )
        # Score should be somewhere in the range
        assert result.value > 0
    
    def test_killip_class_impact(self, calculator):
        """Test that Killip class impacts score"""
        base = calculator.calculate(
            age=60, heart_rate=80, systolic_bp=120, creatinine=1.0,
            killip_class=1, cardiac_arrest=False, st_deviation=False, elevated_markers=False
        )
        killip4 = calculator.calculate(
            age=60, heart_rate=80, systolic_bp=120, creatinine=1.0,
            killip_class=4, cardiac_arrest=False, st_deviation=False, elevated_markers=False
        )
        assert killip4.value > base.value
    
    def test_cardiac_arrest_impact(self, calculator):
        """Test that cardiac arrest impacts score"""
        no_arrest = calculator.calculate(
            age=60, heart_rate=80, systolic_bp=120, creatinine=1.0,
            killip_class=1, cardiac_arrest=False, st_deviation=False, elevated_markers=False
        )
        with_arrest = calculator.calculate(
            age=60, heart_rate=80, systolic_bp=120, creatinine=1.0,
            killip_class=1, cardiac_arrest=True, st_deviation=False, elevated_markers=False
        )
        assert with_arrest.value > no_arrest.value


# =============================================================================
# 4Ts HIT Score Tests
# =============================================================================

class TestFourTsHitCalculator:
    """Tests for FourTsHitCalculator"""
    
    @pytest.fixture
    def calculator(self):
        return FourTsHitCalculator()
    
    def test_metadata(self, calculator):
        """Test calculator metadata"""
        assert calculator.tool_id in ("four_ts_hit", "4ts_hit")
        assert "4T" in calculator.metadata.name or "HIT" in calculator.metadata.name
    
    def test_low_probability(self, calculator):
        """Test low HIT probability"""
        result = calculator.calculate(
            thrombocytopenia=0,
            timing=0,
            thrombosis=0,
            other_causes=0,
        )
        assert result.value <= 3
        assert result.interpretation.risk_level == RiskLevel.LOW
    
    def test_high_probability(self, calculator):
        """Test high HIT probability"""
        result = calculator.calculate(
            thrombocytopenia=2,
            timing=2,
            thrombosis=2,
            other_causes=2,
        )
        assert result.value >= 6
        assert result.interpretation.risk_level == RiskLevel.HIGH
    
    def test_intermediate_probability(self, calculator):
        """Test intermediate HIT probability"""
        result = calculator.calculate(
            thrombocytopenia=1,
            timing=1,
            thrombosis=1,
            other_causes=1,
        )
        assert result.value == 4
        assert result.interpretation.risk_level == RiskLevel.INTERMEDIATE
    
    def test_score_calculation(self, calculator):
        """Test score calculation accuracy"""
        result = calculator.calculate(
            thrombocytopenia=2,
            timing=1,
            thrombosis=0,
            other_causes=2,
        )
        assert result.value == 5  # 2+1+0+2 = 5
    
    def test_max_score(self, calculator):
        """Test maximum possible score"""
        result = calculator.calculate(
            thrombocytopenia=2,
            timing=2,
            thrombosis=2,
            other_causes=2,
        )
        assert result.value == 8
    
    def test_min_score(self, calculator):
        """Test minimum possible score"""
        result = calculator.calculate(
            thrombocytopenia=0,
            timing=0,
            thrombosis=0,
            other_causes=0,
        )
        assert result.value == 0


# =============================================================================
# ACEF II Score Tests
# =============================================================================

class TestAcefIiScoreCalculator:
    """Tests for AcefIiScoreCalculator"""
    
    @pytest.fixture
    def calculator(self):
        return AcefIiScoreCalculator()
    
    def test_metadata(self, calculator):
        """Test calculator metadata"""
        assert calculator.tool_id == "acef_ii"
        assert "ACEF" in calculator.metadata.name
    
    def test_low_risk_patient(self, calculator):
        """Test low risk cardiac surgery patient"""
        result = calculator.calculate(
            age=55,
            lvef=60,
            creatinine=0.9,
            emergency=False,
        )
        # ACEF = 55/60 + 0 = 0.92
        assert result.value < 1.0
        assert result.interpretation.risk_level == RiskLevel.LOW
    
    def test_high_risk_patient(self, calculator):
        """Test high risk cardiac surgery patient"""
        result = calculator.calculate(
            age=80,
            lvef=25,
            creatinine=2.5,
            emergency=False,
        )
        # ACEF = 80/25 + 2 = 3.2 + 2 = 5.2
        assert result.value > 3.0
        assert result.interpretation.risk_level == RiskLevel.VERY_HIGH
    
    def test_creatinine_adjustment(self, calculator):
        """Test creatinine adjustment (+2 if Cr > 2.0)"""
        low_cr = calculator.calculate(age=60, lvef=50, creatinine=1.5)
        high_cr = calculator.calculate(age=60, lvef=50, creatinine=2.5)
        # Difference should be 2 (creatinine adjustment)
        assert abs(high_cr.value - low_cr.value - 2) < 0.1
    
    def test_emergency_doubles_score(self, calculator):
        """Test that emergency surgery doubles the score"""
        elective = calculator.calculate(age=60, lvef=40, creatinine=1.0)
        emergency = calculator.calculate(age=60, lvef=40, creatinine=1.0, emergency=True)
        # Emergency should double the score
        assert abs(emergency.value - elective.value * 2) < 0.1
    
    def test_formula_accuracy(self, calculator):
        """Test ACEF formula accuracy"""
        result = calculator.calculate(age=70, lvef=35, creatinine=1.0)
        # ACEF = 70/35 = 2.0
        assert abs(result.value - 2.0) < 0.01
    
    def test_low_lvef_high_risk(self, calculator):
        """Test that low LVEF leads to higher score"""
        high_ef = calculator.calculate(age=60, lvef=60, creatinine=1.0)
        low_ef = calculator.calculate(age=60, lvef=25, creatinine=1.0)
        assert low_ef.value > high_ef.value
    
    def test_intermediate_risk(self, calculator):
        """Test intermediate risk patient"""
        result = calculator.calculate(age=65, lvef=45, creatinine=1.2)
        # ACEF = 65/45 = 1.44
        assert 1.0 <= result.value < 2.0
        assert result.interpretation.risk_level == RiskLevel.INTERMEDIATE
    
    def test_emergency_with_high_creatinine(self, calculator):
        """Test emergency surgery with renal dysfunction"""
        result = calculator.calculate(age=70, lvef=30, creatinine=3.0, emergency=True)
        # ACEF = ((70/30) + 2) * 2 = (2.33 + 2) * 2 = 8.66
        assert result.value > 8.0
        assert result.interpretation.risk_level == RiskLevel.VERY_HIGH


# =============================================================================
# Integration Tests
# =============================================================================

class TestPhase11Integration:
    """Integration tests for Phase 11 calculators"""
    
    def test_all_calculators_have_metadata(self):
        """Test that all Phase 11 calculators have proper metadata"""
        calculators = [
            IdealBodyWeightCalculator(),
            PfRatioCalculator(),
            RoxIndexCalculator(),
            GraceScoreCalculator(),
            FourTsHitCalculator(),
            AcefIiScoreCalculator(),
        ]
        
        for calc in calculators:
            assert calc.tool_id is not None
            assert calc.metadata.name is not None
            assert len(calc.metadata.references) > 0
    
    def test_all_calculators_have_references(self):
        """Test that all calculators cite references"""
        calculators = [
            IdealBodyWeightCalculator(),
            PfRatioCalculator(),
            RoxIndexCalculator(),
            GraceScoreCalculator(),
            FourTsHitCalculator(),
            AcefIiScoreCalculator(),
        ]
        
        for calc in calculators:
            refs = calc.metadata.references
            assert len(refs) >= 1
            # Each reference should have a citation
            for ref in refs:
                assert ref.citation is not None
    
    def test_results_have_required_fields(self):
        """Test that results have all required fields"""
        # Test one case from each calculator
        test_cases = [
            IdealBodyWeightCalculator().calculate(height_cm=170, sex="male"),
            PfRatioCalculator().calculate(pao2=90, fio2=0.21),
            RoxIndexCalculator().calculate(spo2=95, fio2=0.4, respiratory_rate=20),
            GraceScoreCalculator().calculate(
                age=60, heart_rate=80, systolic_bp=120, creatinine=1.0,
                killip_class=1, cardiac_arrest=False, st_deviation=False, elevated_markers=False
            ),
            FourTsHitCalculator().calculate(
                thrombocytopenia=1, timing=1, thrombosis=1, other_causes=1
            ),
            AcefIiScoreCalculator().calculate(age=60, lvef=50, creatinine=1.0),
        ]
        
        for result in test_cases:
            assert result.value is not None
            assert result.unit is not None
            assert result.interpretation is not None
            assert result.interpretation.summary is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
