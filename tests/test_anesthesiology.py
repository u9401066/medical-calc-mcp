"""
Tests for Anesthesiology/Preoperative Calculators

Tests ASA Physical Status, Mallampati, and RCRI calculators.
"""



class TestAsaPhysicalStatus:
    """Tests for ASA Physical Status Classification."""

    def test_asa_class_1(self) -> None:
        """Test ASA Class I - healthy patient."""
        from src.domain.services.calculators import AsaPhysicalStatusCalculator

        calc = AsaPhysicalStatusCalculator()
        result = calc.calculate(asa_class=1)

        assert result.value is not None
        assert result.value == 1
        assert result.interpretation.summary is not None
        assert "healthy" in result.interpretation.summary.lower()

    def test_asa_class_2(self) -> None:
        """Test ASA Class II - mild systemic disease."""
        from src.domain.services.calculators import AsaPhysicalStatusCalculator

        calc = AsaPhysicalStatusCalculator()
        result = calc.calculate(asa_class=2)

        assert result.value is not None
        assert result.value == 2
        assert result.interpretation.summary is not None
        assert "mild" in result.interpretation.summary.lower()

    def test_asa_class_3(self) -> None:
        """Test ASA Class III - severe systemic disease."""
        from src.domain.services.calculators import AsaPhysicalStatusCalculator

        calc = AsaPhysicalStatusCalculator()
        result = calc.calculate(asa_class=3)

        assert result.value is not None
        assert result.value == 3

    def test_asa_class_4(self) -> None:
        """Test ASA Class IV - life-threatening disease."""
        from src.domain.services.calculators import AsaPhysicalStatusCalculator

        calc = AsaPhysicalStatusCalculator()
        result = calc.calculate(asa_class=4)

        assert result.value is not None
        assert result.value == 4

    def test_asa_class_5(self) -> None:
        """Test ASA Class V - moribund patient."""
        from src.domain.services.calculators import AsaPhysicalStatusCalculator

        calc = AsaPhysicalStatusCalculator()
        result = calc.calculate(asa_class=5)

        assert result.value is not None
        assert result.value == 5

    def test_asa_class_6(self) -> None:
        """Test ASA Class VI - brain-dead organ donor."""
        from src.domain.services.calculators import AsaPhysicalStatusCalculator

        calc = AsaPhysicalStatusCalculator()
        result = calc.calculate(asa_class=6)

        assert result.value is not None
        assert result.value == 6

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import AsaPhysicalStatusCalculator

        calc = AsaPhysicalStatusCalculator()
        assert calc.tool_id == "asa_physical_status"


class TestMallampatiScore:
    """Tests for Mallampati Airway Assessment Score."""

    def test_grade_1(self) -> None:
        """Test Mallampati Grade I - easy intubation."""
        from src.domain.services.calculators import MallampatiScoreCalculator

        calc = MallampatiScoreCalculator()
        result = calc.calculate(mallampati_class=1)

        assert result.value is not None
        assert result.value == 1

    def test_grade_2(self) -> None:
        """Test Mallampati Grade II."""
        from src.domain.services.calculators import MallampatiScoreCalculator

        calc = MallampatiScoreCalculator()
        result = calc.calculate(mallampati_class=2)

        assert result.value is not None
        assert result.value == 2

    def test_grade_3(self) -> None:
        """Test Mallampati Grade III."""
        from src.domain.services.calculators import MallampatiScoreCalculator

        calc = MallampatiScoreCalculator()
        result = calc.calculate(mallampati_class=3)

        assert result.value is not None
        assert result.value == 3

    def test_grade_4(self) -> None:
        """Test Mallampati Grade IV - difficult intubation expected."""
        from src.domain.services.calculators import MallampatiScoreCalculator

        calc = MallampatiScoreCalculator()
        result = calc.calculate(mallampati_class=4)

        assert result.value is not None
        assert result.value == 4

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import MallampatiScoreCalculator

        calc = MallampatiScoreCalculator()
        assert calc.tool_id == "mallampati_score"


class TestRcriCalculator:
    """Tests for Revised Cardiac Risk Index (RCRI/Lee Index)."""

    def test_rcri_zero_points(self) -> None:
        """Test RCRI with no risk factors - low risk."""
        from src.domain.services.calculators import RcriCalculator

        calc = RcriCalculator()
        result = calc.calculate(
            high_risk_surgery=False,
            ischemic_heart_disease=False,
            heart_failure=False,
            cerebrovascular_disease=False,
            insulin_diabetes=False,
            creatinine_above_2=False,
        )

        assert result.value is not None
        assert result.value == 0
        assert result.interpretation.summary is not None
        assert "low" in result.interpretation.summary.lower()

    def test_rcri_one_point(self) -> None:
        """Test RCRI with one risk factor."""
        from src.domain.services.calculators import RcriCalculator

        calc = RcriCalculator()
        result = calc.calculate(
            high_risk_surgery=True,
            ischemic_heart_disease=False,
            heart_failure=False,
            cerebrovascular_disease=False,
            insulin_diabetes=False,
            creatinine_above_2=False,
        )

        assert result.value is not None
        assert result.value == 1

    def test_rcri_multiple_points(self) -> None:
        """Test RCRI with multiple risk factors."""
        from src.domain.services.calculators import RcriCalculator

        calc = RcriCalculator()
        result = calc.calculate(
            high_risk_surgery=True,
            ischemic_heart_disease=True,
            heart_failure=True,
            cerebrovascular_disease=False,
            insulin_diabetes=True,
            creatinine_above_2=True,
        )

        assert result.value is not None
        assert result.value == 5
        assert result.value is not None
        assert result.interpretation.summary is not None
        assert "high" in result.interpretation.summary.lower() or result.value >= 3

    def test_rcri_max_points(self) -> None:
        """Test RCRI with all risk factors - highest risk."""
        from src.domain.services.calculators import RcriCalculator

        calc = RcriCalculator()
        result = calc.calculate(
            high_risk_surgery=True,
            ischemic_heart_disease=True,
            heart_failure=True,
            cerebrovascular_disease=True,
            insulin_diabetes=True,
            creatinine_above_2=True,
        )

        assert result.value is not None
        assert result.value == 6

    def test_has_references(self) -> None:
        """Test that RCRI includes Lee et al. reference."""
        from src.domain.services.calculators import RcriCalculator

        calc = RcriCalculator()
        result = calc.calculate(
            high_risk_surgery=False,
            ischemic_heart_disease=False,
            heart_failure=False,
            cerebrovascular_disease=False,
            insulin_diabetes=False,
            creatinine_above_2=False,
        )

        assert result.references is not None
        assert len(result.references) > 0

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import RcriCalculator

        calc = RcriCalculator()
        assert calc.tool_id == "rcri"


class TestApfelPonvCalculator:
    """Tests for Apfel Score PONV Risk Calculator."""

    def test_zero_risk_factors(self) -> None:
        """Test Apfel score 0 - very low risk (~10%)."""
        from src.domain.services.calculators import ApfelPonvCalculator

        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=False,
            history_motion_sickness_or_ponv=False,
            non_smoker=False,  # Smoker
            postoperative_opioids=False
        )

        assert result.value is not None
        assert result.value == 0
        assert result.calculation_details is not None
        assert result.calculation_details["ponv_risk_percent"] == 10.0
        assert result.interpretation.summary is not None
        assert "very low" in result.interpretation.summary.lower()

    def test_one_risk_factor(self) -> None:
        """Test Apfel score 1 - low risk (~21%)."""
        from src.domain.services.calculators import ApfelPonvCalculator

        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=True,
            history_motion_sickness_or_ponv=False,
            non_smoker=False,
            postoperative_opioids=False
        )

        assert result.value is not None
        assert result.value == 1
        assert result.calculation_details is not None
        assert result.calculation_details["ponv_risk_percent"] == 21.0

    def test_two_risk_factors(self) -> None:
        """Test Apfel score 2 - moderate risk (~39%)."""
        from src.domain.services.calculators import ApfelPonvCalculator

        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=True,
            history_motion_sickness_or_ponv=True,
            non_smoker=False,
            postoperative_opioids=False
        )

        assert result.value is not None
        assert result.value == 2
        assert result.calculation_details is not None
        assert result.calculation_details["ponv_risk_percent"] == 39.0
        assert result.interpretation.summary is not None
        assert "moderate" in result.interpretation.summary.lower()

    def test_three_risk_factors(self) -> None:
        """Test Apfel score 3 - high risk (~61%)."""
        from src.domain.services.calculators import ApfelPonvCalculator

        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=True,
            history_motion_sickness_or_ponv=True,
            non_smoker=True,
            postoperative_opioids=False
        )

        assert result.value is not None
        assert result.value == 3
        assert result.calculation_details is not None
        assert result.calculation_details["ponv_risk_percent"] == 61.0
        assert result.interpretation.summary is not None
        assert "high" in result.interpretation.summary.lower()

    def test_four_risk_factors(self) -> None:
        """Test Apfel score 4 - very high risk (~79%)."""
        from src.domain.services.calculators import ApfelPonvCalculator

        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=True,
            history_motion_sickness_or_ponv=True,
            non_smoker=True,
            postoperative_opioids=True
        )

        assert result.value is not None
        assert result.value == 4
        assert result.calculation_details is not None
        assert result.calculation_details["ponv_risk_percent"] == 79.0
        assert result.interpretation.summary is not None
        assert "very high" in result.interpretation.summary.lower()

    def test_typical_high_risk_patient(self) -> None:
        """Test typical high-risk patient: female, non-smoker, with opioids."""
        from src.domain.services.calculators import ApfelPonvCalculator

        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=True,
            history_motion_sickness_or_ponv=False,
            non_smoker=True,
            postoperative_opioids=True
        )

        assert result.value is not None
        assert result.value == 3
        # Should recommend multi-modal prophylaxis
        assert result.interpretation.recommendations is not None
        assert any("multi" in rec.lower() for rec in result.interpretation.recommendations)

    def test_risk_factors_tracked(self) -> None:
        """Test that risk factors are tracked in calculation details."""
        from src.domain.services.calculators import ApfelPonvCalculator

        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=True,
            history_motion_sickness_or_ponv=True,
            non_smoker=False,
            postoperative_opioids=False
        )

        assert result.calculation_details is not None
        factors = result.calculation_details["risk_factors_present"]
        assert "Female gender" in factors
        assert "History of motion sickness or PONV" in factors
        assert len(factors) == 2

    def test_has_references(self) -> None:
        """Test that Apfel score includes original reference."""
        from src.domain.services.calculators import ApfelPonvCalculator

        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=False,
            history_motion_sickness_or_ponv=False,
            non_smoker=False,
            postoperative_opioids=False
        )

        assert result.references is not None
        assert len(result.references) >= 1
        # Check for Apfel 1999 reference
        ref_text = str(result.references[0])
        assert "Apfel" in ref_text or "10485781" in ref_text

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import ApfelPonvCalculator

        calc = ApfelPonvCalculator()
        assert calc.tool_id == "apfel_ponv"

    def test_metadata(self) -> None:
        """Test that metadata is properly configured."""
        from src.domain.services.calculators import ApfelPonvCalculator

        calc = ApfelPonvCalculator()
        assert calc.name == "Apfel Score for PONV"
        assert "anesthesiology" in [s.value for s in calc.metadata.high_level.specialties]


class TestStopBangCalculator:
    """Tests for STOP-BANG OSA Screening Calculator."""

    def test_low_risk(self) -> None:
        """Test STOP-BANG score 0-2 - low risk for OSA."""
        from src.domain.services.calculators import StopBangCalculator

        calc = StopBangCalculator()
        result = calc.calculate(
            snoring=True,
            tired=False,
            observed_apnea=False,
            high_blood_pressure=False,
            bmi_over_35=False,
            age_over_50=False,
            neck_over_40cm=False,
            male_gender=True
        )

        assert result.value is not None
        assert result.value == 2
        assert result.interpretation.summary is not None
        assert "low" in result.interpretation.summary.lower()

    def test_intermediate_risk(self) -> None:
        """Test STOP-BANG score 3-4 - intermediate risk for OSA."""
        from src.domain.services.calculators import StopBangCalculator

        calc = StopBangCalculator()
        result = calc.calculate(
            snoring=True,
            tired=True,
            observed_apnea=False,
            high_blood_pressure=True,
            bmi_over_35=False,
            age_over_50=False,
            neck_over_40cm=False,
            male_gender=False
        )

        assert result.value is not None
        assert result.value == 3
        assert result.interpretation.summary is not None
        assert "intermediate" in result.interpretation.summary.lower() or "moderate" in result.interpretation.summary.lower()

    def test_high_risk(self) -> None:
        """Test STOP-BANG score 5-8 - high risk for OSA."""
        from src.domain.services.calculators import StopBangCalculator

        calc = StopBangCalculator()
        result = calc.calculate(
            snoring=True,
            tired=True,
            observed_apnea=True,
            high_blood_pressure=True,
            bmi_over_35=True,
            age_over_50=True,
            neck_over_40cm=False,
            male_gender=True
        )

        assert result.value is not None
        assert result.value == 7
        assert result.interpretation.summary is not None
        assert "high" in result.interpretation.summary.lower()

    def test_max_score(self) -> None:
        """Test STOP-BANG maximum score of 8."""
        from src.domain.services.calculators import StopBangCalculator

        calc = StopBangCalculator()
        result = calc.calculate(
            snoring=True,
            tired=True,
            observed_apnea=True,
            high_blood_pressure=True,
            bmi_over_35=True,
            age_over_50=True,
            neck_over_40cm=True,
            male_gender=True
        )

        assert result.value is not None
        assert result.value == 8
        assert result.interpretation.summary is not None
        assert "high" in result.interpretation.summary.lower()

    def test_zero_score(self) -> None:
        """Test STOP-BANG score of 0."""
        from src.domain.services.calculators import StopBangCalculator

        calc = StopBangCalculator()
        result = calc.calculate(
            snoring=False,
            tired=False,
            observed_apnea=False,
            high_blood_pressure=False,
            bmi_over_35=False,
            age_over_50=False,
            neck_over_40cm=False,
            male_gender=False
        )

        assert result.value is not None
        assert result.value == 0

    def test_has_references(self) -> None:
        """Test that STOP-BANG includes Chung 2008 reference."""
        from src.domain.services.calculators import StopBangCalculator

        calc = StopBangCalculator()
        result = calc.calculate(
            snoring=True,
            tired=False,
            observed_apnea=False,
            high_blood_pressure=False,
            bmi_over_35=False,
            age_over_50=False,
            neck_over_40cm=False,
            male_gender=False
        )

        assert result.references is not None
        assert len(result.references) >= 1
        ref_text = str(result.references[0])
        assert "Chung" in ref_text or "18431116" in ref_text

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import StopBangCalculator

        calc = StopBangCalculator()
        assert calc.tool_id == "stop_bang"


class TestAldreteScoreCalculator:
    """Tests for Aldrete Score Post-Anesthesia Recovery Calculator."""

    def test_ready_for_discharge(self) -> None:
        """Test Aldrete score >= 9 - ready for PACU discharge."""
        from src.domain.services.calculators import AldreteScoreCalculator

        calc = AldreteScoreCalculator()
        result = calc.calculate(
            activity=2,
            respiration=2,
            circulation=2,
            consciousness=2,
            oxygen_saturation=2
        )

        assert result.value is not None
        assert result.value == 10
        assert result.interpretation.summary is not None
        assert "discharge" in result.interpretation.summary.lower()

    def test_need_monitoring(self) -> None:
        """Test Aldrete score < 9 - continue PACU monitoring."""
        from src.domain.services.calculators import AldreteScoreCalculator

        calc = AldreteScoreCalculator()
        result = calc.calculate(
            activity=1,
            respiration=1,
            circulation=2,
            consciousness=1,
            oxygen_saturation=1
        )

        assert result.value is not None
        assert result.value == 6
        assert result.value is not None
        assert result.value < 9

    def test_minimal_recovery(self) -> None:
        """Test Aldrete score with minimal recovery."""
        from src.domain.services.calculators import AldreteScoreCalculator

        calc = AldreteScoreCalculator()
        result = calc.calculate(
            activity=0,
            respiration=0,
            circulation=1,
            consciousness=0,
            oxygen_saturation=0
        )

        assert result.value is not None
        assert result.value == 1

    def test_nine_threshold(self) -> None:
        """Test Aldrete score exactly at 9 threshold."""
        from src.domain.services.calculators import AldreteScoreCalculator

        calc = AldreteScoreCalculator()
        result = calc.calculate(
            activity=2,
            respiration=2,
            circulation=2,
            consciousness=2,
            oxygen_saturation=1
        )

        assert result.value is not None
        assert result.value == 9

    def test_max_score(self) -> None:
        """Test Aldrete maximum score of 10."""
        from src.domain.services.calculators import AldreteScoreCalculator

        calc = AldreteScoreCalculator()
        result = calc.calculate(
            activity=2,
            respiration=2,
            circulation=2,
            consciousness=2,
            oxygen_saturation=2
        )

        assert result.value is not None
        assert result.value == 10

    def test_has_references(self) -> None:
        """Test that Aldrete score includes original 1970 reference."""
        from src.domain.services.calculators import AldreteScoreCalculator

        calc = AldreteScoreCalculator()
        result = calc.calculate(
            activity=2,
            respiration=2,
            circulation=2,
            consciousness=2,
            oxygen_saturation=2
        )

        assert result.references is not None
        assert len(result.references) >= 1
        ref_text = str(result.references[0])
        assert "Aldrete" in ref_text or "5534693" in ref_text

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import AldreteScoreCalculator

        calc = AldreteScoreCalculator()
        assert calc.tool_id == "aldrete_score"
