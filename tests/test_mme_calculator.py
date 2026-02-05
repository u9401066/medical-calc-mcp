"""
Tests for MME Calculator (Morphine Milligram Equivalent)

Reference:
    Dowell D, Haegerich TM, Chou R. CDC Guideline for Prescribing Opioids
    for Chronic Pain — United States, 2016. MMWR Recomm Rep. 2016;65(1):1-49.
    PMID: 26987082.

    Dowell D, Ragan KR, Jones CM, Baldwin GT, Chou R. CDC Clinical Practice
    Guideline for Prescribing Opioids for Pain — United States, 2022.
    MMWR Recomm Rep. 2022;71(3):1-95. PMID: 36327391.
"""

import pytest

from src.domain.services.calculators.mme_calculator import (
    MMECalculator,
    OPIOID_MME_FACTORS,
)
from src.domain.value_objects.interpretation import RiskLevel, Severity


@pytest.fixture
def calculator() -> MMECalculator:
    """Provide an MME calculator instance."""
    return MMECalculator()


class TestMMEBasicConversions:
    """Test basic opioid to MME conversions."""

    def test_morphine_30mg(self, calculator: MMECalculator) -> None:
        """Morphine 30mg = 30 MME (factor 1.0)."""
        result = calculator.calculate(opioid_name="morphine", daily_dose_mg=30)
        assert result.value == 30
        assert result.calculation_details["conversion_factor"] == 1.0

    def test_morphine_zero_dose(self, calculator: MMECalculator) -> None:
        """Zero dose = 0 MME."""
        result = calculator.calculate(opioid_name="morphine", daily_dose_mg=0)
        assert result.value == 0
        assert result.interpretation.stage == "None"

    def test_oxycodone_20mg(self, calculator: MMECalculator) -> None:
        """Oxycodone 20mg = 30 MME (factor 1.5)."""
        result = calculator.calculate(opioid_name="oxycodone", daily_dose_mg=20)
        assert result.value == 30
        assert result.calculation_details["conversion_factor"] == 1.5

    def test_hydrocodone_40mg(self, calculator: MMECalculator) -> None:
        """Hydrocodone 40mg = 40 MME (factor 1.0)."""
        result = calculator.calculate(opioid_name="hydrocodone", daily_dose_mg=40)
        assert result.value == 40
        assert result.calculation_details["conversion_factor"] == 1.0

    def test_hydromorphone_8mg(self, calculator: MMECalculator) -> None:
        """Hydromorphone 8mg = 32 MME (factor 4.0)."""
        result = calculator.calculate(opioid_name="hydromorphone", daily_dose_mg=8)
        assert result.value == 32
        assert result.calculation_details["conversion_factor"] == 4.0

    def test_oxymorphone_10mg(self, calculator: MMECalculator) -> None:
        """Oxymorphone 10mg = 30 MME (factor 3.0)."""
        result = calculator.calculate(opioid_name="oxymorphone", daily_dose_mg=10)
        assert result.value == 30

    def test_codeine_120mg(self, calculator: MMECalculator) -> None:
        """Codeine 120mg = 18 MME (factor 0.15)."""
        result = calculator.calculate(opioid_name="codeine", daily_dose_mg=120)
        assert result.value == 18

    def test_tramadol_200mg(self, calculator: MMECalculator) -> None:
        """Tramadol 200mg = 20 MME (factor 0.1)."""
        result = calculator.calculate(opioid_name="tramadol", daily_dose_mg=200)
        assert result.value == 20

    def test_tapentadol_100mg(self, calculator: MMECalculator) -> None:
        """Tapentadol 100mg = 40 MME (factor 0.4)."""
        result = calculator.calculate(opioid_name="tapentadol", daily_dose_mg=100)
        assert result.value == 40


class TestFentanylTransdermal:
    """Test fentanyl transdermal patch conversions."""

    def test_fentanyl_25mcg_hr(self, calculator: MMECalculator) -> None:
        """Fentanyl 25mcg/hr = 60 MME (factor 2.4)."""
        result = calculator.calculate(
            opioid_name="fentanyl_transdermal", fentanyl_mcg_hr=25
        )
        assert result.value == 60
        assert result.calculation_details["dose_unit"] == "mcg/hr"

    def test_fentanyl_50mcg_hr(self, calculator: MMECalculator) -> None:
        """Fentanyl 50mcg/hr = 120 MME."""
        result = calculator.calculate(
            opioid_name="fentanyl_transdermal", fentanyl_mcg_hr=50
        )
        assert result.value == 120

    def test_fentanyl_100mcg_hr(self, calculator: MMECalculator) -> None:
        """Fentanyl 100mcg/hr = 240 MME (very high)."""
        result = calculator.calculate(
            opioid_name="fentanyl_transdermal", fentanyl_mcg_hr=100
        )
        assert result.value == 240
        assert result.interpretation.risk_level == RiskLevel.HIGH

    def test_fentanyl_requires_mcg_hr_parameter(
        self, calculator: MMECalculator
    ) -> None:
        """Fentanyl transdermal requires fentanyl_mcg_hr."""
        with pytest.raises(ValueError, match="fentanyl_mcg_hr must be provided"):
            calculator.calculate(opioid_name="fentanyl_transdermal", daily_dose_mg=25)


class TestMethadone:
    """Test methadone dose-dependent conversions."""

    def test_methadone_10mg_low_range(self, calculator: MMECalculator) -> None:
        """Methadone 10mg (1-20 range) = 40 MME (factor 4.0)."""
        result = calculator.calculate(
            opioid_name="methadone",
            daily_dose_mg=10,
            methadone_dose_range="1_20",
        )
        assert result.value == 40
        assert result.calculation_details["conversion_factor"] == 4.0

    def test_methadone_30mg_mid_range(self, calculator: MMECalculator) -> None:
        """Methadone 30mg (21-40 range) = 240 MME (factor 8.0)."""
        result = calculator.calculate(
            opioid_name="methadone",
            daily_dose_mg=30,
            methadone_dose_range="21_40",
        )
        assert result.value == 240

    def test_methadone_50mg_high_range(self, calculator: MMECalculator) -> None:
        """Methadone 50mg (41-60 range) = 500 MME (factor 10.0)."""
        result = calculator.calculate(
            opioid_name="methadone",
            daily_dose_mg=50,
            methadone_dose_range="41_60",
        )
        assert result.value == 500

    def test_methadone_80mg_very_high(self, calculator: MMECalculator) -> None:
        """Methadone 80mg (>60 range) = 960 MME (factor 12.0)."""
        result = calculator.calculate(
            opioid_name="methadone",
            daily_dose_mg=80,
            methadone_dose_range="over_60",
        )
        assert result.value == 960

    def test_methadone_auto_select_range(self, calculator: MMECalculator) -> None:
        """Methadone auto-selects range when not specified."""
        # 15mg should use 1-20 range
        result = calculator.calculate(opioid_name="methadone", daily_dose_mg=15)
        assert result.calculation_details["methadone_dose_range"] == "1_20"

        # 35mg should use 21-40 range
        result2 = calculator.calculate(opioid_name="methadone", daily_dose_mg=35)
        assert result2.calculation_details["methadone_dose_range"] == "21_40"


class TestBuprenorphine:
    """Test buprenorphine conversions."""

    def test_buprenorphine_transdermal(self, calculator: MMECalculator) -> None:
        """Buprenorphine transdermal 10mcg/hr equivalent."""
        # Buprenorphine transdermal: factor ~12.6
        result = calculator.calculate(
            opioid_name="buprenorphine_transdermal", daily_dose_mg=5
        )
        assert result.value == 63  # 5 * 12.6

    def test_buprenorphine_sublingual(self, calculator: MMECalculator) -> None:
        """Buprenorphine sublingual 8mg."""
        result = calculator.calculate(
            opioid_name="buprenorphine_sublingual", daily_dose_mg=8
        )
        assert result.value == 80  # 8 * 10


class TestCustomConversionFactor:
    """Test custom conversion factor override."""

    def test_other_opioid_requires_custom_factor(
        self, calculator: MMECalculator
    ) -> None:
        """'other' opioid requires custom conversion factor."""
        with pytest.raises(ValueError, match="custom_conversion_factor must be provided"):
            calculator.calculate(opioid_name="other", daily_dose_mg=10)

    def test_other_opioid_with_custom_factor(
        self, calculator: MMECalculator
    ) -> None:
        """'other' opioid uses custom factor."""
        result = calculator.calculate(
            opioid_name="other",
            daily_dose_mg=10,
            custom_conversion_factor=2.5,
        )
        assert result.value == 25

    def test_override_standard_opioid_factor(
        self, calculator: MMECalculator
    ) -> None:
        """Override standard opioid conversion factor."""
        # Normally morphine factor is 1.0
        result = calculator.calculate(
            opioid_name="morphine",
            daily_dose_mg=10,
            custom_conversion_factor=1.5,
        )
        assert result.value == 15


class TestRiskStratification:
    """Test MME risk stratification thresholds."""

    def test_zero_mme_no_risk(self, calculator: MMECalculator) -> None:
        """0 MME = no opioid risk."""
        result = calculator.calculate(opioid_name="morphine", daily_dose_mg=0)
        assert result.interpretation.risk_level == RiskLevel.VERY_LOW
        assert result.interpretation.stage == "None"

    def test_low_mme_under_20(self, calculator: MMECalculator) -> None:
        """<20 MME = low risk."""
        result = calculator.calculate(opioid_name="morphine", daily_dose_mg=15)
        assert result.interpretation.risk_level == RiskLevel.VERY_LOW
        assert "Low" in result.interpretation.stage

    def test_moderate_mme_20_49(self, calculator: MMECalculator) -> None:
        """20-49 MME = moderate risk."""
        result = calculator.calculate(opioid_name="morphine", daily_dose_mg=30)
        assert result.interpretation.risk_level == RiskLevel.LOW
        assert "Moderate" in result.interpretation.stage

    def test_elevated_mme_50_89(self, calculator: MMECalculator) -> None:
        """50-89 MME = elevated risk."""
        result = calculator.calculate(opioid_name="morphine", daily_dose_mg=60)
        assert result.interpretation.risk_level == RiskLevel.INTERMEDIATE
        assert "Elevated" in result.interpretation.stage

    def test_high_mme_90_plus(self, calculator: MMECalculator) -> None:
        """≥90 MME = high risk."""
        result = calculator.calculate(opioid_name="morphine", daily_dose_mg=100)
        assert result.interpretation.risk_level == RiskLevel.HIGH
        assert "High" in result.interpretation.stage
        assert result.interpretation.severity == Severity.SEVERE


class TestRecommendations:
    """Test MME-based recommendations."""

    def test_low_dose_continue_monitoring(self, calculator: MMECalculator) -> None:
        """Low dose: monitor for efficacy."""
        result = calculator.calculate(opioid_name="morphine", daily_dose_mg=10)
        recommendations = result.interpretation.recommendations
        assert any("monitor" in r.lower() for r in recommendations)

    def test_moderate_dose_naloxone_discussion(
        self, calculator: MMECalculator
    ) -> None:
        """Moderate dose: discuss naloxone."""
        result = calculator.calculate(opioid_name="morphine", daily_dose_mg=30)
        recommendations = result.interpretation.recommendations
        assert any("naloxone" in r.lower() for r in recommendations)

    def test_elevated_dose_naloxone_recommended(
        self, calculator: MMECalculator
    ) -> None:
        """Elevated dose: naloxone strongly recommended."""
        result = calculator.calculate(opioid_name="morphine", daily_dose_mg=60)
        recommendations = result.interpretation.recommendations
        assert any("naloxone" in r.lower() for r in recommendations)

    def test_high_dose_naloxone_mandatory(self, calculator: MMECalculator) -> None:
        """High dose: naloxone mandatory."""
        result = calculator.calculate(opioid_name="morphine", daily_dose_mg=100)
        recommendations = result.interpretation.recommendations
        assert any("naloxone" in r.lower() and "mandatory" in r.lower() for r in recommendations)

    def test_high_dose_warnings(self, calculator: MMECalculator) -> None:
        """High dose: warnings about overdose risk."""
        result = calculator.calculate(opioid_name="morphine", daily_dose_mg=120)
        warnings = result.interpretation.warnings
        assert any("overdose" in w.lower() or "risk" in w.lower() for w in warnings)


class TestMultipleOpioids:
    """Test calculate_multiple for polypharmacy scenarios."""

    def test_two_opioids(self, calculator: MMECalculator) -> None:
        """Calculate total from two opioids."""
        opioids = [
            {"name": "morphine", "daily_dose_mg": 30},
            {"name": "oxycodone", "daily_dose_mg": 10},
        ]
        result = calculator.calculate_multiple(opioids)
        # 30 * 1.0 + 10 * 1.5 = 45
        assert result.value == 45
        assert result.calculation_details["opioid_count"] == 2

    def test_three_opioids_mixed(self, calculator: MMECalculator) -> None:
        """Three opioids with different factors."""
        opioids = [
            {"name": "morphine", "daily_dose_mg": 20},
            {"name": "hydrocodone", "daily_dose_mg": 20},
            {"name": "oxycodone", "daily_dose_mg": 10},
        ]
        result = calculator.calculate_multiple(opioids)
        # 20*1 + 20*1 + 10*1.5 = 55
        assert result.value == 55

    def test_with_fentanyl_patch(self, calculator: MMECalculator) -> None:
        """Include fentanyl patch in total."""
        opioids = [
            {"name": "fentanyl_transdermal", "fentanyl_mcg_hr": 25},
            {"name": "oxycodone", "daily_dose_mg": 10},
        ]
        result = calculator.calculate_multiple(opioids)
        # 25*2.4 + 10*1.5 = 60 + 15 = 75
        assert result.value == 75

    def test_empty_list_error(self, calculator: MMECalculator) -> None:
        """Empty opioid list raises error."""
        with pytest.raises(ValueError, match="At least one opioid"):
            calculator.calculate_multiple([])

    def test_itemized_breakdown(self, calculator: MMECalculator) -> None:
        """Result includes itemized breakdown."""
        opioids = [
            {"name": "morphine", "daily_dose_mg": 20},
            {"name": "oxycodone", "daily_dose_mg": 10},
        ]
        result = calculator.calculate_multiple(opioids)
        breakdown = result.calculation_details["individual_opioids"]
        assert len(breakdown) == 2
        assert breakdown[0]["opioid"] == "morphine"
        assert breakdown[0]["mme"] == 20
        assert breakdown[1]["opioid"] == "oxycodone"
        assert breakdown[1]["mme"] == 15


class TestClinicalScenarios:
    """Test realistic clinical scenarios."""

    def test_scenario_chronic_pain_patient(self, calculator: MMECalculator) -> None:
        """Chronic pain patient on moderate opioid therapy."""
        # Patient on oxycodone 10mg TID = 30mg/day
        result = calculator.calculate(opioid_name="oxycodone", daily_dose_mg=30)
        # 30 * 1.5 = 45 MME
        assert result.value == 45
        assert result.interpretation.risk_level == RiskLevel.LOW

    def test_scenario_postop_patient(self, calculator: MMECalculator) -> None:
        """Post-operative patient with short-term opioid."""
        result = calculator.calculate(opioid_name="hydrocodone", daily_dose_mg=20)
        assert result.value == 20
        # In moderate range

    def test_scenario_cancer_pain_high_dose(self, calculator: MMECalculator) -> None:
        """Cancer pain patient on high-dose opioids."""
        # Fentanyl patch 75mcg/hr
        result = calculator.calculate(
            opioid_name="fentanyl_transdermal", fentanyl_mcg_hr=75
        )
        # 75 * 2.4 = 180 MME
        assert result.value == 180
        assert result.interpretation.risk_level == RiskLevel.HIGH

    def test_scenario_polypharmacy(self, calculator: MMECalculator) -> None:
        """Patient on multiple opioids (common in escalation)."""
        opioids = [
            {"name": "fentanyl_transdermal", "fentanyl_mcg_hr": 50},
            {"name": "oxycodone", "daily_dose_mg": 20},  # Breakthrough
        ]
        result = calculator.calculate_multiple(opioids)
        # 50*2.4 + 20*1.5 = 120 + 30 = 150
        assert result.value == 150
        assert result.interpretation.severity == Severity.SEVERE

    def test_scenario_prescriber_threshold_check(
        self, calculator: MMECalculator
    ) -> None:
        """Prescriber checking if adding PRN would exceed threshold."""
        # Current: oxycodone 40mg/day = 60 MME
        current = calculator.calculate(opioid_name="oxycodone", daily_dose_mg=40)
        assert current.value == 60  # Already at threshold

        # Adding hydrocodone 10mg PRN = 10 MME more
        total = calculator.calculate_multiple(
            [
                {"name": "oxycodone", "daily_dose_mg": 40},
                {"name": "hydrocodone", "daily_dose_mg": 10},
            ]
        )
        assert total.value == 70  # Now 70 MME, approaching 90


class TestMMEMetadata:
    """Test MME calculator metadata and references."""

    def test_tool_id(self, calculator: MMECalculator) -> None:
        """Test calculator tool_id."""
        assert calculator.tool_id == "mme_calculator"

    def test_metadata_name(self, calculator: MMECalculator) -> None:
        """Test metadata name."""
        assert "MME" in calculator.metadata.low_level.name

    def test_references_cdc_guidelines(self, calculator: MMECalculator) -> None:
        """Test CDC guideline references."""
        refs = calculator.references
        pmids = [ref.pmid for ref in refs]
        assert "26987082" in pmids  # CDC 2016
        assert "36327391" in pmids  # CDC 2022

    def test_unit_is_mme_day(self, calculator: MMECalculator) -> None:
        """Test result unit is MME/day."""
        result = calculator.calculate(opioid_name="morphine", daily_dose_mg=30)
        assert result.unit.value == "MME/day"


class TestHelperMethods:
    """Test helper methods."""

    def test_get_conversion_factor(self, calculator: MMECalculator) -> None:
        """Test get_conversion_factor method."""
        assert calculator.get_conversion_factor("morphine") == 1.0
        assert calculator.get_conversion_factor("oxycodone") == 1.5
        assert calculator.get_conversion_factor("unknown_opioid") is None

    def test_list_supported_opioids(self, calculator: MMECalculator) -> None:
        """Test list_supported_opioids method."""
        opioids = calculator.list_supported_opioids()
        assert len(opioids) > 10
        names = [o["opioid"] for o in opioids]
        assert "morphine" in names
        assert "oxycodone" in names
        assert "fentanyl_transdermal" in names


class TestEdgeCases:
    """Test edge cases."""

    def test_negative_dose_error(self, calculator: MMECalculator) -> None:
        """Negative dose raises error."""
        with pytest.raises(ValueError):
            calculator.calculate(opioid_name="morphine", daily_dose_mg=-10)

    def test_very_small_dose(self, calculator: MMECalculator) -> None:
        """Very small dose calculation."""
        result = calculator.calculate(opioid_name="codeine", daily_dose_mg=10)
        # 10 * 0.15 = 1.5
        assert result.value == 1.5

    def test_rounding(self, calculator: MMECalculator) -> None:
        """MME values are rounded to 1 decimal."""
        result = calculator.calculate(opioid_name="tramadol", daily_dose_mg=33)
        # 33 * 0.1 = 3.3
        assert result.value == 3.3

    def test_calculation_details_formula(self, calculator: MMECalculator) -> None:
        """Calculation details include formula string."""
        result = calculator.calculate(opioid_name="oxycodone", daily_dose_mg=20)
        assert "formula" in result.calculation_details
        assert "20" in result.calculation_details["formula"]
        assert "1.5" in result.calculation_details["formula"]

    def test_methadone_zero_dose_error(self, calculator: MMECalculator) -> None:
        """Methadone with zero dose raises error."""
        with pytest.raises(ValueError, match="positive"):
            calculator.calculate(opioid_name="methadone", daily_dose_mg=0)
