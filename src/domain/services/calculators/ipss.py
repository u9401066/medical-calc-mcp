"""
IPSS (International Prostate Symptom Score)

The IPSS is a validated questionnaire for assessing lower urinary
tract symptoms (LUTS) related to benign prostatic hyperplasia (BPH).

Reference (Original AUA Symptom Score):
    Barry MJ, Fowler FJ Jr, O'Leary MP, et al. The American Urological
    Association symptom index for benign prostatic hyperplasia.
    J Urol. 1992;148(5):1549-1557.
    PMID: 1279218

Reference (EAU Guidelines):
    Gravas S, Cornu JN, Gacci M, et al. EAU Guidelines on Management
    of Non-Neurogenic Male Lower Urinary Tract Symptoms (LUTS).
    European Association of Urology. 2023.
"""

from typing import Any

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import (
    ClinicalContext,
    HighLevelKey,
    LowLevelKey,
    Specialty,
)
from ...value_objects.units import Unit
from ..base import BaseCalculator


class IPSSCalculator(BaseCalculator):
    """
    IPSS (International Prostate Symptom Score) Calculator

    7-item symptom questionnaire + 1 QoL question.
    Symptom score range: 0-35
    QoL score range: 0-6
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="ipss",
                name="IPSS (International Prostate Symptom Score)",
                purpose="Assess severity of lower urinary tract symptoms in BPH",
                input_params=[
                    "incomplete_emptying",
                    "frequency",
                    "intermittency",
                    "urgency",
                    "weak_stream",
                    "straining",
                    "nocturia",
                    "quality_of_life",
                ],
                output_type="Score 0-35 with symptom severity classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.UROLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.FAMILY_MEDICINE,
                ),
                conditions=(
                    "Benign Prostatic Hyperplasia",
                    "BPH",
                    "Lower Urinary Tract Symptoms",
                    "LUTS",
                    "Prostatism",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.SCREENING,
                    ClinicalContext.MONITORING,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "How severe are this patient's LUTS?",
                    "Should this patient receive treatment for BPH?",
                    "Calculate IPSS score",
                    "Assess prostate symptoms",
                ),
                keywords=(
                    "IPSS",
                    "prostate symptoms",
                    "BPH",
                    "LUTS",
                    "AUA symptom score",
                    "urinary symptoms",
                ),
            ),
            references=(
                Reference(
                    citation="Barry MJ, Fowler FJ Jr, O'Leary MP, et al. The American Urological Association symptom index for benign prostatic hyperplasia. J Urol. 1992;148(5):1549-1557.",
                    pmid="1279218",
                    doi="10.1016/s0022-5347(17)36966-5",
                    year=1992,
                ),
                Reference(
                    citation="Gravas S, Cornu JN, Gacci M, et al. EAU Guidelines on Management of Non-Neurogenic Male LUTS. European Association of Urology. 2023.",
                    url="https://uroweb.org/guidelines/management-of-non-neurogenic-male-luts",
                    year=2023,
                ),
            ),
        )

    def calculate(self, **params: Any) -> ScoreResult:
        """
        Calculate IPSS score.

        Args:
            Each symptom question scored 0-5:
            0 = Not at all
            1 = Less than 1 in 5 times
            2 = Less than half the time
            3 = About half the time
            4 = More than half the time
            5 = Almost always

            incomplete_emptying: Sensation of incomplete bladder emptying
            frequency: Urinating again <2 hours after finishing
            intermittency: Stopping and starting several times
            urgency: Difficulty postponing urination
            weak_stream: Weak urinary stream
            straining: Needing to push or strain to begin
            nocturia: Times getting up at night (0=none, 1=1x, 2=2x, 3=3x, 4=4x, 5=5+x)

            quality_of_life: QoL question (0-6)
                0 = Delighted
                1 = Pleased
                2 = Mostly satisfied
                3 = Mixed
                4 = Mostly dissatisfied
                5 = Unhappy
                6 = Terrible

        Returns:
            ScoreResult with IPSS symptom score and QoL
        """
        # Extract and validate symptom scores
        symptom_names = [
            "incomplete_emptying",
            "frequency",
            "intermittency",
            "urgency",
            "weak_stream",
            "straining",
            "nocturia",
        ]

        symptom_scores = {}
        for name in symptom_names:
            value = int(params.get(name, 0))
            if not 0 <= value <= 5:
                raise ValueError(f"{name} must be 0-5")
            symptom_scores[name] = value

        # Calculate total symptom score
        total_symptom_score = sum(symptom_scores.values())

        # Quality of life score (optional but recommended)
        qol_score = params.get("quality_of_life")
        if qol_score is not None:
            qol_score = int(qol_score)
            if not 0 <= qol_score <= 6:
                raise ValueError("quality_of_life must be 0-6")

        # Classify symptom severity (EAU/AUA guidelines)
        if total_symptom_score <= 7:
            severity = Severity.MILD
            severity_text = "Mild symptoms"
            stage = "Mild"
        elif total_symptom_score <= 19:
            severity = Severity.MODERATE
            severity_text = "Moderate symptoms"
            stage = "Moderate"
        else:
            severity = Severity.SEVERE
            severity_text = "Severe symptoms"
            stage = "Severe"

        # Identify voiding vs storage symptoms
        voiding_score = symptom_scores["incomplete_emptying"] + symptom_scores["intermittency"] + symptom_scores["weak_stream"] + symptom_scores["straining"]
        storage_score = symptom_scores["frequency"] + symptom_scores["urgency"] + symptom_scores["nocturia"]

        # Recommendations (per EAU guidelines)
        recommendations = []
        if total_symptom_score <= 7:
            recommendations.append("Mild symptoms - watchful waiting appropriate")
            recommendations.append("Lifestyle advice: fluid management, bladder training")
            recommendations.append("Reassess symptoms in 6-12 months")
        elif total_symptom_score <= 19:
            recommendations.append("Moderate symptoms - medical therapy indicated")
            recommendations.append("First-line: alpha-blocker (e.g., tamsulosin)")
            recommendations.append("Consider 5-alpha reductase inhibitor if prostate >40mL")
            if storage_score > voiding_score:
                recommendations.append("Storage symptoms predominate - consider anticholinergic/beta-3 agonist")
        else:
            recommendations.append("Severe symptoms - aggressive treatment needed")
            recommendations.append("Combination therapy: alpha-blocker + 5ARI")
            recommendations.append("Consider surgical intervention (TURP, HoLEP)")
            recommendations.append("Refer to urology for comprehensive evaluation")

        # QoL interpretation
        qol_text = ""
        if qol_score is not None:
            qol_labels = ["Delighted", "Pleased", "Mostly satisfied", "Mixed", "Mostly dissatisfied", "Unhappy", "Terrible"]
            qol_text = f"QoL: {qol_labels[qol_score]} ({qol_score}/6)"
            if qol_score >= 4:
                recommendations.append("Poor QoL - more aggressive treatment may be warranted")

        warnings = []
        if total_symptom_score >= 20:
            warnings.append("Severe LUTS - evaluate for complications (retention, renal impairment)")
        if symptom_scores["nocturia"] >= 3:
            warnings.append("Significant nocturia - consider other causes (cardiac, sleep apnea)")

        next_steps = [
            "Digital rectal examination",
            "PSA measurement",
            "Uroflowmetry if considering intervention",
            "Post-void residual measurement",
        ]

        return ScoreResult(
            value=total_symptom_score,
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"IPSS = {total_symptom_score}/35: {severity_text}" + (f" | {qol_text}" if qol_text else ""),
                detail=(
                    f"IPSS symptom score of {total_symptom_score}/35 indicates {severity_text.lower()}. "
                    f"Voiding symptoms: {voiding_score}/20, Storage symptoms: {storage_score}/15. "
                    f"{'Voiding symptoms predominate.' if voiding_score > storage_score else 'Storage symptoms predominate.' if storage_score > voiding_score else 'Balanced symptom pattern.'} "
                    f"{qol_text if qol_text else 'QoL not assessed.'}"
                ),
                severity=severity,
                stage=stage,
                stage_description=severity_text,
                recommendations=tuple(recommendations),
                warnings=tuple(warnings),
                next_steps=tuple(next_steps),
            ),
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "total_symptom_score": total_symptom_score,
                "voiding_score": voiding_score,
                "storage_score": storage_score,
                "quality_of_life_score": qol_score,
                "severity_category": stage,
                **{f"q_{k}": v for k, v in symptom_scores.items()},
            },
        )
