"""
Pediatric Glasgow Coma Scale (Pediatric GCS) Calculator

Age-adapted Glasgow Coma Scale for infants and young children
who cannot follow verbal commands or speak.

Clinical Application:
- Consciousness assessment in pre-verbal children
- Trauma severity assessment
- Head injury monitoring
- PICU neurological assessment

Scoring Components:
1. Eye Opening (1-4)
2. Verbal Response - age-adapted (1-5)
3. Motor Response (1-6)

Age Adaptations:
- Infants (<1 year): Modified verbal scale for non-verbal patients
- Children (1-5 years): Age-appropriate verbal responses
- >5 years: Standard GCS can be used

Score Interpretation:
- 13-15: Mild impairment
- 9-12: Moderate impairment
- 3-8: Severe impairment (consider airway protection)

References:
    James HE. Neurologic evaluation and support in the child with an acute
    brain insult. Pediatr Ann. 1986;15(1):16-22. PMID: 3951884
    
    Simpson D, Reilly P. Pediatric coma scale.
    Lancet. 1982;2(8295):450. PMID: 6124856
    
    Holmes JF, et al. Performance of the pediatric Glasgow Coma Scale
    in children with blunt head trauma.
    Acad Emerg Med. 2005;12(9):814-819. PMID: 16141014
    
    Reilly PL, Simpson DA, Sprod R, Thomas L. Assessing the conscious level
    in infants and young children: a paediatric version of the Glasgow Coma Scale.
    Childs Nerv Syst. 1988;4(1):30-33. PMID: 3401866
"""

from typing import Optional
from ..base import BaseCalculator
from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.units import Unit
from ...value_objects.reference import Reference
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.tool_keys import (
    LowLevelKey,
    HighLevelKey,
    Specialty,
    ClinicalContext
)


class PediatricGCSCalculator(BaseCalculator):
    """
    Pediatric Glasgow Coma Scale (Pediatric GCS) Calculator
    
    Age-adapted GCS for infants and young children.
    Uses modified verbal scale for pre-verbal patients.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="pediatric_gcs",
                name="Pediatric Glasgow Coma Scale",
                purpose="Age-adapted consciousness assessment for children",
                input_params=[
                    "eye_response", "verbal_response", "motor_response",
                    "age_group", "intubated"
                ],
                output_type="Pediatric GCS score (3-15) with interpretation"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.PEDIATRICS,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.NEUROLOGY,
                    Specialty.TRAUMA,
                ),
                conditions=(
                    "Head injury",
                    "Altered consciousness",
                    "Trauma assessment",
                    "Neurological monitoring",
                    "Encephalopathy",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.TRAUMA_ASSESSMENT,
                    ClinicalContext.NEUROLOGICAL_ASSESSMENT,
                    ClinicalContext.ICU_ASSESSMENT,
                ),
            ),
            references=(
                Reference(
                    citation="Reilly PL, et al. Assessing the conscious level in infants and young children: a paediatric version of the GCS. Childs Nerv Syst. 1988;4(1):30-33.",
                    pmid="3401866",
                    year=1988
                ),
                Reference(
                    citation="Holmes JF, et al. Performance of the pediatric GCS in children with blunt head trauma. Acad Emerg Med. 2005;12(9):814-819.",
                    doi="10.1197/j.aem.2005.04.019",
                    pmid="16141014",
                    year=2005
                ),
            ),
        )

    # Age-specific verbal response descriptions
    VERBAL_INFANT = {
        5: "Coos, babbles, smiles appropriately",
        4: "Irritable cry, consolable",
        3: "Cries to pain, inconsolable",
        2: "Moans to pain",
        1: "No response",
    }

    VERBAL_CHILD = {
        5: "Oriented, appropriate words/sentences",
        4: "Confused, disoriented",
        3: "Inappropriate words, crying",
        2: "Incomprehensible sounds",
        1: "No response",
    }

    def calculate(
        self,
        eye_response: int,
        verbal_response: int,
        motor_response: int,
        age_group: str = "child",
        intubated: bool = False
    ) -> ScoreResult:
        """
        Calculate Pediatric Glasgow Coma Scale.
        
        Args:
            eye_response: Eye opening response (1-4)
                4 = Spontaneous
                3 = To voice/sound
                2 = To pain
                1 = None
            verbal_response: Verbal/vocal response (1-5)
                For infants (<1y):
                    5 = Coos, babbles
                    4 = Irritable cry
                    3 = Cries to pain
                    2 = Moans
                    1 = None
                For children (>1y):
                    5 = Oriented, appropriate
                    4 = Confused
                    3 = Inappropriate words
                    2 = Incomprehensible
                    1 = None
            motor_response: Best motor response (1-6)
                6 = Obeys commands / Normal spontaneous movement
                5 = Localizes pain / Withdraws to touch
                4 = Withdraws from pain
                3 = Abnormal flexion (decorticate)
                2 = Extension (decerebrate)
                1 = None
            age_group: "infant" (<1y) or "child" (≥1y)
            intubated: If intubated, verbal score noted as "T"
        
        Returns:
            ScoreResult with Pediatric GCS and interpretation
        """
        # Validate inputs
        if eye_response < 1 or eye_response > 4:
            raise ValueError("eye_response must be 1-4")
        if verbal_response < 1 or verbal_response > 5:
            raise ValueError("verbal_response must be 1-5")
        if motor_response < 1 or motor_response > 6:
            raise ValueError("motor_response must be 1-6")
        
        valid_ages = ["infant", "child"]
        if age_group not in valid_ages:
            raise ValueError(f"age_group must be one of: {valid_ages}")

        # Calculate total score
        total_score = eye_response + verbal_response + motor_response

        # Get verbal description based on age
        if age_group == "infant":
            verbal_desc = self.VERBAL_INFANT.get(verbal_response, "")
        else:
            verbal_desc = self.VERBAL_CHILD.get(verbal_response, "")

        # Component descriptions
        eye_desc = {
            4: "Spontaneous",
            3: "To voice/sound",
            2: "To pain",
            1: "None"
        }.get(eye_response, "")

        motor_desc = {
            6: "Obeys commands/Normal movement",
            5: "Localizes pain/Withdraws to touch",
            4: "Withdraws from pain",
            3: "Abnormal flexion (decorticate)",
            2: "Extension (decerebrate)",
            1: "None"
        }.get(motor_response, "")

        # Determine severity
        if total_score >= 13:
            severity = Severity.MILD
            impairment = "Mild"
            action = "Observation; serial neuro exams"
        elif total_score >= 9:
            severity = Severity.MODERATE
            impairment = "Moderate"
            action = "Close monitoring; consider CT if trauma; neurology consult"
        elif total_score >= 6:
            severity = Severity.SEVERE
            impairment = "Severe"
            action = "Airway protection likely needed; urgent imaging; PICU admission"
        else:  # 3-5
            severity = Severity.CRITICAL
            impairment = "Critical"
            action = "Immediate intubation; neuroprotection; emergent CT; neurosurgery consult"

        # Intubation notation
        if intubated:
            gcs_notation = f"{total_score}T (E{eye_response} V{verbal_response}T M{motor_response})"
            verbal_note = "Verbal score recorded for reference; patient intubated"
        else:
            gcs_notation = f"{total_score} (E{eye_response} V{verbal_response} M{motor_response})"
            verbal_note = None

        # Build component details
        components = {
            "Eye (E)": f"{eye_response} - {eye_desc}",
            "Verbal (V)": f"{verbal_response} - {verbal_desc}",
            "Motor (M)": f"{motor_response} - {motor_desc}",
        }

        interpretation = Interpretation(
            severity=severity,
            summary=f"Pediatric GCS {gcs_notation}: {impairment} impairment",
            detail=(
                f"Age group: {age_group.capitalize()}\n"
                f"Components: E={eye_response} V={verbal_response} M={motor_response}\n"
                f"Eye: {eye_desc}\n"
                f"Verbal ({age_group}): {verbal_desc}\n"
                f"Motor: {motor_desc}"
                + (f"\nNote: {verbal_note}" if verbal_note else "")
            ),
            recommendations=(action,)
        )

        details = {
            "total_score": total_score,
            "gcs_notation": gcs_notation,
            "age_group": age_group,
            "components": components,
            "impairment_level": impairment,
            "intubated": intubated,
            "airway_concern": total_score <= 8,
            "next_step": self._get_next_step(total_score, intubated)
        }

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "eye_response": eye_response,
                "verbal_response": verbal_response,
                "motor_response": motor_response,
                "age_group": age_group,
                "intubated": intubated,
            },
            calculation_details=details
        )

    def _get_next_step(self, score: int, intubated: bool) -> str:
        """Get clinical next step recommendation."""
        if score <= 8 and not intubated:
            return "Consider intubation for airway protection (GCS ≤8)"
        elif score <= 8:
            return "Continue neuroprotective measures; repeat assessment q1-2h"
        elif score <= 12:
            return "Serial neurological assessments q2-4h; reassess need for imaging"
        else:
            return "Continue monitoring; reassess if deterioration"
