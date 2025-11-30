"""Tests for Nephrology Calculators"""
import pytest


class TestCkdEpi2021Calculator:
    def test_ckd_epi_basic(self):
        from src.domain.services.calculators import CkdEpi2021Calculator
        calc = CkdEpi2021Calculator()
        result = calc.calculate(age=50, sex="male", serum_creatinine=1.0)
        assert result.value > 0
        assert "mL/min" in str(result.unit)

    def test_ckd_epi_female(self):
        from src.domain.services.calculators import CkdEpi2021Calculator
        calc = CkdEpi2021Calculator()
        result = calc.calculate(age=50, sex="female", serum_creatinine=1.0)
        assert result.value > 0

    def test_tool_id(self):
        from src.domain.services.calculators import CkdEpi2021Calculator
        calc = CkdEpi2021Calculator()
        assert calc.tool_id == "ckd_epi_2021"


class TestKdigoAkiCalculator:
    """Tests for KDIGO AKI Staging calculator"""
    
    def test_no_aki_normal_creatinine(self):
        """Test no AKI when creatinine is normal"""
        from src.domain.services.calculators import KdigoAkiCalculator
        calc = KdigoAkiCalculator()
        result = calc.calculate(
            current_creatinine=1.0,
            baseline_creatinine=1.0,
        )
        assert result.value == 0
        assert "No AKI" in result.interpretation.summary
    
    def test_stage_1_by_ratio(self):
        """Test Stage 1 by creatinine ratio (1.5-1.9x)"""
        from src.domain.services.calculators import KdigoAkiCalculator
        calc = KdigoAkiCalculator()
        result = calc.calculate(
            current_creatinine=1.6,
            baseline_creatinine=1.0,  # 1.6x baseline
        )
        assert result.value == 1
        assert "Stage 1" in result.interpretation.summary
    
    def test_stage_1_by_absolute_increase(self):
        """Test Stage 1 by ≥0.3 mg/dL increase in 48h"""
        from src.domain.services.calculators import KdigoAkiCalculator
        calc = KdigoAkiCalculator()
        result = calc.calculate(
            current_creatinine=1.3,
            creatinine_increase_48h=0.4,  # ≥0.3 increase
        )
        assert result.value == 1
    
    def test_stage_2_by_ratio(self):
        """Test Stage 2 by creatinine ratio (2.0-2.9x)"""
        from src.domain.services.calculators import KdigoAkiCalculator
        calc = KdigoAkiCalculator()
        result = calc.calculate(
            current_creatinine=2.4,
            baseline_creatinine=1.0,  # 2.4x baseline
        )
        assert result.value == 2
        assert "Stage 2" in result.interpretation.summary
    
    def test_stage_3_by_ratio(self):
        """Test Stage 3 by creatinine ratio (≥3.0x)"""
        from src.domain.services.calculators import KdigoAkiCalculator
        calc = KdigoAkiCalculator()
        result = calc.calculate(
            current_creatinine=3.5,
            baseline_creatinine=1.0,  # 3.5x baseline
        )
        assert result.value == 3
        assert "Stage 3" in result.interpretation.summary
    
    def test_stage_3_by_absolute_value(self):
        """Test Stage 3 by absolute creatinine ≥4.0"""
        from src.domain.services.calculators import KdigoAkiCalculator
        calc = KdigoAkiCalculator()
        result = calc.calculate(
            current_creatinine=4.5,  # ≥4.0 mg/dL
        )
        assert result.value == 3
    
    def test_stage_3_by_rrt(self):
        """Test Stage 3 automatically when on RRT"""
        from src.domain.services.calculators import KdigoAkiCalculator
        calc = KdigoAkiCalculator()
        result = calc.calculate(
            current_creatinine=2.0,
            baseline_creatinine=1.0,  # Would be Stage 2 by ratio
            on_rrt=True,  # But RRT = Stage 3
        )
        assert result.value == 3
        assert "RRT" in result.interpretation.summary or "Stage 3" in result.interpretation.summary
    
    def test_stage_1_by_urine_output(self):
        """Test Stage 1 by UO <0.5 mL/kg/h for 6-12h"""
        from src.domain.services.calculators import KdigoAkiCalculator
        calc = KdigoAkiCalculator()
        result = calc.calculate(
            current_creatinine=1.0,  # Normal Cr
            urine_output_ml_kg_h=0.4,
            urine_output_duration_hours=8,
        )
        assert result.value == 1
    
    def test_stage_2_by_urine_output(self):
        """Test Stage 2 by UO <0.5 mL/kg/h for ≥12h"""
        from src.domain.services.calculators import KdigoAkiCalculator
        calc = KdigoAkiCalculator()
        result = calc.calculate(
            current_creatinine=1.0,
            urine_output_ml_kg_h=0.4,
            urine_output_duration_hours=14,
        )
        assert result.value == 2
    
    def test_stage_3_by_anuria(self):
        """Test Stage 3 by anuria for ≥12h"""
        from src.domain.services.calculators import KdigoAkiCalculator
        calc = KdigoAkiCalculator()
        result = calc.calculate(
            current_creatinine=1.5,
            urine_output_ml_kg_h=0.05,  # Near anuria
            urine_output_duration_hours=14,
        )
        assert result.value == 3
    
    def test_higher_stage_wins(self):
        """Test that higher stage from Cr or UO is used"""
        from src.domain.services.calculators import KdigoAkiCalculator
        calc = KdigoAkiCalculator()
        result = calc.calculate(
            current_creatinine=1.8,
            baseline_creatinine=1.0,  # Stage 1 by Cr
            urine_output_ml_kg_h=0.4,
            urine_output_duration_hours=14,  # Stage 2 by UO
        )
        assert result.value == 2  # Higher stage wins
    
    def test_references_include_kdigo(self):
        """Test that references include KDIGO guideline"""
        from src.domain.services.calculators import KdigoAkiCalculator
        calc = KdigoAkiCalculator()
        refs = calc.references
        dois = [r.doi for r in refs if r.doi]
        assert "10.1038/kisup.2012.1" in dois  # KDIGO 2012
    
    def test_tool_id(self):
        from src.domain.services.calculators import KdigoAkiCalculator
        assert KdigoAkiCalculator().tool_id == "kdigo_aki"
