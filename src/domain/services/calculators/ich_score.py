"""
ICH Score (Intracerebral Hemorrhage Score)

The ICH Score is a clinical grading scale that predicts 30-day mortality in 
patients with spontaneous intracerebral hemorrhage. It is one of the most 
widely validated and used prognostic scores in ICH.

Reference (Original):
    Hemphill JC 3rd, Bonovich DC, Besmertis L, Manley GT, Johnston SC.
    The ICH score: a simple, reliable grading scale for intracerebral hemorrhage.
    Stroke. 2001;32(4):891-897.
    DOI: 10.1161/01.str.32.4.891
    PMID: 11283388

Clinical Notes:
- Five components: GCS, ICH volume, IVH, infratentorial location, age
- Score range: 0-6
- Widely validated across different populations
- Should be used cautiously - not a substitute for clinical judgment
- May contribute to self-fulfilling prophecy if used for withdrawal decisions
- Higher scores correlate with higher 30-day mortality
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


class IchScoreCalculator(BaseCalculator):
    """
    ICH Score Calculator
    
    Predicts 30-day mortality in spontaneous intracerebral hemorrhage.
    
    Components (Total 0-6 points):
    
    1. Glasgow Coma Scale (GCS):
       - GCS 3-4: 2 points
       - GCS 5-12: 1 point
       - GCS 13-15: 0 points
    
    2. ICH Volume:
       - ≥30 mL: 1 point
       - <30 mL: 0 points
    
    3. Intraventricular Hemorrhage (IVH):
       - Yes: 1 point
       - No: 0 points
    
    4. Infratentorial Origin:
       - Yes: 1 point
       - No: 0 points
    
    5. Age:
       - ≥80 years: 1 point
       - <80 years: 0 points
    
    30-day Mortality:
    - ICH Score 0: 0%
    - ICH Score 1: 13%
    - ICH Score 2: 26%
    - ICH Score 3: 72%
    - ICH Score 4: 97%
    - ICH Score 5: 100%
    - ICH Score 6: 100%
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="ich_score",
                name="ICH Score (Intracerebral Hemorrhage Score)",
                purpose="Predict 30-day mortality in spontaneous intracerebral hemorrhage",
                input_params=["gcs_score", "ich_volume_ml", "ivh_present", "infratentorial", "age"],
                output_type="ICH Score (0-6) with 30-day mortality prediction"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.NEUROLOGY,
                    Specialty.NEUROSURGERY,
                    Specialty.CRITICAL_CARE,
                    Specialty.EMERGENCY_MEDICINE,
                ),
                conditions=(
                    "Intracerebral Hemorrhage",
                    "ICH",
                    "Hemorrhagic Stroke",
                    "Brain Hemorrhage",
                    "Intraparenchymal Hemorrhage",
                    "Hypertensive Hemorrhage",
                ),
                clinical_contexts=(
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.SURGICAL_PLANNING,
                ),
                clinical_questions=(
                    "What is the prognosis for this ICH patient?",
                    "What is the 30-day mortality risk?",
                    "Should we consider surgical evacuation?",
                    "What should we tell the family about prognosis?",
                ),
                icd10_codes=("I61", "I61.0", "I61.1", "I61.9", "I62.9"),
                keywords=(
                    "ICH score", "intracerebral hemorrhage", "brain hemorrhage",
                    "hemorrhagic stroke", "prognosis", "mortality", "Hemphill",
                    "brain bleed", "hypertensive hemorrhage",
                )
            ),
            references=(
                Reference(
                    citation="Hemphill JC 3rd, Bonovich DC, Besmertis L, Manley GT, "
                             "Johnston SC. The ICH score: a simple, reliable grading "
                             "scale for intracerebral hemorrhage. "
                             "Stroke. 2001;32(4):891-897.",
                    doi="10.1161/01.str.32.4.891",
                    pmid="11283388",
                    year=2001
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )
    
    def calculate(
        self,
        gcs_score: int,
        ich_volume_ml: float,
        ivh_present: bool,
        infratentorial: bool,
        age: int,
    ) -> ScoreResult:
        """
        Calculate ICH Score.
        
        Args:
            gcs_score: Glasgow Coma Scale score (3-15)
            ich_volume_ml: ICH volume in milliliters (ABC/2 method typically)
            ivh_present: Intraventricular hemorrhage present
            infratentorial: Infratentorial (posterior fossa) origin
            age: Patient age in years
                
        Returns:
            ScoreResult with ICH Score and mortality prediction
        """
        # Validate inputs
        if not 3 <= gcs_score <= 15:
            raise ValueError("GCS score must be between 3 and 15")
        if ich_volume_ml < 0:
            raise ValueError("ICH volume must be non-negative")
        if age < 0 or age > 120:
            raise ValueError("Age must be between 0 and 120 years")
        
        # Calculate component scores
        gcs_points = self._get_gcs_points(gcs_score)
        volume_points = 1 if ich_volume_ml >= 30 else 0
        ivh_points = 1 if ivh_present else 0
        location_points = 1 if infratentorial else 0
        age_points = 1 if age >= 80 else 0
        
        # Total score
        total_score = gcs_points + volume_points + ivh_points + location_points + age_points
        
        # Get interpretation
        interpretation = self._get_interpretation(total_score)
        
        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "gcs_score": gcs_score,
                "ich_volume_ml": ich_volume_ml,
                "ivh_present": ivh_present,
                "infratentorial": infratentorial,
                "age": age,
            },
            calculation_details={
                "total_score": total_score,
                "components": {
                    "gcs": {
                        "value": gcs_score,
                        "points": gcs_points,
                        "criteria": self._get_gcs_criteria(gcs_score),
                    },
                    "ich_volume": {
                        "value": f"{ich_volume_ml:.1f} mL",
                        "points": volume_points,
                        "threshold": "≥30 mL = 1 point",
                    },
                    "ivh": {
                        "present": ivh_present,
                        "points": ivh_points,
                    },
                    "infratentorial": {
                        "present": infratentorial,
                        "points": location_points,
                    },
                    "age": {
                        "value": age,
                        "points": age_points,
                        "threshold": "≥80 years = 1 point",
                    },
                },
                "mortality_30_day": self._get_mortality(total_score),
            },
        )
    
    def _get_gcs_points(self, gcs_score: int) -> int:
        """Get points for GCS component"""
        if gcs_score <= 4:
            return 2
        elif gcs_score <= 12:
            return 1
        else:  # 13-15
            return 0
    
    def _get_gcs_criteria(self, gcs_score: int) -> str:
        """Get GCS criteria description"""
        if gcs_score <= 4:
            return f"GCS {gcs_score} (3-4 = 2 points)"
        elif gcs_score <= 12:
            return f"GCS {gcs_score} (5-12 = 1 point)"
        else:
            return f"GCS {gcs_score} (13-15 = 0 points)"
    
    def _get_mortality(self, score: int) -> str:
        """Get 30-day mortality percentage"""
        mortality_map = {
            0: "0%",
            1: "13%",
            2: "26%",
            3: "72%",
            4: "97%",
            5: "100%",
            6: "100%",
        }
        return mortality_map.get(score, "Unknown")
    
    def _get_interpretation(self, score: int) -> Interpretation:
        """Generate interpretation based on score"""
        
        # Mortality data from Hemphill et al. 2001
        mortality_map = {
            0: "0%",
            1: "13%",
            2: "26%",
            3: "72%",
            4: "97%",
            5: "100%",
            6: "100%",
        }
        mortality = mortality_map.get(score, "Unknown")
        
        if score == 0:
            return Interpretation(
                summary="ICH Score 0 - Excellent Prognosis",
                detail=(
                    f"ICH Score: {score}/6. 30-day mortality: {mortality}. "
                    "Excellent prognosis with no mortality in original validation cohort. "
                    "All negative prognostic factors absent."
                ),
                severity=Severity.NORMAL,
                stage=f"Score {score}",
                stage_description="Excellent prognosis",
                recommendations=(
                    "Standard ICH management with blood pressure control",
                    "Reversal of anticoagulation if applicable",
                    "Serial CT to monitor for hematoma expansion",
                    "ICU monitoring for first 24-48 hours",
                    "Early rehabilitation planning",
                ),
                warnings=(
                    "Score does not account for hematoma expansion risk",
                    "Serial neurological exams required",
                ),
                next_steps=(
                    "Repeat CT if neurological change",
                    "Blood pressure target per guidelines",
                    "Physical/occupational therapy evaluation",
                ),
            )
        elif score == 1:
            return Interpretation(
                summary="ICH Score 1 - Good Prognosis",
                detail=(
                    f"ICH Score: {score}/6. 30-day mortality: {mortality}. "
                    "Good prognosis. One adverse prognostic factor present. "
                    "Majority of patients survive with aggressive management."
                ),
                severity=Severity.MILD,
                stage=f"Score {score}",
                stage_description="Good prognosis",
                recommendations=(
                    "ICU admission for close monitoring",
                    "Aggressive blood pressure control",
                    "Serial imaging to detect expansion",
                    "Consider EVD if IVH with hydrocephalus",
                    "Early goals of care discussion",
                ),
                warnings=(
                    "Risk of hematoma expansion in first 24 hours",
                    "Watch for delayed hydrocephalus if IVH present",
                ),
                next_steps=(
                    "Serial neurological assessments",
                    "Repeat CT at 6 hours or with clinical change",
                    "Rehabilitation planning if stable",
                ),
            )
        elif score == 2:
            return Interpretation(
                summary="ICH Score 2 - Moderate Prognosis",
                detail=(
                    f"ICH Score: {score}/6. 30-day mortality: {mortality}. "
                    "Moderate prognosis with approximately 1 in 4 patients dying within 30 days. "
                    "Multiple adverse prognostic factors present."
                ),
                severity=Severity.MODERATE,
                stage=f"Score {score}",
                stage_description="Moderate prognosis",
                recommendations=(
                    "ICU care with aggressive medical management",
                    "Intracranial pressure monitoring if indicated",
                    "EVD placement for IVH with hydrocephalus",
                    "Goals of care discussion with family",
                    "Consider surgical evaluation for accessible hematomas",
                ),
                warnings=(
                    "Significant mortality risk - close monitoring essential",
                    "Risk of clinical deterioration from edema and expansion",
                ),
                next_steps=(
                    "Neurosurgical consultation",
                    "Serial imaging protocol",
                    "Family meeting for prognosis discussion",
                ),
            )
        elif score == 3:
            return Interpretation(
                summary="ICH Score 3 - Poor Prognosis",
                detail=(
                    f"ICH Score: {score}/6. 30-day mortality: {mortality}. "
                    "Poor prognosis with majority of patients not surviving. "
                    "However, score should inform, not determine, treatment decisions."
                ),
                severity=Severity.SEVERE,
                stage=f"Score {score}",
                stage_description="Poor prognosis",
                recommendations=(
                    "Intensive care with full support unless goals clarified",
                    "Urgent goals of care discussion with family",
                    "Consider surgical options in selected candidates",
                    "Avoid self-fulfilling prophecy from early withdrawal",
                    "Palliative care consultation for symptom management",
                ),
                warnings=(
                    "High mortality but some patients survive with good outcomes",
                    "Early withdrawal may worsen outcomes (self-fulfilling prophecy)",
                    "Score developed in era before modern ICH management",
                ),
                next_steps=(
                    "Multidisciplinary family meeting",
                    "Document patient wishes if known",
                    "Reassess at 48-72 hours for trajectory",
                ),
            )
        elif score == 4:
            return Interpretation(
                summary="ICH Score 4 - Very Poor Prognosis",
                detail=(
                    f"ICH Score: {score}/6. 30-day mortality: {mortality}. "
                    "Very poor prognosis with rare survival. However, individual variation "
                    "exists and score should not solely determine care limitations."
                ),
                severity=Severity.CRITICAL,
                stage=f"Score {score}",
                stage_description="Very poor prognosis",
                recommendations=(
                    "Immediate family meeting for goals of care",
                    "Consider comfort-focused care if consistent with patient values",
                    "If full support desired, continue aggressive treatment",
                    "Palliative care involvement recommended",
                    "Document decision-making process clearly",
                ),
                warnings=(
                    "Some survivors reported - avoid premature limitation of care",
                    "Score should not mandate withdrawal of treatment",
                    "Consider patient age and baseline function in decisions",
                ),
                next_steps=(
                    "Clarify goals with family/surrogate",
                    "Consider ethics consultation if conflict",
                    "Reassess trajectory at 72 hours",
                ),
            )
        else:  # score 5-6
            return Interpretation(
                summary=f"ICH Score {score} - Extremely Poor Prognosis",
                detail=(
                    f"ICH Score: {score}/6. 30-day mortality: {mortality}. "
                    "Extremely poor prognosis in original validation. "
                    "Maximum adverse prognostic factors present. "
                    "Compassionate, patient-centered care essential."
                ),
                severity=Severity.CRITICAL,
                stage=f"Score {score}",
                stage_description="Extremely poor prognosis",
                recommendations=(
                    "Urgent family meeting for goals of care",
                    "Discuss comfort-focused care if appropriate",
                    "Palliative care consultation",
                    "If aggressive care chosen, document reasoning",
                    "Spiritual care and family support",
                ),
                warnings=(
                    "Score should guide, not mandate, care limitations",
                    "Individual clinical judgment remains important",
                    "Consider potential for organ donation if appropriate",
                ),
                next_steps=(
                    "Goals of care documentation",
                    "Family support and grief counseling",
                    "Ensure comfort and dignity",
                ),
            )
