"""
DAS28 (Disease Activity Score 28)

The DAS28 is a composite score used to measure disease activity in rheumatoid
arthritis. It incorporates tender and swollen joint counts (28 joints),
acute phase reactant (ESR or CRP), and patient global assessment.

Reference (Original DAS):
    van der Heijde DM, van 't Hof MA, van Riel PL, et al. Judging disease
    activity in clinical practice in rheumatoid arthritis: first step in
    the development of a disease activity score.
    Ann Rheum Dis. 1990;49(11):916-920.
    PMID: 2256738

Reference (DAS28):
    Prevoo ML, van 't Hof MA, Kuper HH, et al. Modified disease activity
    scores that include twenty-eight-joint counts. Development and
    validation in a prospective longitudinal study of patients with
    rheumatoid arthritis. Arthritis Rheum. 1995;38(1):44-48.
    PMID: 7818570

Reference (DAS28-CRP):
    Fransen J, van Riel PL. The Disease Activity Score and the EULAR
    response criteria. Rheum Dis Clin North Am. 2009;35(4):745-757.
    PMID: 19962619
"""

import math

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class DAS28Calculator(BaseCalculator):
    """
    DAS28 (Disease Activity Score 28) Calculator

    Two versions supported:
    1. DAS28-ESR: Uses erythrocyte sedimentation rate
    2. DAS28-CRP: Uses C-reactive protein

    28 joints assessed:
    - Shoulders (2), Elbows (2), Wrists (2), MCP (10), PIP (10), Knees (2)

    Score interpretation:
    - <2.6: Remission
    - 2.6-3.2: Low disease activity
    - 3.2-5.1: Moderate disease activity
    - >5.1: High disease activity
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="das28",
                name="DAS28 (Disease Activity Score 28)",
                purpose="Measure disease activity in rheumatoid arthritis",
                input_params=["tender_joint_count", "swollen_joint_count", "esr", "crp", "patient_global_assessment"],
                output_type="Score with disease activity classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.RHEUMATOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Rheumatoid Arthritis",
                    "RA",
                    "Inflammatory Arthritis",
                ),
                clinical_contexts=(
                    ClinicalContext.MONITORING,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                ),
                clinical_questions=(
                    "What is the disease activity in this RA patient?",
                    "Is this patient in remission?",
                    "Should I change RA therapy?",
                    "Is the patient responding to treatment?",
                ),
                icd10_codes=("M05", "M06", "M06.9"),
                keywords=(
                    "DAS28",
                    "disease activity score",
                    "rheumatoid arthritis",
                    "RA",
                    "joint count",
                    "ESR",
                    "CRP",
                    "remission",
                    "treat to target",
                    "EULAR response",
                ),
            ),
            references=(
                Reference(
                    citation="Prevoo ML, van 't Hof MA, Kuper HH, et al. Modified disease "
                    "activity scores that include twenty-eight-joint counts. "
                    "Arthritis Rheum. 1995;38(1):44-48.",
                    pmid="7818570",
                    year=1995,
                ),
                Reference(
                    citation="Fransen J, van Riel PL. The Disease Activity Score and the EULAR response criteria. Rheum Dis Clin North Am. 2009;35(4):745-757.",
                    pmid="19962619",
                    year=2009,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        tender_joint_count: int,
        swollen_joint_count: int,
        patient_global_assessment: float,
        esr: float | None = None,
        crp: float | None = None,
    ) -> ScoreResult:
        """
        Calculate DAS28 score.

        Args:
            tender_joint_count: Number of tender joints (0-28)
            swollen_joint_count: Number of swollen joints (0-28)
            patient_global_assessment: Patient global assessment of disease activity
                (0-100mm VAS, or 0-10 scale)
            esr: Erythrocyte sedimentation rate (mm/hr) for DAS28-ESR
            crp: C-reactive protein (mg/L) for DAS28-CRP

        Returns:
            ScoreResult with DAS28 score and interpretation
        """
        # Validate inputs
        if not 0 <= tender_joint_count <= 28:
            raise ValueError("Tender joint count must be between 0 and 28")
        if not 0 <= swollen_joint_count <= 28:
            raise ValueError("Swollen joint count must be between 0 and 28")
        if patient_global_assessment < 0:
            raise ValueError("Patient global assessment cannot be negative")

        # Convert VAS to 0-100 scale if needed
        if patient_global_assessment <= 10:
            pga_100 = patient_global_assessment * 10
        else:
            pga_100 = patient_global_assessment

        if pga_100 > 100:
            raise ValueError("Patient global assessment must be 0-100mm or 0-10")

        if esr is None and crp is None:
            raise ValueError("Either ESR or CRP must be provided")

        # Calculate DAS28
        tjc_sqrt = math.sqrt(tender_joint_count)
        sjc_sqrt = math.sqrt(swollen_joint_count)

        das28_type: str
        das28_score: float

        if esr is not None:
            # DAS28-ESR formula
            # DAS28-ESR = 0.56*sqrt(TJC28) + 0.28*sqrt(SJC28) + 0.70*ln(ESR) + 0.014*GH
            if esr <= 0:
                esr = 1  # Avoid log(0)
            das28_score = 0.56 * tjc_sqrt + 0.28 * sjc_sqrt + 0.70 * math.log(esr) + 0.014 * pga_100
            das28_type = "DAS28-ESR"
        else:
            # DAS28-CRP formula
            # DAS28-CRP = 0.56*sqrt(TJC28) + 0.28*sqrt(SJC28) + 0.36*ln(CRP+1) + 0.014*GH + 0.96
            if crp is None:
                crp = 0
            das28_score = 0.56 * tjc_sqrt + 0.28 * sjc_sqrt + 0.36 * math.log(crp + 1) + 0.014 * pga_100 + 0.96
            das28_type = "DAS28-CRP"

        # Round to 2 decimal places
        das28_score = round(das28_score, 2)

        # Determine disease activity category
        if das28_score < 2.6:
            category = "Remission"
        elif das28_score <= 3.2:
            category = "Low Disease Activity"
        elif das28_score <= 5.1:
            category = "Moderate Disease Activity"
        else:
            category = "High Disease Activity"

        # Get interpretation
        interpretation = self._get_interpretation(das28_score, category, das28_type, tender_joint_count, swollen_joint_count, esr, crp)

        return ScoreResult(
            value=das28_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "tender_joint_count": tender_joint_count,
                "swollen_joint_count": swollen_joint_count,
                "patient_global_assessment": patient_global_assessment,
                "esr": esr,
                "crp": crp,
            },
            calculation_details={
                "das28_type": das28_type,
                "components": {
                    "tjc28": tender_joint_count,
                    "sjc28": swollen_joint_count,
                    "pga": pga_100,
                    "esr": esr,
                    "crp": crp,
                },
                "das28_score": das28_score,
                "category": category,
                "thresholds": {
                    "remission": "<2.6",
                    "low": "2.6-3.2",
                    "moderate": "3.2-5.1",
                    "high": ">5.1",
                },
            },
            formula_used=f"{das28_type} = 0.56×√TJC + 0.28×√SJC + {'0.70×ln(ESR)' if esr else '0.36×ln(CRP+1)'} + 0.014×GH{' + 0.96' if crp else ''}",
        )

    def _get_interpretation(self, score: float, category: str, das28_type: str, tjc: int, sjc: int, esr: float | None, crp: float | None) -> Interpretation:
        """Get interpretation based on DAS28 score"""

        lab_text = f"ESR {esr}" if esr else f"CRP {crp}"
        component_text = f"TJC28={tjc}, SJC28={sjc}, {lab_text}"

        if score < 2.6:
            return Interpretation(
                summary=f"{das28_type} {score}: Remission",
                detail=f"Score <2.6 indicates disease remission. Components: {component_text}. Treatment target achieved per ACR/EULAR guidelines.",
                severity=Severity.NORMAL,
                stage="Remission",
                stage_description="DAS28 <2.6: Remission",
                recommendations=(
                    "Target achieved - maintain current therapy",
                    "Consider dose reduction if sustained remission (>6 months)",
                    "Continue monitoring every 3-6 months",
                    "May cautiously taper therapy per treat-to-target guidelines",
                ),
                next_steps=(
                    "Continue current DMARD therapy",
                    "Monitor for sustained remission",
                    "Reassess in 3-6 months",
                ),
            )
        elif score <= 3.2:
            return Interpretation(
                summary=f"{das28_type} {score}: Low Disease Activity",
                detail=f"Score 2.6-3.2 indicates low disease activity (LDA). "
                f"Components: {component_text}. "
                f"Alternative target for treat-to-target if remission not achievable.",
                severity=Severity.MILD,
                stage="Low Disease Activity",
                stage_description="DAS28 2.6-3.2: Low disease activity",
                recommendations=(
                    "Acceptable alternative target to remission",
                    "Consider treatment optimization if comorbidities allow",
                    "If sustained, may be acceptable long-term goal",
                    "Monitor for progression",
                ),
                next_steps=(
                    "Assess if remission achievable",
                    "Consider treatment optimization",
                    "Reassess in 3 months",
                ),
            )
        elif score <= 5.1:
            return Interpretation(
                summary=f"{das28_type} {score}: Moderate Disease Activity",
                detail=f"Score 3.2-5.1 indicates moderate disease activity. Components: {component_text}. Treatment escalation should be considered.",
                severity=Severity.MODERATE,
                stage="Moderate Disease Activity",
                stage_description="DAS28 3.2-5.1: Moderate disease activity",
                recommendations=(
                    "Treatment target NOT achieved",
                    "Consider escalation of DMARD therapy",
                    "Options: Optimize current DMARD, add/switch csDMARD, add bDMARD/tsDMARD",
                    "Assess for poor prognostic factors",
                    "Check compliance with current therapy",
                ),
                warnings=(
                    "Ongoing disease activity causes joint damage",
                    "Early aggressive treatment improves outcomes",
                ),
                next_steps=(
                    "Discuss treatment escalation",
                    "Reassess response in 3 months",
                    "Consider specialist rheumatology review",
                ),
            )
        else:
            return Interpretation(
                summary=f"{das28_type} {score}: High Disease Activity",
                detail=f"Score >5.1 indicates high disease activity. Components: {component_text}. Urgent treatment optimization required.",
                severity=Severity.SEVERE,
                stage="High Disease Activity",
                stage_description="DAS28 >5.1: High disease activity",
                recommendations=(
                    "URGENT: Treatment escalation required",
                    "High disease activity associated with rapid joint damage",
                    "Consider addition of biologic/targeted synthetic DMARD",
                    "Corticosteroid bridging may provide rapid relief",
                    "Frequent monitoring needed (every 1-3 months)",
                ),
                warnings=(
                    "Urgent treatment escalation needed",
                    "High disease activity causes irreversible joint damage",
                    "Increased cardiovascular and mortality risk",
                ),
                next_steps=(
                    "Urgent treatment change",
                    "Consider bridging corticosteroids",
                    "Reassess in 1-3 months",
                    "Ensure access to biologics if needed",
                ),
            )
