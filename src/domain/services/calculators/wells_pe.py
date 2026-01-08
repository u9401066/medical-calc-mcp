"""
Wells Score for PE Calculator

Estimates the pretest probability of pulmonary embolism (PE) in patients
with suspected PE to guide diagnostic workup.

Original Reference:
    Wells PS, Anderson DR, Rodger M, et al. Derivation of a simple
    clinical model to categorize patients probability of pulmonary
    embolism: increasing the models utility with the SimpliRED D-dimer.
    Thromb Haemost. 2000;83(3):416-420.
    PMID: 10744147.

Validation Reference:
    Wells PS, Anderson DR, Rodger M, et al. Excluding pulmonary embolism
    at the bedside without diagnostic imaging: management of patients
    with suspected pulmonary embolism presenting to the emergency
    department by using a simple clinical model and D-dimer.
    Ann Intern Med. 2001;135(2):98-107.
    doi:10.7326/0003-4819-135-2-200107170-00010. PMID: 11453709.
"""

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


class WellsPeCalculator(BaseCalculator):
    """
    Wells Score for PE (Pulmonary Embolism)

    Scoring criteria:
    - Clinical signs/symptoms of DVT: +3
    - PE is #1 diagnosis or equally likely: +3
    - Heart rate >100 bpm: +1.5
    - Immobilization ≥3 days or surgery within 4 weeks: +1.5
    - Previous DVT/PE: +1.5
    - Hemoptysis: +1
    - Malignancy (treatment within 6 months or palliative): +1

    Original (three-level) interpretation:
    - <2: Low probability (~3.6% PE)
    - 2-6: Moderate probability (~20.5% PE)
    - >6: High probability (~66.7% PE)

    Simplified (two-level) interpretation:
    - ≤4: PE Unlikely (~12.1% PE)
    - >4: PE Likely (~37.1% PE)
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="wells_pe",
                name="Wells Score for PE",
                purpose="Estimate pretest probability of pulmonary embolism to guide diagnostic workup",
                input_params=[
                    "clinical_signs_dvt",
                    "pe_most_likely_diagnosis",
                    "heart_rate_gt_100",
                    "immobilization_or_surgery",
                    "previous_dvt_pe",
                    "hemoptysis",
                    "malignancy",
                ],
                output_type="Score with PE probability and diagnostic recommendations",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.PULMONOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.HEMATOLOGY,
                ),
                conditions=(
                    "pulmonary embolism",
                    "PE",
                    "venous thromboembolism",
                    "VTE",
                    "dyspnea",
                    "chest pain",
                    "suspected PE",
                    "tachycardia",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.RISK_STRATIFICATION,
                ),
                clinical_questions=(
                    "Does this patient have a pulmonary embolism?",
                    "Should I order a CTPA or D-dimer?",
                    "What is the probability of PE in this patient?",
                    "Can I rule out PE with a D-dimer?",
                    "Does this dyspneic patient need a CT scan?",
                ),
                icd10_codes=(
                    "I26",  # Pulmonary embolism
                    "I26.0",  # Pulmonary embolism with acute cor pulmonale
                    "I26.9",  # Pulmonary embolism without acute cor pulmonale
                ),
                keywords=(
                    "Wells score PE",
                    "Wells criteria",
                    "PE probability",
                    "pulmonary embolism",
                    "D-dimer",
                    "CTPA",
                    "CT pulmonary angiogram",
                    "VTE workup",
                ),
            ),
            references=(
                Reference(
                    citation="Wells PS, Anderson DR, Rodger M, et al. Derivation of a simple "
                    "clinical model to categorize patients probability of pulmonary "
                    "embolism: increasing the models utility with the SimpliRED D-dimer. "
                    "Thromb Haemost. 2000;83(3):416-420.",
                    pmid="10744147",
                    year=2000,
                ),
                Reference(
                    citation="Wells PS, Anderson DR, Rodger M, et al. Excluding pulmonary embolism "
                    "at the bedside without diagnostic imaging: management of patients "
                    "with suspected pulmonary embolism presenting to the emergency "
                    "department by using a simple clinical model and D-dimer. "
                    "Ann Intern Med. 2001;135(2):98-107.",
                    doi="10.7326/0003-4819-135-2-200107170-00010",
                    pmid="11453709",
                    year=2001,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        clinical_signs_dvt: bool,
        pe_most_likely_diagnosis: bool,
        heart_rate_gt_100: bool,
        immobilization_or_surgery: bool,
        previous_dvt_pe: bool,
        hemoptysis: bool,
        malignancy: bool,
    ) -> ScoreResult:
        """
        Calculate Wells score for PE.

        Args:
            clinical_signs_dvt: Clinical signs/symptoms of DVT (leg swelling, pain with palpation)
            pe_most_likely_diagnosis: PE is #1 diagnosis or equally likely
            heart_rate_gt_100: Heart rate >100 bpm
            immobilization_or_surgery: Immobilization ≥3 days or surgery in past 4 weeks
            previous_dvt_pe: Previous DVT or PE
            hemoptysis: Hemoptysis (coughing up blood)
            malignancy: Active malignancy (treatment ongoing, within 6 months, or palliative)

        Returns:
            ScoreResult with Wells PE score, probability, and diagnostic recommendations
        """
        # Calculate score
        score = 0.0
        score += 3.0 if clinical_signs_dvt else 0
        score += 3.0 if pe_most_likely_diagnosis else 0
        score += 1.5 if heart_rate_gt_100 else 0
        score += 1.5 if immobilization_or_surgery else 0
        score += 1.5 if previous_dvt_pe else 0
        score += 1.0 if hemoptysis else 0
        score += 1.0 if malignancy else 0

        # Determine interpretation
        interpretation = self._interpret_score(score)

        # Component details
        components = {
            "Clinical signs/symptoms of DVT": 3.0 if clinical_signs_dvt else 0,
            "PE #1 diagnosis or equally likely": 3.0 if pe_most_likely_diagnosis else 0,
            "Heart rate >100 bpm": 1.5 if heart_rate_gt_100 else 0,
            "Immobilization ≥3d or surgery <4wk": 1.5 if immobilization_or_surgery else 0,
            "Previous DVT/PE": 1.5 if previous_dvt_pe else 0,
            "Hemoptysis": 1.0 if hemoptysis else 0,
            "Active malignancy": 1.0 if malignancy else 0,
        }

        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            calculation_details=components,
            references=list(self.references),
        )

    def _interpret_score(self, score: float) -> Interpretation:
        """Generate interpretation based on Wells PE score"""

        # Two-level model (simplified, most commonly used)
        if score <= 4:
            # PE Unlikely
            category = "PE Unlikely"

            if score < 2:
                # Three-level: Low probability
                severity = Severity.MILD
                risk_level = RiskLevel.LOW
                pe_probability = "~3.6%"
                three_level = "Low probability"
            else:
                # Three-level: Moderate probability (2-4)
                severity = Severity.MILD
                risk_level = RiskLevel.LOW
                pe_probability = "~12%"
                three_level = "Moderate probability"

            summary = f"Wells PE = {score}: {category} ({pe_probability} probability)"
            detail = f"Lower pretest probability of PE (approximately {pe_probability}). D-dimer can be used to rule out PE if negative."
            recommendations = [
                "Order high-sensitivity D-dimer",
                "If D-dimer negative: PE effectively ruled out",
                "If D-dimer positive: Proceed to CT pulmonary angiography (CTPA)",
                "Consider age-adjusted D-dimer cutoff in patients ≥50 years",
            ]
            next_steps = [
                "Obtain D-dimer (age-adjusted cutoff: age × 10 µg/L if ≥50y)",
                "Negative D-dimer excludes PE (NPV ~99%)",
                "Positive D-dimer requires imaging",
                "CTPA is gold standard for PE diagnosis",
            ]

        else:
            # PE Likely (score >4)
            if score > 6:
                # Three-level: High probability
                severity = Severity.SEVERE
                risk_level = RiskLevel.HIGH
                pe_probability = "~67%"
                three_level = "High probability"
            else:
                # Three-level: Moderate probability (4-6)
                severity = Severity.MODERATE
                risk_level = RiskLevel.INTERMEDIATE
                pe_probability = "~37%"
                three_level = "Moderate probability"

            category = "PE Likely"
            summary = f"Wells PE = {score}: {category} ({pe_probability} probability)"
            detail = f"Elevated pretest probability of PE (approximately {pe_probability}). Direct imaging with CTPA is recommended."
            recommendations = [
                "Proceed directly to CT pulmonary angiography (CTPA)",
                "D-dimer alone cannot exclude PE at this probability",
                "Consider empiric anticoagulation while awaiting imaging",
                "If CTPA contraindicated, consider V/Q scan",
            ]
            next_steps = [
                "Order CTPA (or V/Q scan if contrast contraindicated)",
                "Consider bilateral leg ultrasound if DVT suspected",
                "If hemodynamically unstable: bedside echo for RV strain",
                "If PE confirmed: initiate anticoagulation, assess severity",
            ]

            if score > 6:
                recommendations.insert(0, "High probability - strongly consider empiric anticoagulation")

        return Interpretation(
            summary=summary,
            severity=severity,
            detail=detail,
            stage=f"Wells PE = {score}",
            stage_description=f"Two-level: {category} | Three-level: {three_level}",
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
            warnings=("High probability of PE - consider empiric anticoagulation",) if score > 6 else tuple(),
        )
