"""
MME Calculator (Morphine Milligram Equivalent)

Calculates the total daily Morphine Milligram Equivalent (MME) dose for opioid
prescriptions to assess overdose risk and guide prescribing decisions.

Original Reference:
    Dowell D, Haegerich TM, Chou R.
    CDC Guideline for Prescribing Opioids for Chronic Pain — United States, 2016.
    MMWR Recomm Rep. 2016;65(1):1-49.
    doi:10.15585/mmwr.rr6501e1. PMID: 26987082.

Updated Reference:
    Dowell D, Ragan KR, Jones CM, Baldwin GT, Chou R.
    CDC Clinical Practice Guideline for Prescribing Opioids for Pain —
    United States, 2022.
    MMWR Recomm Rep. 2022;71(3):1-95.
    doi:10.15585/mmwr.rr7103a1. PMID: 36327391.

Clinical Significance:
    - ≥50 MME/day: Increased risk of opioid-related harm
    - ≥90 MME/day: Substantially increased risk; avoid or carefully justify
"""

from typing import Literal

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import (
    ClinicalContext,
    HighLevelKey,
    LowLevelKey,
    Specialty,
)
from ...value_objects.units import Unit
from ..base import BaseCalculator

# Opioid conversion factors to morphine milligram equivalents
# Source: CDC 2022 Guidelines, CMS Opioid Oral MME Conversion Factors
OPIOID_MME_FACTORS: dict[str, float] = {
    # Standard oral opioids
    "morphine": 1.0,
    "codeine": 0.15,
    "hydrocodone": 1.0,  # May vary 0.9-1.0 depending on source
    "oxycodone": 1.5,
    "oxymorphone": 3.0,
    "hydromorphone": 4.0,
    "tramadol": 0.1,
    "tapentadol": 0.4,
    # Methadone uses variable conversion based on current dose
    # For simplicity, we use a midrange factor; actual varies 1-20
    "methadone_1_20": 4.0,  # 1-20 mg/day methadone
    "methadone_21_40": 8.0,  # 21-40 mg/day methadone
    "methadone_41_60": 10.0,  # 41-60 mg/day methadone
    "methadone_over_60": 12.0,  # >60 mg/day methadone
    # Transdermal fentanyl: mcg/hr * 2.4 = MME/day
    "fentanyl_transdermal": 2.4,  # per mcg/hr
    # Buprenorphine - varies by formulation
    "buprenorphine_transdermal": 12.6,  # per mg/day (Butrans patch)
    "buprenorphine_sublingual": 10.0,  # approximate; varies 10-30
    "buprenorphine_film": 10.0,  # sublingual film
    # Other less common opioids
    "meperidine": 0.1,
    "levorphanol": 11.0,
    "pentazocine": 0.37,
    "butorphanol": 7.0,
    "nalbuphine": 1.0,
    "dihydrocodeine": 0.25,
}


OpioidName = Literal[
    "morphine",
    "codeine",
    "hydrocodone",
    "oxycodone",
    "oxymorphone",
    "hydromorphone",
    "tramadol",
    "tapentadol",
    "methadone",
    "fentanyl_transdermal",
    "buprenorphine_transdermal",
    "buprenorphine_sublingual",
    "meperidine",
    "levorphanol",
    "pentazocine",
    "other",
]


class MMECalculator(BaseCalculator):
    """
    MME (Morphine Milligram Equivalent) Calculator

    Converts opioid doses to morphine milligram equivalents (MME) to:
    - Standardize opioid dosage measurement across different medications
    - Identify patients at higher risk for opioid overdose
    - Guide opioid prescribing decisions per CDC guidelines

    Risk Thresholds (CDC 2022):
        - <20 MME/day: Lower risk
        - 20-49 MME/day: Moderate risk
        - 50-89 MME/day: Increased risk
        - ≥90 MME/day: Substantially increased risk

    Note: These thresholds apply to chronic pain management, not acute pain
    or palliative/cancer pain settings.

    Conversion factors are approximations; clinical judgment is essential.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="mme_calculator",
                name="MME Calculator (Morphine Milligram Equivalent)",
                purpose="Calculate total opioid dose in morphine equivalents",
                input_params=[
                    "opioid_name",
                    "daily_dose_mg",
                    "fentanyl_mcg_hr",
                    "methadone_dose_range",
                    "custom_conversion_factor",
                ],
                output_type="MME/day with risk stratification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.PAIN_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.PSYCHIATRY,
                    Specialty.ONCOLOGY,
                    Specialty.ANESTHESIOLOGY,
                ),
                conditions=(
                    "opioid use",
                    "chronic pain",
                    "opioid overdose risk",
                    "opioid prescribing",
                    "pain management",
                    "opioid conversion",
                    "opioid tapering",
                    "substance use disorder",
                ),
                clinical_contexts=(
                    ClinicalContext.MONITORING,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.DRUG_DOSING,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What is the patient's total daily opioid dose?",
                    "Is this opioid dose putting the patient at risk?",
                    "How do I convert between different opioids?",
                    "Should I reduce this patient's opioid dose?",
                    "How much morphine equivalent is the patient taking?",
                ),
                icd10_codes=(
                    "F11.10",  # Opioid abuse, uncomplicated
                    "F11.20",  # Opioid dependence, uncomplicated
                    "T40.2X1A",  # Poisoning by other opioids, accidental
                    "G89.29",  # Other chronic pain
                    "G89.4",  # Chronic pain syndrome
                    "Z79.891",  # Long term opioid use
                ),
                keywords=(
                    "MME",
                    "morphine equivalent",
                    "morphine milligram equivalent",
                    "opioid conversion",
                    "opioid dose",
                    "opioid risk",
                    "CDC opioid guideline",
                    "opioid prescribing",
                    "pain medication",
                    "narcotic dose",
                ),
            ),
            references=(
                Reference(
                    citation="Dowell D, Haegerich TM, Chou R. CDC Guideline for "
                    "Prescribing Opioids for Chronic Pain — United States, 2016. "
                    "MMWR Recomm Rep. 2016;65(1):1-49.",
                    doi="10.15585/mmwr.rr6501e1",
                    pmid="26987082",
                    year=2016,
                ),
                Reference(
                    citation="Dowell D, Ragan KR, Jones CM, Baldwin GT, Chou R. "
                    "CDC Clinical Practice Guideline for Prescribing Opioids for Pain — "
                    "United States, 2022. MMWR Recomm Rep. 2022;71(3):1-95.",
                    doi="10.15585/mmwr.rr7103a1",
                    pmid="36327391",
                    year=2022,
                ),
            ),
            version="CDC 2022",
            validation_status="guideline-recommended",
        )

    def calculate(
        self,
        opioid_name: OpioidName = "morphine",
        daily_dose_mg: float = 0.0,
        fentanyl_mcg_hr: float | None = None,
        methadone_dose_range: Literal[
            "1_20", "21_40", "41_60", "over_60"
        ] | None = None,
        custom_conversion_factor: float | None = None,
    ) -> ScoreResult:
        """
        Calculate MME for a single opioid.

        Args:
            opioid_name: Name of the opioid medication
            daily_dose_mg: Total daily dose in mg (except fentanyl transdermal)
            fentanyl_mcg_hr: For transdermal fentanyl, dose in mcg/hr
            methadone_dose_range: For methadone, specify dose range for
                                  appropriate conversion factor
            custom_conversion_factor: Override default conversion factor

        Returns:
            ScoreResult with calculated MME/day and risk assessment

        Note:
            For fentanyl transdermal patches, use fentanyl_mcg_hr parameter.
            The patch delivers a continuous dose; MME = mcg/hr × 2.4
        """
        # Validate inputs
        if opioid_name == "fentanyl_transdermal":
            if fentanyl_mcg_hr is None or fentanyl_mcg_hr < 0:
                raise ValueError(
                    "For fentanyl transdermal, fentanyl_mcg_hr must be provided "
                    "and non-negative"
                )
            dose_value = fentanyl_mcg_hr
            conversion_factor = OPIOID_MME_FACTORS["fentanyl_transdermal"]
            dose_unit = "mcg/hr"
        elif opioid_name == "methadone":
            if daily_dose_mg <= 0:
                raise ValueError("daily_dose_mg must be positive for methadone")
            # Use dose range to select appropriate conversion factor
            if methadone_dose_range is None:
                # Auto-select based on dose
                if daily_dose_mg <= 20:
                    methadone_dose_range = "1_20"
                elif daily_dose_mg <= 40:
                    methadone_dose_range = "21_40"
                elif daily_dose_mg <= 60:
                    methadone_dose_range = "41_60"
                else:
                    methadone_dose_range = "over_60"
            conversion_factor = OPIOID_MME_FACTORS[f"methadone_{methadone_dose_range}"]
            dose_value = daily_dose_mg
            dose_unit = "mg/day"
        elif opioid_name == "other":
            if custom_conversion_factor is None:
                raise ValueError(
                    "For 'other' opioid, custom_conversion_factor must be provided"
                )
            if daily_dose_mg < 0:
                raise ValueError("daily_dose_mg must be non-negative")
            conversion_factor = custom_conversion_factor
            dose_value = daily_dose_mg
            dose_unit = "mg/day"
        else:
            if daily_dose_mg < 0:
                raise ValueError("daily_dose_mg must be non-negative")
            dose_value = daily_dose_mg
            # Handle buprenorphine variants
            if opioid_name in ["buprenorphine_transdermal", "buprenorphine_sublingual"]:
                conversion_factor = OPIOID_MME_FACTORS[opioid_name]
            else:
                conversion_factor = OPIOID_MME_FACTORS.get(opioid_name, 1.0)
            dose_unit = "mg/day"

        # Override with custom factor if provided
        if custom_conversion_factor is not None and opioid_name != "other":
            conversion_factor = custom_conversion_factor

        # Calculate MME
        mme_per_day = dose_value * conversion_factor

        # Generate interpretation
        interpretation = self._interpret_mme(mme_per_day)

        # Build calculation details
        calculation_details: dict[str, object] = {
            "opioid": opioid_name,
            "dose": dose_value,
            "dose_unit": dose_unit,
            "conversion_factor": conversion_factor,
            "mme_per_day": round(mme_per_day, 1),
            "formula": f"{dose_value} {dose_unit} × {conversion_factor} = {round(mme_per_day, 1)} MME/day",
        }

        if opioid_name == "methadone" and methadone_dose_range:
            calculation_details["methadone_dose_range"] = methadone_dose_range

        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=round(mme_per_day, 1),
            unit=Unit.MME_DAY,
            interpretation=interpretation,
            calculation_details=calculation_details,
            references=list(self.references),
            formula_used=f"MME = Daily Dose × Conversion Factor ({conversion_factor})",
        )

    def calculate_multiple(
        self,
        opioids: list[dict[str, float | str | None]],
    ) -> ScoreResult:
        """
        Calculate total MME from multiple opioid medications.

        Args:
            opioids: List of dicts with keys:
                - name: Opioid name (required)
                - daily_dose_mg: Daily dose in mg (required for most)
                - fentanyl_mcg_hr: For fentanyl patches (optional)
                - methadone_dose_range: For methadone (optional)
                - custom_conversion_factor: Override factor (optional)

        Returns:
            ScoreResult with total MME/day and itemized breakdown
        """
        if not opioids:
            raise ValueError("At least one opioid must be provided")

        total_mme = 0.0
        breakdown: list[dict[str, object]] = []

        for opioid in opioids:
            name = str(opioid.get("name", "morphine"))
            daily_dose = float(opioid.get("daily_dose_mg", 0))
            fentanyl_mcg = opioid.get("fentanyl_mcg_hr")
            methadone_range = opioid.get("methadone_dose_range")
            custom_factor = opioid.get("custom_conversion_factor")

            # Get conversion factor
            if name == "fentanyl_transdermal" and fentanyl_mcg is not None:
                dose_value = float(fentanyl_mcg)
                factor = OPIOID_MME_FACTORS["fentanyl_transdermal"]
            elif name == "methadone":
                dose_value = daily_dose
                if methadone_range is None:
                    if dose_value <= 20:
                        methadone_range = "1_20"
                    elif dose_value <= 40:
                        methadone_range = "21_40"
                    elif dose_value <= 60:
                        methadone_range = "41_60"
                    else:
                        methadone_range = "over_60"
                factor = OPIOID_MME_FACTORS[f"methadone_{methadone_range}"]
            else:
                dose_value = daily_dose
                factor = OPIOID_MME_FACTORS.get(name, 1.0)

            if custom_factor is not None:
                factor = float(custom_factor)

            mme = dose_value * factor
            total_mme += mme

            breakdown.append(
                {
                    "opioid": name,
                    "dose": dose_value,
                    "conversion_factor": factor,
                    "mme": round(mme, 1),
                }
            )

        interpretation = self._interpret_mme(total_mme)

        calculation_details: dict[str, object] = {
            "opioid_count": len(opioids),
            "individual_opioids": breakdown,
            "total_mme_per_day": round(total_mme, 1),
        }

        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=round(total_mme, 1),
            unit=Unit.MME_DAY,
            interpretation=interpretation,
            calculation_details=calculation_details,
            references=list(self.references),
            formula_used="Total MME = Σ(Daily Dose × Conversion Factor) for each opioid",
        )

    def _interpret_mme(self, mme: float) -> Interpretation:
        """Generate risk-based interpretation for MME value."""

        if mme == 0:
            return Interpretation(
                summary="No opioid dose (0 MME/day)",
                detail="No opioid medication or zero dose entered.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.VERY_LOW,
                stage="None",
                stage_description="No opioid use",
                recommendations=(
                    "Continue non-opioid pain management strategies if applicable",
                ),
                next_steps=(),
                warnings=(),
            )

        if mme < 20:
            return Interpretation(
                summary=f"Low opioid dose: {round(mme, 1)} MME/day",
                detail="This opioid dose is below typical risk thresholds. "
                "Continue to monitor for efficacy and side effects.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.VERY_LOW,
                stage="Low MME",
                stage_description="<20 MME/day",
                recommendations=(
                    "Continue current regimen if effective",
                    "Monitor for adverse effects (constipation, sedation)",
                    "Assess pain control periodically",
                    "Continue non-pharmacologic pain strategies",
                ),
                next_steps=(
                    "Reassess pain and function at follow-up",
                    "Consider tapering if pain controlled or resolved",
                ),
                warnings=(),
            )

        if mme < 50:
            return Interpretation(
                summary=f"Moderate opioid dose: {round(mme, 1)} MME/day",
                detail="This dose is in the moderate range. Per CDC guidelines, "
                "carefully reassess individual benefits and risks when increasing "
                "dosage to ≥50 MME/day.",
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="Moderate MME",
                stage_description="20-49 MME/day",
                recommendations=(
                    "Evaluate benefits vs risks before dose increases",
                    "Consider non-opioid and non-pharmacologic therapies",
                    "Assess for opioid use disorder risk factors",
                    "Ensure patient understands overdose risks",
                    "Discuss naloxone availability",
                ),
                next_steps=(
                    "Review prescription drug monitoring program (PDMP)",
                    "Document pain assessment and functional improvement",
                    "Consider referral to pain specialist if not improving",
                ),
                warnings=(
                    "Approaching higher risk threshold (50 MME/day)",
                    "Co-prescribing benzodiazepines increases overdose risk",
                ),
            )

        if mme < 90:
            return Interpretation(
                summary=f"Elevated opioid dose: {round(mme, 1)} MME/day (≥50 MME)",
                detail="This dose is at or above 50 MME/day, the threshold "
                "where CDC guidelines recommend increased caution. "
                "Risk of overdose increases significantly at this level.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Elevated MME",
                stage_description="50-89 MME/day",
                recommendations=(
                    "Implement risk mitigation strategies",
                    "Consider naloxone co-prescription (strongly recommended)",
                    "Increase frequency of follow-up visits",
                    "Maximize non-opioid and non-pharmacologic therapies",
                    "Evaluate for opioid rotation to improve efficacy",
                    "Screen for opioid use disorder with validated tools",
                ),
                next_steps=(
                    "Check PDMP before each prescription",
                    "Consider urine drug screening",
                    "Develop tapering plan if appropriate",
                    "Consult pain medicine specialist",
                ),
                warnings=(
                    "Increased risk of opioid-related harm at ≥50 MME/day",
                    "Avoid concurrent benzodiazepine prescriptions if possible",
                    "Naloxone should be prescribed",
                ),
            )

        # ≥90 MME/day
        return Interpretation(
            summary=f"High opioid dose: {round(mme, 1)} MME/day (≥90 MME)",
            detail="This dose is at or above 90 MME/day. CDC guidelines recommend "
            "avoiding or carefully justifying doses at this level due to "
            "substantially increased risk of overdose and death.",
            severity=Severity.SEVERE,
            risk_level=RiskLevel.HIGH,
            stage="High MME",
            stage_description="≥90 MME/day",
            recommendations=(
                "Carefully re-evaluate medical necessity of high-dose therapy",
                "Document clear justification for this dose level",
                "Prescribe naloxone (MANDATORY recommendation)",
                "More frequent and intensive monitoring",
                "Offer or arrange evidence-based treatment for OUD if suspected",
                "Develop individualized tapering plan with patient",
                "Consider specialist pain management referral",
            ),
            next_steps=(
                "Urgent reassessment of pain management strategy",
                "Check PDMP immediately",
                "Urine drug screening",
                "Assess for diversion risk",
                "Consider supervised tapering",
            ),
            warnings=(
                "HIGH OVERDOSE RISK at ≥90 MME/day",
                "Mortality risk increases substantially at this dose",
                "MUST co-prescribe naloxone",
                "Avoid benzodiazepine co-prescription",
                "Risk of opioid-induced hyperalgesia at high doses",
            ),
        )

    def get_conversion_factor(self, opioid_name: str) -> float | None:
        """
        Get the MME conversion factor for a specific opioid.

        Args:
            opioid_name: Name of the opioid

        Returns:
            Conversion factor or None if not found
        """
        return OPIOID_MME_FACTORS.get(opioid_name.lower())

    def list_supported_opioids(self) -> list[dict[str, object]]:
        """
        List all supported opioids and their conversion factors.

        Returns:
            List of opioid information dicts
        """
        result = []
        for name, factor in OPIOID_MME_FACTORS.items():
            if name.startswith("methadone_"):
                continue  # Skip methadone variants
            result.append(
                {
                    "opioid": name,
                    "conversion_factor": factor,
                    "unit": "mcg/hr" if name == "fentanyl_transdermal" else "mg",
                }
            )
        return result
