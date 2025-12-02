"""
Aldrete Score for Post-Anesthesia Recovery

A scoring system to assess patient readiness for discharge from PACU.
Original 1970 score uses 5 criteria; Modified 1995 version uses 6 criteria.

Reference:
    Aldrete JA, Kroulik D.
    A postanesthetic recovery score.
    Anesth Analg. 1970;49(6):924-934.
    PMID: 5534693
    
    Aldrete JA.
    The post-anesthesia recovery score revisited.
    J Clin Anesth. 1995;7(1):89-91.
    PMID: 7772368
"""

from typing import Literal

from ..base import BaseCalculator
from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.units import Unit
from ...value_objects.reference import Reference
from ...value_objects.interpretation import Interpretation, Severity, RiskLevel
from ...value_objects.tool_keys import (
    LowLevelKey,
    HighLevelKey,
    Specialty,
    ClinicalContext
)


class AldreteScoreCalculator(BaseCalculator):
    """
    Aldrete Score (Modified) for Post-Anesthesia Discharge
    
    Five criteria, each scored 0-2 (max 10 points):
    
    1. Activity (Motor Function):
       - 2: Moves all extremities voluntarily/on command
       - 1: Moves two extremities
       - 0: Unable to move extremities
       
    2. Respiration:
       - 2: Breathes deeply, coughs freely
       - 1: Dyspnea, shallow or limited breathing
       - 0: Apneic
       
    3. Circulation (Blood Pressure):
       - 2: BP ±20 mmHg of preanesthetic level
       - 1: BP ±20-50 mmHg of preanesthetic level
       - 0: BP ±50 mmHg of preanesthetic level
       
    4. Consciousness:
       - 2: Fully awake
       - 1: Arousable on calling
       - 0: Not responding
       
    5. Oxygen Saturation (SpO2):
       - 2: SpO2 >92% on room air
       - 1: Needs O2 to maintain SpO2 >90%
       - 0: SpO2 <90% even with O2
    
    Discharge criteria: Score ≥9 typically required for PACU discharge
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="aldrete_score",
                name="Aldrete Score",
                purpose="Assess post-anesthesia recovery and PACU discharge readiness",
                input_params=[
                    "activity", "respiration", "circulation",
                    "consciousness", "oxygen_saturation"
                ],
                output_type="Aldrete score (0-10) with discharge recommendation"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ANESTHESIOLOGY,
                    Specialty.SURGERY,
                    Specialty.CRITICAL_CARE,
                ),
                conditions=(
                    "Post-Anesthesia Recovery",
                    "PACU Discharge",
                    "Post-Operative Care",
                    "Anesthesia Recovery",
                    "Ambulatory Surgery",
                ),
                clinical_contexts=(
                    ClinicalContext.DISPOSITION,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "Is this patient ready for PACU discharge?",
                    "What is the Aldrete score?",
                    "Can this patient be discharged from recovery?",
                    "Is the patient recovered from anesthesia?",
                ),
                icd10_codes=(
                    "Z51.89",  # Encounter for other specified aftercare
                ),
                keywords=(
                    "Aldrete", "PACU", "recovery", "discharge", "post-anesthesia",
                    "post-operative", "consciousness", "respiration", "activity",
                    "ambulatory", "day surgery",
                )
            ),
            references=(
                Reference(
                    citation="Aldrete JA, Kroulik D. "
                             "A postanesthetic recovery score. "
                             "Anesth Analg. 1970;49(6):924-934.",
                    pmid="5534693",
                    year=1970
                ),
                Reference(
                    citation="Aldrete JA. "
                             "The post-anesthesia recovery score revisited. "
                             "J Clin Anesth. 1995;7(1):89-91.",
                    pmid="7772368",
                    year=1995
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )

    def calculate(
        self,
        activity: Literal[0, 1, 2],
        respiration: Literal[0, 1, 2],
        circulation: Literal[0, 1, 2],
        consciousness: Literal[0, 1, 2],
        oxygen_saturation: Literal[0, 1, 2]
    ) -> ScoreResult:
        """
        Calculate Aldrete Score.
        
        Args:
            activity: Motor function
                0=Unable to move, 1=Moves 2 extremities, 2=Moves all 4
            respiration: Breathing quality
                0=Apneic, 1=Dyspnea/shallow, 2=Deep breathing/coughs
            circulation: Blood pressure relative to baseline
                0=±50mmHg, 1=±20-50mmHg, 2=±20mmHg of baseline
            consciousness: Level of awareness
                0=Not responding, 1=Arousable, 2=Fully awake
            oxygen_saturation: SpO2 status
                0=<90% with O2, 1=Needs O2 for >90%, 2=>92% on room air
            
        Returns:
            ScoreResult with discharge recommendation
        """
        # Calculate total score
        score = activity + respiration + circulation + consciousness + oxygen_saturation
        
        # Component analysis
        components = {
            "activity": {
                "score": activity,
                "max": 2,
                "description": self._activity_description(activity)
            },
            "respiration": {
                "score": respiration,
                "max": 2,
                "description": self._respiration_description(respiration)
            },
            "circulation": {
                "score": circulation,
                "max": 2,
                "description": self._circulation_description(circulation)
            },
            "consciousness": {
                "score": consciousness,
                "max": 2,
                "description": self._consciousness_description(consciousness)
            },
            "oxygen_saturation": {
                "score": oxygen_saturation,
                "max": 2,
                "description": self._spo2_description(oxygen_saturation)
            }
        }
        
        # Identify limiting factors (components < 2)
        limiting_factors = [
            name for name, data in components.items() if data["score"] < 2
        ]
        
        # Get interpretation
        interpretation = self._get_interpretation(score, limiting_factors)
        
        return ScoreResult(
            value=float(score),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "activity": activity,
                "respiration": respiration,
                "circulation": circulation,
                "consciousness": consciousness,
                "oxygen_saturation": oxygen_saturation
            },
            calculation_details={
                "total_score": score,
                "max_possible": 10,
                "components": components,
                "limiting_factors": limiting_factors,
                "discharge_ready": score >= 9
            },
            notes=self._get_notes(score, limiting_factors)
        )

    def _activity_description(self, score: int) -> str:
        """Get activity description"""
        descriptions = {
            0: "Unable to move extremities voluntarily",
            1: "Moves 2 extremities voluntarily or on command",
            2: "Moves all 4 extremities voluntarily or on command"
        }
        return descriptions.get(score, "Unknown")

    def _respiration_description(self, score: int) -> str:
        """Get respiration description"""
        descriptions = {
            0: "Apneic",
            1: "Dyspnea, shallow or limited breathing",
            2: "Breathes deeply, coughs freely"
        }
        return descriptions.get(score, "Unknown")

    def _circulation_description(self, score: int) -> str:
        """Get circulation description"""
        descriptions = {
            0: "BP ±50 mmHg of preanesthetic level",
            1: "BP ±20-50 mmHg of preanesthetic level",
            2: "BP ±20 mmHg of preanesthetic level"
        }
        return descriptions.get(score, "Unknown")

    def _consciousness_description(self, score: int) -> str:
        """Get consciousness description"""
        descriptions = {
            0: "Not responding",
            1: "Arousable on calling",
            2: "Fully awake"
        }
        return descriptions.get(score, "Unknown")

    def _spo2_description(self, score: int) -> str:
        """Get SpO2 description"""
        descriptions = {
            0: "SpO2 <90% even with supplemental O2",
            1: "Needs supplemental O2 to maintain SpO2 >90%",
            2: "SpO2 >92% on room air"
        }
        return descriptions.get(score, "Unknown")

    def _get_interpretation(self, score: int, limiting_factors: list[str]) -> Interpretation:
        """Get clinical interpretation based on score"""
        
        if score >= 9:
            return Interpretation(
                summary=f"Ready for PACU Discharge (Aldrete {score}/10)",
                detail="Patient meets Aldrete criteria for Phase I PACU discharge.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.LOW,
                stage="Discharge Ready",
                stage_description="Aldrete ≥9/10",
                recommendations=(
                    "May proceed with PACU Phase I discharge",
                    "Ensure accompanying adult for ambulatory patients",
                    "Review discharge instructions with patient/family",
                    "Confirm stable vital signs for 30 minutes",
                ),
                next_steps=(
                    "Complete discharge checklist",
                    "Provide written discharge instructions",
                    "Schedule follow-up as appropriate",
                )
            )
        elif score >= 7:
            limiting_str = ", ".join(limiting_factors) if limiting_factors else "Unknown"
            return Interpretation(
                summary=f"Nearly Ready - Continue Monitoring (Aldrete {score}/10)",
                detail=f"Patient approaching discharge criteria. Limiting factors: {limiting_str}",
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="Approaching Discharge",
                stage_description="Aldrete 7-8/10",
                recommendations=(
                    "Continue PACU monitoring",
                    f"Address limiting factors: {limiting_str}",
                    "Reassess in 15-30 minutes",
                    "Continue supportive care",
                ),
                next_steps=(
                    "Serial Aldrete assessments",
                    "Targeted interventions for limiting factors",
                )
            )
        elif score >= 5:
            limiting_str = ", ".join(limiting_factors) if limiting_factors else "Unknown"
            return Interpretation(
                summary=f"Continued Recovery Needed (Aldrete {score}/10)",
                detail="Patient requires continued PACU monitoring. Multiple factors below optimal.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Active Recovery",
                stage_description="Aldrete 5-6/10",
                recommendations=(
                    "Close monitoring in PACU",
                    "Address airway and breathing issues first",
                    "Consider causes of delayed emergence",
                    "Rule out surgical complications",
                ),
                warnings=(
                    "Delayed recovery - investigate cause",
                    "Consider residual neuromuscular blockade",
                    "Rule out opioid over-sedation",
                ),
                next_steps=(
                    "Anesthesia team notification",
                    "Consider reversal agents if appropriate",
                    "Targeted treatment of limiting factors",
                )
            )
        else:
            return Interpretation(
                summary=f"Significant Recovery Concerns (Aldrete {score}/10)",
                detail="Patient significantly below discharge criteria. Intensive monitoring required.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage="Critical Recovery Phase",
                stage_description="Aldrete <5/10",
                recommendations=(
                    "Immediate anesthesiologist notification",
                    "Ensure airway protection",
                    "High-flow supplemental oxygen",
                    "Continuous pulse oximetry and vital signs",
                    "Consider ICU transfer if no improvement",
                    "Rule out serious complications",
                ),
                warnings=(
                    "Patient not safe for discharge",
                    "Risk of respiratory compromise",
                    "May indicate serious underlying issue",
                ),
                next_steps=(
                    "Urgent anesthesiologist assessment",
                    "Full workup for delayed emergence",
                    "Consider imaging if concern for surgical complication",
                )
            )

    def _get_notes(self, score: int, limiting_factors: list[str]) -> list[str]:
        """Get clinical notes"""
        notes = [
            "Aldrete score should be documented every 5-15 minutes in PACU",
            "Score ≥9 generally required for Phase I PACU discharge",
        ]
        
        if "oxygen_saturation" in limiting_factors:
            notes.append("SpO2 issues: Consider residual anesthetic effect, atelectasis, or bronchospasm")
        
        if "consciousness" in limiting_factors:
            notes.append("Delayed awakening: Consider residual drug effect, metabolic causes, or neurological event")
        
        if "activity" in limiting_factors:
            notes.append("Motor deficit: Consider residual neuromuscular blockade (check TOF), neuraxial block effect")
        
        if score < 9:
            notes.append("Some institutions use Aldrete ≥8 for discharge; follow local protocol")
        
        return notes
