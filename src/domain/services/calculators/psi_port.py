"""
PSI/PORT Score Calculator for Pneumonia Severity

The Pneumonia Severity Index (PSI), also known as PORT Score, stratifies
patients with community-acquired pneumonia (CAP) into risk classes to guide
disposition decisions (outpatient vs inpatient vs ICU).

Original Reference:
    Fine MJ, Auble TE, Yealy DM, et al. A prediction rule to identify
    low-risk patients with community-acquired pneumonia. N Engl J Med.
    1997;336(4):243-250.
    doi:10.1056/NEJM199701233360402. PMID: 8995086.

Validation Reference:
    Aujesky D, Auble TE, Yealy DM, et al. Prospective comparison of three
    validated prediction rules for prognosis in community-acquired pneumonia.
    Am J Med. 2005;118(4):384-392.
    doi:10.1016/j.amjmed.2005.01.006. PMID: 15808136.
"""

from typing import Any

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


class PsiPortCalculator(BaseCalculator):
    """
    Pneumonia Severity Index (PSI) / PORT Score Calculator

    Calculates PSI score for community-acquired pneumonia to determine
    risk class and guide disposition decisions.

    Scoring System:

    Demographics:
    - Age (years): Male = age, Female = age - 10

    Comorbidities (+10 each):
    - Neoplastic disease
    - Liver disease
    - Congestive heart failure
    - Cerebrovascular disease
    - Renal disease

    Physical Exam Findings:
    - Altered mental status: +20
    - Respiratory rate ≥30/min: +20
    - Systolic BP <90 mmHg: +20
    - Temperature <35°C or ≥40°C: +15
    - Pulse ≥125/min: +10

    Laboratory/Radiology Findings:
    - Arterial pH <7.35: +30
    - BUN ≥30 mg/dL (≥11 mmol/L): +20
    - Sodium <130 mEq/L: +20
    - Glucose ≥250 mg/dL (≥14 mmol/L): +10
    - Hematocrit <30%: +10
    - PaO2 <60 mmHg or O2 sat <90%: +10
    - Pleural effusion: +10

    Risk Classes:
    - Class I: ≤50 years, no comorbidities, normal vitals → Outpatient
    - Class II: ≤70 points → Outpatient
    - Class III: 71-90 points → Brief inpatient/observation
    - Class IV: 91-130 points → Inpatient
    - Class V: >130 points → Inpatient (consider ICU)

    30-Day Mortality by Class:
    - Class I: 0.1-0.4%
    - Class II: 0.6-0.7%
    - Class III: 0.9-2.8%
    - Class IV: 8.2-9.3%
    - Class V: 27.0-31.1%
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="psi_port",
                name="PSI/PORT Score for Pneumonia",
                purpose="Stratify CAP patients by mortality risk to guide disposition",
                input_params=[
                    "age_years",
                    "female",
                    "nursing_home_resident",
                    "neoplastic_disease",
                    "liver_disease",
                    "chf",
                    "cerebrovascular_disease",
                    "renal_disease",
                    "altered_mental_status",
                    "respiratory_rate_gte_30",
                    "systolic_bp_lt_90",
                    "temperature_abnormal",
                    "pulse_gte_125",
                    "arterial_ph_lt_7_35",
                    "bun_gte_30",
                    "sodium_lt_130",
                    "glucose_gte_250",
                    "hematocrit_lt_30",
                    "pao2_lt_60_or_sao2_lt_90",
                    "pleural_effusion",
                ],
                output_type="PSI score with risk class and disposition recommendation",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.PULMONOLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.INFECTIOUS_DISEASE,
                    Specialty.CRITICAL_CARE,
                ),
                conditions=(
                    "community-acquired pneumonia",
                    "CAP",
                    "pneumonia",
                    "lower respiratory tract infection",
                    "LRTI",
                    "respiratory infection",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.DISPOSITION,
                ),
                clinical_questions=(
                    "Can this pneumonia patient be treated as an outpatient?",
                    "Does this patient with pneumonia need to be admitted?",
                    "What is the mortality risk for this CAP patient?",
                    "Should this pneumonia patient go to the ICU?",
                    "Is this pneumonia patient safe for discharge?",
                ),
                icd10_codes=(
                    "J18.9",  # Pneumonia, unspecified organism
                    "J18.1",  # Lobar pneumonia, unspecified organism
                    "J13",  # Pneumonia due to Streptococcus pneumoniae
                    "J15.9",  # Bacterial pneumonia, unspecified
                    "J22",  # Unspecified acute lower respiratory infection
                ),
                keywords=(
                    "PSI score",
                    "PORT score",
                    "pneumonia severity index",
                    "CAP risk stratification",
                    "pneumonia disposition",
                    "pneumonia mortality",
                    "community-acquired pneumonia",
                    "Fine score",
                ),
            ),
            references=(
                Reference(
                    citation="Fine MJ, Auble TE, Yealy DM, et al. A prediction rule to identify "
                    "low-risk patients with community-acquired pneumonia. N Engl J Med. "
                    "1997;336(4):243-250.",
                    doi="10.1056/NEJM199701233360402",
                    pmid="8995086",
                    year=1997,
                ),
                Reference(
                    citation="Aujesky D, Auble TE, Yealy DM, et al. Prospective comparison of "
                    "three validated prediction rules for prognosis in community-acquired "
                    "pneumonia. Am J Med. 2005;118(4):384-392.",
                    doi="10.1016/j.amjmed.2005.01.006",
                    pmid="15808136",
                    year=2005,
                ),
            ),
            version="1997",
            validation_status="validated",
        )

    def calculate(
        self,
        age_years: int,
        female: bool = False,
        nursing_home_resident: bool = False,
        # Comorbidities
        neoplastic_disease: bool = False,
        liver_disease: bool = False,
        chf: bool = False,
        cerebrovascular_disease: bool = False,
        renal_disease: bool = False,
        # Physical exam findings
        altered_mental_status: bool = False,
        respiratory_rate_gte_30: bool = False,
        systolic_bp_lt_90: bool = False,
        temperature_abnormal: bool = False,
        pulse_gte_125: bool = False,
        # Laboratory/radiology findings
        arterial_ph_lt_7_35: bool = False,
        bun_gte_30: bool = False,
        sodium_lt_130: bool = False,
        glucose_gte_250: bool = False,
        hematocrit_lt_30: bool = False,
        pao2_lt_60_or_sao2_lt_90: bool = False,
        pleural_effusion: bool = False,
    ) -> ScoreResult:
        """
        Calculate PSI/PORT Score for Community-Acquired Pneumonia.

        Args:
            age_years: Patient age in years
            female: Patient is female (age -10 adjustment)
            nursing_home_resident: Patient resides in nursing home (+10)
            neoplastic_disease: Active neoplastic disease (+10)
            liver_disease: Liver disease (+10)
            chf: Congestive heart failure (+10)
            cerebrovascular_disease: Cerebrovascular disease (+10)
            renal_disease: Renal disease (+10)
            altered_mental_status: Altered mental status (+20)
            respiratory_rate_gte_30: Respiratory rate ≥30/min (+20)
            systolic_bp_lt_90: Systolic BP <90 mmHg (+20)
            temperature_abnormal: Temperature <35°C or ≥40°C (+15)
            pulse_gte_125: Pulse ≥125/min (+10)
            arterial_ph_lt_7_35: Arterial pH <7.35 (+30)
            bun_gte_30: BUN ≥30 mg/dL (≥11 mmol/L) (+20)
            sodium_lt_130: Sodium <130 mEq/L (+20)
            glucose_gte_250: Glucose ≥250 mg/dL (≥14 mmol/L) (+10)
            hematocrit_lt_30: Hematocrit <30% (+10)
            pao2_lt_60_or_sao2_lt_90: PaO2 <60 mmHg or O2 sat <90% (+10)
            pleural_effusion: Pleural effusion on imaging (+10)

        Returns:
            ScoreResult with PSI score, risk class, and disposition recommendations
        """
        components: dict[str, Any] = {}

        # Check for Class I (low-risk criteria)
        has_comorbidities = any([neoplastic_disease, liver_disease, chf, cerebrovascular_disease, renal_disease])
        has_abnormal_vitals = any([altered_mental_status, respiratory_rate_gte_30, systolic_bp_lt_90, temperature_abnormal, pulse_gte_125])

        # Class I: ≤50 years, no comorbidities, no abnormal vitals
        is_class_i = (
            age_years <= 50
            and not female  # Original study used male-only for Class I
            and not nursing_home_resident
            and not has_comorbidities
            and not has_abnormal_vitals
        )

        # Actually, Class I is determined differently:
        # Low-risk criteria: age ≤50, no neoplastic/liver/CHF/CVD/renal disease,
        # no altered mental status, no RR≥30, no SBP<90, no temp<35 or ≥40, no pulse≥125
        is_class_i = (
            age_years <= 50
            and not nursing_home_resident
            and not neoplastic_disease
            and not liver_disease
            and not chf
            and not cerebrovascular_disease
            and not renal_disease
            and not altered_mental_status
            and not respiratory_rate_gte_30
            and not systolic_bp_lt_90
            and not temperature_abnormal
            and not pulse_gte_125
        )

        if is_class_i:
            # Class I - don't calculate score, just assign class
            score = 0
            risk_class = "I"
            components["Class I criteria"] = "Met - no score calculation needed"
        else:
            # Calculate score for Classes II-V
            score = 0

            # Age points
            if female:
                age_points = age_years - 10
                components["Age (female, -10)"] = age_points
            else:
                age_points = age_years
                components["Age (male)"] = age_points
            score += max(0, age_points)  # Ensure non-negative

            # Nursing home resident
            if nursing_home_resident:
                score += 10
                components["Nursing home resident"] = 10

            # Comorbidities (+10 each)
            if neoplastic_disease:
                score += 30
                components["Neoplastic disease"] = 30
            if liver_disease:
                score += 20
                components["Liver disease"] = 20
            if chf:
                score += 10
                components["Congestive heart failure"] = 10
            if cerebrovascular_disease:
                score += 10
                components["Cerebrovascular disease"] = 10
            if renal_disease:
                score += 10
                components["Renal disease"] = 10

            # Physical exam findings
            if altered_mental_status:
                score += 20
                components["Altered mental status"] = 20
            if respiratory_rate_gte_30:
                score += 20
                components["Respiratory rate ≥30/min"] = 20
            if systolic_bp_lt_90:
                score += 20
                components["Systolic BP <90 mmHg"] = 20
            if temperature_abnormal:
                score += 15
                components["Temperature <35°C or ≥40°C"] = 15
            if pulse_gte_125:
                score += 10
                components["Pulse ≥125/min"] = 10

            # Laboratory/radiology findings
            if arterial_ph_lt_7_35:
                score += 30
                components["Arterial pH <7.35"] = 30
            if bun_gte_30:
                score += 20
                components["BUN ≥30 mg/dL"] = 20
            if sodium_lt_130:
                score += 20
                components["Sodium <130 mEq/L"] = 20
            if glucose_gte_250:
                score += 10
                components["Glucose ≥250 mg/dL"] = 10
            if hematocrit_lt_30:
                score += 10
                components["Hematocrit <30%"] = 10
            if pao2_lt_60_or_sao2_lt_90:
                score += 10
                components["PaO2 <60 or SaO2 <90%"] = 10
            if pleural_effusion:
                score += 10
                components["Pleural effusion"] = 10

            # Determine risk class
            if score <= 70:
                risk_class = "II"
            elif score <= 90:
                risk_class = "III"
            elif score <= 130:
                risk_class = "IV"
            else:
                risk_class = "V"

        # Generate interpretation
        interpretation = self._interpret_score(score, risk_class, is_class_i)

        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            calculation_details=components,
            references=list(self.references),
        )

    def _interpret_score(self, score: int, risk_class: str, is_class_i: bool) -> Interpretation:
        """Generate interpretation based on PSI/PORT score and risk class"""

        mortality_rates = {
            "I": "0.1-0.4%",
            "II": "0.6-0.7%",
            "III": "0.9-2.8%",
            "IV": "8.2-9.3%",
            "V": "27.0-31.1%",
        }

        if risk_class == "I":
            severity = Severity.NORMAL
            risk_level = RiskLevel.VERY_LOW
            mortality = mortality_rates["I"]
            disposition = "Outpatient treatment"
            recommendations = [
                "Outpatient treatment is appropriate",
                "Oral antibiotics per guidelines (e.g., amoxicillin or doxycycline)",
                "Close follow-up in 24-48 hours",
                "Return precautions for worsening symptoms",
            ]
            next_steps = [
                "Prescribe appropriate oral antibiotics",
                "Ensure adequate follow-up",
                "Provide return precautions",
                "Consider social factors that may require admission",
            ]

        elif risk_class == "II":
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            mortality = mortality_rates["II"]
            disposition = "Outpatient treatment"
            recommendations = [
                "Outpatient treatment is generally appropriate",
                "Oral antibiotics per CAP guidelines",
                "Close follow-up within 24-48 hours",
                "Consider brief observation if concerns exist",
            ]
            next_steps = [
                "Prescribe appropriate oral antibiotics",
                "Ensure reliable follow-up",
                "Review social situation (ability to care for self)",
                "Low threshold for short observation if any concern",
            ]

        elif risk_class == "III":
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            mortality = mortality_rates["III"]
            disposition = "Brief inpatient stay or extended observation"
            recommendations = [
                "Brief inpatient admission (24-48h) OR extended observation",
                "IV antibiotics initially, transition to oral when stable",
                "Monitor response to treatment",
                "Consider outpatient if rapid improvement",
            ]
            next_steps = [
                "Admit for observation/brief stay",
                "Start IV antibiotics (ceftriaxone + azithromycin or respiratory FQ)",
                "Reassess in 24-48 hours for discharge",
                "Transition to oral antibiotics when improving",
            ]

        elif risk_class == "IV":
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            mortality = mortality_rates["IV"]
            disposition = "Inpatient admission"
            recommendations = [
                "Inpatient admission recommended",
                "IV antibiotics per CAP guidelines",
                "Consider ICU admission if clinical deterioration",
                "Monitor for complications",
            ]
            next_steps = [
                "Admit to hospital ward",
                "Start IV antibiotics (ceftriaxone + azithromycin or respiratory FQ)",
                "Consider blood cultures, procalcitonin",
                "Monitor respiratory status closely",
                "Assess for ICU criteria (severe CAP)",
            ]

        else:  # Class V
            severity = Severity.CRITICAL
            risk_level = RiskLevel.VERY_HIGH
            mortality = mortality_rates["V"]
            disposition = "Inpatient admission; consider ICU"
            recommendations = [
                "Inpatient admission required",
                "Strong consideration for ICU admission",
                "IV antibiotics - consider broader coverage",
                "Close monitoring for sepsis and respiratory failure",
            ]
            next_steps = [
                "Admit to ICU or step-down unit",
                "Start IV antibiotics (consider anti-pseudomonal coverage if risk factors)",
                "Blood cultures, procalcitonin, lactate",
                "Monitor for need for mechanical ventilation",
                "Consider vasopressors if hypotensive",
            ]

        if is_class_i:
            summary = f"PSI Class I: Very Low Risk ({mortality} 30-day mortality)"
        else:
            summary = f"PSI = {score}, Class {risk_class}: {mortality} 30-day mortality"

        detail = (
            f"Pneumonia Severity Index Class {risk_class} indicates a {risk_level} risk "
            f"with estimated 30-day mortality of {mortality}. "
            f"Recommended disposition: {disposition}."
        )

        warnings: tuple[str, ...] = tuple()
        if risk_class in ["IV", "V"]:
            warnings = (
                "High-risk pneumonia - inpatient treatment required",
                "Monitor closely for sepsis and respiratory failure",
            )
        if risk_class == "V":
            warnings = warnings + ("Very high mortality risk - consider ICU admission",)

        return Interpretation(
            summary=summary,
            severity=severity,
            detail=detail,
            stage=f"PSI Class {risk_class}",
            stage_description=f"30-day mortality: {mortality}",
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
            warnings=warnings,
        )
