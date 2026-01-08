"""
Murray Lung Injury Score (LIS)

The Murray Lung Injury Score quantifies the severity of acute lung injury
using four components: chest X-ray, PaO2/FiO2 ratio, PEEP level, and
respiratory system compliance. Originally proposed as part of an expanded
definition of ARDS.

Reference (Original):
    Murray JF, Matthay MA, Luce JM, Flick MR. An expanded definition of
    the adult respiratory distress syndrome.
    Am Rev Respir Dis. 1988;138(3):720-723.
    DOI: 10.1164/ajrccm/138.3.720
    PMID: 3202424

Note:
    While the Berlin Definition (2012) has largely replaced this for ARDS
    diagnosis, the Murray Score remains useful for:
    - Quantifying lung injury severity
    - ECMO referral criteria (LIS >3.0)
    - Research and clinical trials
"""

from typing import Optional

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class MurrayLungInjuryScoreCalculator(BaseCalculator):
    """
    Murray Lung Injury Score (LIS) Calculator

    Four components, each scored 0-4:
    1. Chest X-ray consolidation
    2. PaO2/FiO2 ratio
    3. PEEP level
    4. Respiratory system compliance (if available)

    Final score = Sum of component scores / Number of components used

    Interpretation:
    - 0: No lung injury
    - 0.1-2.5: Mild to moderate lung injury
    - >2.5: Severe lung injury (ARDS)
    - >3.0: Consider ECMO referral
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="murray_lung_injury_score",
                name="Murray Lung Injury Score (LIS)",
                purpose="Quantify severity of acute lung injury and guide ECMO consideration",
                input_params=["cxr_quadrants", "pao2_fio2_ratio", "peep", "compliance"],
                output_type="Score (0-4) with severity classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.PULMONOLOGY,
                    Specialty.ANESTHESIOLOGY,
                ),
                conditions=(
                    "ARDS",
                    "Acute Respiratory Distress Syndrome",
                    "Acute Lung Injury",
                    "Respiratory Failure",
                    "Hypoxemic Respiratory Failure",
                    "ECMO Candidacy",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.ICU_MANAGEMENT,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.PROGNOSIS,
                ),
                clinical_questions=(
                    "How severe is this patient's lung injury?",
                    "Should this patient be considered for ECMO?",
                    "Is this ARDS severe enough for advanced therapies?",
                    "How do I quantify lung injury severity?",
                ),
                icd10_codes=("J80", "J96.0", "J96.9"),
                keywords=(
                    "Murray score",
                    "lung injury score",
                    "LIS",
                    "ARDS",
                    "acute lung injury",
                    "ECMO",
                    "respiratory failure",
                    "P/F ratio",
                    "PEEP",
                    "compliance",
                ),
            ),
            references=(
                Reference(
                    citation="Murray JF, Matthay MA, Luce JM, Flick MR. An expanded definition "
                    "of the adult respiratory distress syndrome. "
                    "Am Rev Respir Dis. 1988;138(3):720-723.",
                    doi="10.1164/ajrccm/138.3.720",
                    pmid="3202424",
                    year=1988,
                ),
                Reference(
                    citation="ELSO Guidelines for Cardiopulmonary Extracorporeal Life Support. Extracorporeal Life Support Organization. Version 1.4, 2017.",
                    url="https://www.elso.org/resources/guidelines.aspx",
                    year=2017,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        cxr_quadrants: int,
        pao2_fio2_ratio: float,
        peep: float,
        compliance: Optional[float] = None,
    ) -> ScoreResult:
        """
        Calculate Murray Lung Injury Score.

        Args:
            cxr_quadrants: Number of quadrants with alveolar consolidation on CXR (0-4)
            pao2_fio2_ratio: PaO2/FiO2 ratio (mmHg)
            peep: PEEP level (cmH2O)
            compliance: Respiratory system compliance (mL/cmH2O), optional

        Returns:
            ScoreResult with Murray score and interpretation
        """
        # Validate inputs
        if not 0 <= cxr_quadrants <= 4:
            raise ValueError("CXR quadrants must be between 0 and 4")
        if pao2_fio2_ratio <= 0:
            raise ValueError("PaO2/FiO2 ratio must be positive")
        if peep < 0:
            raise ValueError("PEEP cannot be negative")
        if compliance is not None and compliance <= 0:
            raise ValueError("Compliance must be positive")

        # Score CXR component
        cxr_score = cxr_quadrants  # Direct mapping: 0, 1, 2, 3, 4 quadrants

        # Score PaO2/FiO2 ratio
        if pao2_fio2_ratio >= 300:
            pf_score = 0
        elif pao2_fio2_ratio >= 225:
            pf_score = 1
        elif pao2_fio2_ratio >= 175:
            pf_score = 2
        elif pao2_fio2_ratio >= 100:
            pf_score = 3
        else:
            pf_score = 4

        # Score PEEP
        if peep <= 5:
            peep_score = 0
        elif peep <= 8:
            peep_score = 1
        elif peep <= 11:
            peep_score = 2
        elif peep <= 14:
            peep_score = 3
        else:
            peep_score = 4

        # Score compliance (if available)
        compliance_score: Optional[int] = None
        if compliance is not None:
            if compliance >= 80:
                compliance_score = 0
            elif compliance >= 60:
                compliance_score = 1
            elif compliance >= 40:
                compliance_score = 2
            elif compliance >= 20:
                compliance_score = 3
            else:
                compliance_score = 4

        # Calculate final score
        total_score = cxr_score + pf_score + peep_score
        num_components = 3

        if compliance_score is not None:
            total_score += compliance_score
            num_components = 4

        final_score = total_score / num_components

        # Determine severity
        if final_score == 0:
            category = "No Lung Injury"
        elif final_score <= 2.5:
            category = "Mild-Moderate Lung Injury"
        else:
            category = "Severe Lung Injury (ARDS)"

        ecmo_consideration = final_score > 3.0

        # Get interpretation
        interpretation = self._get_interpretation(final_score, category, ecmo_consideration, cxr_score, pf_score, peep_score, compliance_score, pao2_fio2_ratio)

        return ScoreResult(
            value=round(final_score, 2),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "cxr_quadrants": cxr_quadrants,
                "pao2_fio2_ratio": pao2_fio2_ratio,
                "peep": peep,
                "compliance": compliance,
            },
            calculation_details={
                "components": {
                    "cxr_score": {"value": cxr_score, "input": f"{cxr_quadrants} quadrants", "description": "Alveolar consolidation on CXR"},
                    "pf_ratio_score": {"value": pf_score, "input": f"P/F {pao2_fio2_ratio:.0f}", "description": "Hypoxemia severity"},
                    "peep_score": {"value": peep_score, "input": f"PEEP {peep} cmH2O", "description": "PEEP requirement"},
                    "compliance_score": {
                        "value": compliance_score,
                        "input": f"{compliance} mL/cmH2O" if compliance else "Not provided",
                        "description": "Respiratory system compliance",
                    }
                    if compliance is not None
                    else None,
                },
                "total_score": total_score,
                "num_components": num_components,
                "final_score": round(final_score, 2),
                "category": category,
                "ecmo_consideration": ecmo_consideration,
            },
            formula_used="Murray Score = (CXR + P/F + PEEP + Compliance) / Number of components used",
        )

    def _get_interpretation(
        self,
        score: float,
        category: str,
        ecmo_consideration: bool,
        cxr_score: int,
        pf_score: int,
        peep_score: int,
        compliance_score: Optional[int],
        pf_ratio: float,
    ) -> Interpretation:
        """Get interpretation based on Murray score"""

        component_details = f"CXR={cxr_score}, P/F={pf_score}, PEEP={peep_score}"
        if compliance_score is not None:
            component_details += f", Compliance={compliance_score}"

        if score > 3.0:
            return Interpretation(
                summary=f"Murray Score {score:.1f}: Severe Lung Injury - Consider ECMO",
                detail=f"Score >{3.0} indicates severe lung injury meeting ECMO referral criteria. "
                f"Components: {component_details}. P/F ratio {pf_ratio:.0f} mmHg. "
                f"ELSO guidelines suggest ECMO consideration for Murray Score >3.0 or P/F <100.",
                severity=Severity.CRITICAL,
                stage="Severe (ECMO Consideration)",
                stage_description="Score >3.0: Severe lung injury, ECMO candidate",
                recommendations=(
                    "Consider early ECMO consultation",
                    "Contact nearest ECMO center for transfer evaluation",
                    "Optimize conventional therapy while arranging ECMO:",
                    "- Low tidal volume ventilation (4-6 mL/kg IBW)",
                    "- Prone positioning if P/F <150",
                    "- Neuromuscular blockade in early severe ARDS",
                    "- Conservative fluid management",
                    "Consider inhaled pulmonary vasodilators",
                    "Avoid additional lung injury from ventilator",
                ),
                warnings=(
                    "Very high mortality risk without advanced intervention",
                    "ECMO should be considered before multi-organ failure develops",
                    "Early referral improves ECMO outcomes",
                    "Transport may be required to ECMO center",
                ),
                next_steps=(
                    "Urgent ECMO center consultation",
                    "Optimize lung-protective ventilation",
                    "Consider prone positioning",
                    "Prepare for potential ECMO cannulation or transfer",
                ),
            )
        elif score > 2.5:
            return Interpretation(
                summary=f"Murray Score {score:.1f}: Severe Lung Injury (ARDS)",
                detail=f"Score >2.5 indicates severe lung injury consistent with ARDS. Components: {component_details}. P/F ratio {pf_ratio:.0f} mmHg.",
                severity=Severity.SEVERE,
                stage="Severe",
                stage_description="Score 2.5-3.0: Severe lung injury",
                recommendations=(
                    "Implement ARDSNet lung-protective ventilation",
                    "Tidal volume 4-6 mL/kg ideal body weight",
                    "Plateau pressure <30 cmH2O",
                    "Consider prone positioning if P/F <150",
                    "Neuromuscular blockade in early severe ARDS",
                    "Conservative fluid strategy",
                    "Consider corticosteroids per current guidelines",
                ),
                warnings=(
                    "High mortality risk (30-50%)",
                    "Monitor for progression requiring ECMO",
                    "Watch for barotrauma, ventilator-induced lung injury",
                ),
                next_steps=(
                    "Daily reassessment of Murray Score",
                    "Optimize ventilator settings",
                    "Early ECMO discussion if worsening",
                ),
            )
        elif score > 0:
            return Interpretation(
                summary=f"Murray Score {score:.1f}: Mild-Moderate Lung Injury",
                detail=f"Score 0.1-2.5 indicates mild to moderate lung injury. Components: {component_details}. P/F ratio {pf_ratio:.0f} mmHg.",
                severity=Severity.MODERATE if score > 1.0 else Severity.MILD,
                stage="Mild-Moderate",
                stage_description="Score 0.1-2.5: Mild to moderate lung injury",
                recommendations=(
                    "Lung-protective ventilation strategy",
                    "Target tidal volume 6-8 mL/kg IBW",
                    "Monitor for progression",
                    "Identify and treat underlying cause",
                    "Avoid excessive fluid administration",
                ),
                next_steps=(
                    "Serial monitoring of oxygenation",
                    "Reassess Murray Score if clinical change",
                    "Continue mechanical ventilation optimization",
                ),
            )
        else:
            return Interpretation(
                summary="Murray Score 0: No Lung Injury",
                detail="Score of 0 indicates no significant lung injury. Normal oxygenation, CXR, and respiratory mechanics.",
                severity=Severity.NORMAL,
                stage="None",
                stage_description="Score 0: No lung injury",
                recommendations=(
                    "Continue standard respiratory care",
                    "Monitor for development of lung injury in at-risk patients",
                ),
                next_steps=("Routine monitoring",),
            )
