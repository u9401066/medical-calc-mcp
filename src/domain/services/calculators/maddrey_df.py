"""
Maddrey Discriminant Function (mDF) Calculator

用於評估酒精性肝炎的嚴重程度和預後。
mDF ≥ 32 表示嚴重酒精性肝炎，考慮類固醇治療。

References:
- Maddrey WC, et al. Gastroenterology. 1978;75(2):193-199. PMID: 352788
- Carithers RL Jr, et al. Ann Intern Med. 1989;110(9):685-690. PMID: 2648927
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class MaddreyDFCalculator(BaseCalculator):
    """
    Maddrey Discriminant Function (mDF) Calculator

    計算公式:
    mDF = 4.6 × (patient PT - control PT) + total bilirubin

    臨床意義:
    - mDF < 32: 輕至中度，死亡率 < 10%
    - mDF ≥ 32: 嚴重，死亡率 30-50%，考慮類固醇治療
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="maddrey_df",
                name="Maddrey Discriminant Function (mDF)",
                purpose="Assess severity and prognosis in alcoholic hepatitis",
                input_params=["pt_patient", "pt_control", "bilirubin"],
                output_type="Discriminant function score",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.HEPATOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.GASTROENTEROLOGY,
                ),
                conditions=("Alcoholic Hepatitis", "Alcohol-Associated Hepatitis", "Acute Alcoholic Liver Disease", "Severe Alcoholic Hepatitis"),
                clinical_contexts=(
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "Is this alcoholic hepatitis severe enough for steroids?",
                    "What is the prognosis for this alcoholic hepatitis patient?",
                    "Should I start corticosteroid therapy?",
                    "What is the mDF score for treatment decision?",
                ),
                icd10_codes=("K70.10", "K70.11", "K70.40", "K70.41"),
                keywords=(
                    "Maddrey",
                    "discriminant function",
                    "alcoholic hepatitis",
                    "corticosteroids",
                    "prednisolone",
                    "hepatology",
                    "alcohol liver disease",
                    "mDF",
                ),
            ),
            references=(
                Reference(
                    citation="Maddrey WC, Boitnott JK, Bedine MS, et al. Corticosteroid therapy of alcoholic hepatitis. Gastroenterology. 1978;75(2):193-199.",
                    pmid="352788",
                    year=1978,
                ),
                Reference(
                    citation="Carithers RL Jr, Herlong HF, Diehl AM, et al. Methylprednisolone therapy in patients with severe alcoholic hepatitis. A randomized multicenter trial. Ann Intern Med. 1989;110(9):685-690.",
                    pmid="2648927",
                    year=1989,
                ),
                Reference(
                    citation="Thursz MR, Richardson P, Allison M, et al. Prednisolone or pentoxifylline for alcoholic hepatitis. N Engl J Med. 2015;372(17):1619-1628.",
                    pmid="25901427",
                    doi="10.1056/NEJMoa1412278",
                    year=2015,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        pt_patient: float,
        pt_control: float,
        bilirubin: float,
        bilirubin_unit: str = "mg/dL",
    ) -> ScoreResult:
        """
        Calculate Maddrey Discriminant Function (mDF).

        Args:
            pt_patient: Patient's PT (prothrombin time) in seconds
            pt_control: Control/reference PT in seconds (usually 12-14)
            bilirubin: Total bilirubin level
            bilirubin_unit: "mg/dL" (default) or "umol/L"

        Returns:
            ScoreResult with mDF score and interpretation
        """
        # Validate inputs
        if pt_patient <= 0:
            raise ValueError("Patient PT must be positive")
        if pt_control <= 0:
            raise ValueError("Control PT must be positive")
        if bilirubin < 0:
            raise ValueError("Bilirubin cannot be negative")

        # Convert bilirubin to mg/dL if needed
        if bilirubin_unit.lower() in ["umol/l", "μmol/l", "umol"]:
            bilirubin_mgdl = bilirubin / 17.1
        else:
            bilirubin_mgdl = bilirubin

        # Calculate PT prolongation
        pt_prolongation = pt_patient - pt_control

        # Calculate mDF
        mdf = 4.6 * pt_prolongation + bilirubin_mgdl

        # Components
        components = [
            f"PT prolongation = {pt_patient} - {pt_control} = {pt_prolongation:.1f} sec",
            f"4.6 × PT prolongation = 4.6 × {pt_prolongation:.1f} = {4.6 * pt_prolongation:.1f}",
            f"mDF = {4.6 * pt_prolongation:.1f} + {bilirubin_mgdl:.1f} = {mdf:.1f}",
        ]

        # Interpretation based on mDF threshold
        if mdf >= 32:
            risk_level = RiskLevel.HIGH
            severity = Severity.SEVERE
            recommendation = "Consider corticosteroid therapy (prednisolone 40mg/day × 28 days)"
            mortality = "28-day mortality ~30-50% without treatment"
            steroid_indicated = True
        else:
            risk_level = RiskLevel.LOW
            severity = Severity.MILD
            recommendation = "Supportive care; steroids not indicated by mDF alone"
            mortality = "28-day mortality < 10%"
            steroid_indicated = False

        interpretation = Interpretation(
            summary=f"mDF = {mdf:.1f}: {'Severe' if mdf >= 32 else 'Non-severe'} alcoholic hepatitis",
            detail=(
                f"Maddrey Discriminant Function of {mdf:.1f}. "
                f"{mortality}. "
                f"{'Meets criteria for corticosteroid therapy.' if steroid_indicated else 'Does not meet criteria for corticosteroid therapy based on mDF.'}"
            ),
            severity=severity,
            risk_level=risk_level,
            stage="Severe AH" if mdf >= 32 else "Non-severe AH",
            stage_description=("Severe alcoholic hepatitis (mDF ≥32) - high short-term mortality" if mdf >= 32 else "Non-severe alcoholic hepatitis (mDF <32)"),
            recommendations=(
                recommendation,
                "Ensure alcohol abstinence",
                "Nutritional support (high calorie, high protein diet)",
                "Screen for infections before starting steroids" if steroid_indicated else "Monitor closely",
                "Consider MELD score for additional prognostic info",
            ),
            next_steps=(
                "Calculate Lille score at day 7 if steroids started" if steroid_indicated else "Continue supportive care",
                "Consider transplant evaluation if not improving",
            ),
        )

        return ScoreResult(
            value=round(mdf, 1),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs={
                "pt_patient": pt_patient,
                "pt_control": pt_control,
                "bilirubin": bilirubin,
                "bilirubin_unit": bilirubin_unit,
            },
            calculation_details={
                "score_name": "Maddrey Discriminant Function (mDF)",
                "mdf_score": round(mdf, 1),
                "pt_prolongation_seconds": round(pt_prolongation, 1),
                "bilirubin_mgdl": round(bilirubin_mgdl, 1),
                "threshold": 32,
                "meets_steroid_criteria": steroid_indicated,
                "components": components,
            },
            formula_used="mDF = 4.6 × (PT_patient - PT_control) + Total Bilirubin (mg/dL)",
            notes=[
                "mDF ≥ 32 indicates severe alcoholic hepatitis",
                "STOPAH trial showed modest benefit of prednisolone at 28 days",
                "Calculate Lille score at day 7 to assess steroid response",
                "Consider MELD score as complementary prognostic tool",
            ],
        )
