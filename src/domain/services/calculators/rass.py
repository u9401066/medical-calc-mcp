"""
Richmond Agitation-Sedation Scale (RASS) Calculator

The RASS is a 10-point scale used to assess the level of agitation or sedation
in ICU patients.

Reference:
    Sessler CN, Gosnell MS, Grap MJ, et al. The Richmond Agitation-Sedation Scale:
    validity and reliability in adult intensive care unit patients. Am J Respir
    Crit Care Med. 2002;166(10):1338-1344.
    DOI: 10.1164/rccm.2107138
    PMID: 12421743

    Ely EW, Truman B, Shintani A, et al. Monitoring sedation status over time in
    ICU patients: reliability and validity of the Richmond Agitation-Sedation
    Scale (RASS). JAMA. 2003;289(22):2983-2991.
    DOI: 10.1001/jama.289.22.2983
    PMID: 12799407
"""

from typing import Literal

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator

# RASS ranges from -5 (unarousable) to +4 (combative)
RASS_SCORE = Literal[-5, -4, -3, -2, -1, 0, 1, 2, 3, 4]


class RassCalculator(BaseCalculator):
    """
    Richmond Agitation-Sedation Scale (RASS)

    A validated scale for assessing sedation level and agitation in ICU patients.
    Used to guide sedation titration and assess for delirium.

    Score Definitions:
        +4 Combative: Overtly combative, violent, immediate danger to staff
        +3 Very agitated: Pulls/removes tubes or catheters; aggressive
        +2 Agitated: Frequent non-purposeful movement, fights ventilator
        +1 Restless: Anxious but movements not aggressive or vigorous
         0 Alert and calm
        -1 Drowsy: Not fully alert, but sustained awakening to voice (>10 sec)
        -2 Light sedation: Briefly awakens to voice with eye contact (<10 sec)
        -3 Moderate sedation: Movement or eye opening to voice, no eye contact
        -4 Deep sedation: No response to voice, movement to physical stimulation
        -5 Unarousable: No response to voice or physical stimulation
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="rass",
                name="Richmond Agitation-Sedation Scale (RASS)",
                purpose="Assess level of agitation or sedation in ICU patients",
                input_params=["rass_score"],
                output_type="RASS Score (-5 to +4) with sedation level interpretation",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.ANESTHESIOLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.NEUROLOGY,
                ),
                conditions=(
                    "Sedation Assessment",
                    "Agitation",
                    "Delirium",
                    "Mechanical Ventilation",
                    "ICU Care",
                ),
                clinical_contexts=(
                    ClinicalContext.SEDATION_ASSESSMENT,
                    ClinicalContext.ICU_MANAGEMENT,
                    ClinicalContext.VENTILATOR_MANAGEMENT,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "Is this patient adequately sedated?",
                    "Is the patient too sedated or not sedated enough?",
                    "What is the RASS score?",
                    "Can we do a sedation vacation?",
                    "Is the patient ready for extubation?",
                    "Is this patient agitated?",
                ),
                icd10_codes=(
                    "R40.0",  # Somnolence
                    "R41.82",  # Altered mental status
                    "R45.1",  # Restlessness and agitation
                    "F05",  # Delirium
                ),
                keywords=(
                    "RASS",
                    "sedation",
                    "agitation",
                    "sedation scale",
                    "ICU",
                    "delirium",
                    "sedation assessment",
                    "sedation vacation",
                    "oversedation",
                    "undersedation",
                    "light sedation",
                ),
            ),
            references=(
                Reference(
                    citation="Sessler CN, Gosnell MS, Grap MJ, et al. The Richmond Agitation-Sedation "
                    "Scale: validity and reliability in adult intensive care unit patients. "
                    "Am J Respir Crit Care Med. 2002;166(10):1338-1344.",
                    doi="10.1164/rccm.2107138",
                    pmid="12421743",
                    year=2002,
                ),
                Reference(
                    citation="Ely EW, Truman B, Shintani A, et al. Monitoring sedation status over "
                    "time in ICU patients: reliability and validity of the Richmond "
                    "Agitation-Sedation Scale (RASS). JAMA. 2003;289(22):2983-2991.",
                    doi="10.1001/jama.289.22.2983",
                    pmid="12799407",
                    year=2003,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(self, rass_score: RASS_SCORE) -> ScoreResult:
        """
        Document and interpret RASS score.

        Args:
            rass_score: RASS score from -5 to +4 based on assessment:
                +4: Combative
                +3: Very agitated
                +2: Agitated
                +1: Restless
                 0: Alert and calm
                -1: Drowsy
                -2: Light sedation
                -3: Moderate sedation
                -4: Deep sedation
                -5: Unarousable

        Returns:
            ScoreResult with RASS interpretation and management recommendations
        """
        if rass_score < -5 or rass_score > 4:
            raise ValueError("RASS score must be between -5 and +4")

        # Get interpretation
        interpretation = self._get_interpretation(rass_score)

        # Get category description
        category = self._get_category_description(rass_score)

        return ScoreResult(
            value=float(rass_score),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={"rass_score": rass_score},
            calculation_details={"score": rass_score, "category": category["name"], "description": category["description"]},
            notes=[
                "Assess RASS before CAM-ICU for delirium screening",
                "Target RASS of -2 to 0 for most ICU patients",
                "RASS -3 to -5: patient cannot be assessed for delirium",
                "Daily sedation interruption recommended for most patients",
            ],
        )

    def _get_category_description(self, rass_score: int) -> dict[str, str]:
        """Get category name and description for RASS score"""
        categories = {
            4: {"name": "Combative", "description": "Overtly combative, violent, immediate danger to staff"},
            3: {"name": "Very agitated", "description": "Pulls or removes tubes or catheters; aggressive behavior"},
            2: {"name": "Agitated", "description": "Frequent non-purposeful movement, fights ventilator"},
            1: {"name": "Restless", "description": "Anxious but movements not aggressive or vigorous"},
            0: {"name": "Alert and calm", "description": "Spontaneously pays attention to caregiver"},
            -1: {"name": "Drowsy", "description": "Not fully alert, but has sustained awakening (eye-opening/eye contact) to voice (>10 seconds)"},
            -2: {"name": "Light sedation", "description": "Briefly awakens with eye contact to voice (<10 seconds)"},
            -3: {"name": "Moderate sedation", "description": "Movement or eye opening to voice but no eye contact"},
            -4: {"name": "Deep sedation", "description": "No response to voice, but movement or eye opening to physical stimulation"},
            -5: {"name": "Unarousable", "description": "No response to voice or physical stimulation"},
        }
        return categories.get(rass_score, {"name": "Unknown", "description": ""})

    def _get_interpretation(self, rass_score: int) -> Interpretation:
        """Get clinical interpretation for RASS score"""

        category = self._get_category_description(rass_score)

        if rass_score >= 3:
            # Combative or very agitated
            return Interpretation(
                summary=f"RASS +{rass_score}: {category['name']} - Immediate intervention needed",
                detail=category["description"] + ". Patient poses risk to self and staff.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage=category["name"],
                stage_description=f"RASS +{rass_score}",
                recommendations=(
                    "Ensure patient safety and staff safety",
                    "Rule out underlying cause (pain, hypoxia, hypoglycemia, drug withdrawal)",
                    "Consider antipsychotic (haloperidol, quetiapine)",
                    "Increase sedation if on mechanical ventilation",
                    "Soft restraints may be needed temporarily",
                ),
                warnings=(
                    "Risk of self-extubation",
                    "Risk of line/device removal",
                    "Risk of falls or injury",
                    "Staff injury risk",
                ),
                next_steps=(
                    "Address underlying cause",
                    "Titrate sedation to target",
                    "Frequent reassessment",
                ),
            )
        elif rass_score >= 1:
            # Restless or agitated
            return Interpretation(
                summary=f"RASS +{rass_score}: {category['name']} - Mild agitation",
                detail=category["description"] + ". Monitor closely and address underlying causes.",
                severity=Severity.MILD,
                risk_level=RiskLevel.INTERMEDIATE,
                stage=category["name"],
                stage_description=f"RASS +{rass_score}",
                recommendations=(
                    "Assess and treat pain (use BPS or CPOT)",
                    "Rule out hypoxia, urinary retention, constipation",
                    "Provide reassurance and reorientation",
                    "Consider PRN anxiolytic if needed",
                ),
                next_steps=(
                    "Address reversible causes",
                    "Non-pharmacologic interventions first",
                    "Reassess in 30 minutes",
                ),
            )
        elif rass_score == 0:
            # Alert and calm - optimal for most patients
            return Interpretation(
                summary=f"RASS 0: {category['name']} - Optimal",
                detail=category["description"] + ". Ideal sedation level for most ICU patients.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.VERY_LOW,
                stage=category["name"],
                stage_description="RASS 0",
                recommendations=(
                    "Maintain current sedation strategy",
                    "Perform CAM-ICU to assess for delirium",
                    "Continue daily sedation vacation if applicable",
                ),
                next_steps=(
                    "Continue current management",
                    "Assess for delirium with CAM-ICU",
                    "Evaluate readiness for weaning/extubation if intubated",
                ),
            )
        elif rass_score == -1:
            # Drowsy - acceptable for many patients
            return Interpretation(
                summary=f"RASS -1: {category['name']} - Appropriate for many patients",
                detail=category["description"] + ". Acceptable sedation level; patient can still be assessed for delirium.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.VERY_LOW,
                stage=category["name"],
                stage_description="RASS -1",
                recommendations=(
                    "This is within target range for most patients",
                    "Perform CAM-ICU for delirium assessment",
                    "Consider lightening sedation if appropriate",
                ),
                next_steps=(
                    "Assess for delirium with CAM-ICU",
                    "Continue weaning sedation if indicated",
                ),
            )
        elif rass_score == -2:
            # Light sedation - common target
            return Interpretation(
                summary=f"RASS -2: {category['name']} - Common target sedation",
                detail=category["description"] + ". Acceptable for most patients on ventilator; can still assess for delirium.",
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage=category["name"],
                stage_description="RASS -2",
                recommendations=(
                    "Common target for ventilated patients",
                    "CAM-ICU still possible at this level",
                    "Continue sedation vacation protocols",
                    "Consider reducing sedation to RASS 0 to -1",
                ),
                next_steps=(
                    "Perform CAM-ICU if not recently done",
                    "Assess readiness for spontaneous breathing trial",
                ),
            )
        elif rass_score == -3:
            # Moderate sedation - may be too deep for many
            return Interpretation(
                summary=f"RASS -3: {category['name']} - Deeper sedation",
                detail=category["description"] + ". CAM-ICU cannot be performed. Consider if this depth of sedation is necessary.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage=category["name"],
                stage_description="RASS -3",
                recommendations=(
                    "Cannot assess for delirium at this level",
                    "Evaluate if deep sedation is clinically necessary",
                    "Consider reducing sedation if stable",
                    "Document indication for deeper sedation",
                ),
                warnings=(
                    "Deep sedation associated with longer ventilator days",
                    "Increased risk of ICU-acquired weakness",
                    "Delirium assessment not possible",
                ),
                next_steps=(
                    "Consider sedation vacation",
                    "Reassess need for deep sedation",
                    "Reduce sedation if ARDS/refractory hypoxemia resolved",
                ),
            )
        elif rass_score == -4:
            # Deep sedation
            return Interpretation(
                summary=f"RASS -4: {category['name']} - Deep sedation",
                detail=category["description"] + ". Very deep sedation; only appropriate for specific indications.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage=category["name"],
                stage_description="RASS -4",
                recommendations=(
                    "Document indication (ARDS, neuromuscular blockade, status epilepticus, etc.)",
                    "Plan for lightening sedation when possible",
                    "Ensure train-of-four monitoring if paralyzed",
                    "Daily evaluation for sedation reduction",
                ),
                warnings=(
                    "Prolonged deep sedation increases delirium risk",
                    "Associated with longer ICU stay",
                    "ICU-acquired weakness risk",
                ),
                next_steps=(
                    "Daily assessment for sedation lightening",
                    "Document ongoing need for deep sedation",
                ),
            )
        else:
            # -5: Unarousable
            return Interpretation(
                summary=f"RASS -5: {category['name']} - Unresponsive",
                detail=category["description"] + ". Patient completely unresponsive. Consider etiologies beyond sedation.",
                severity=Severity.CRITICAL,
                risk_level=RiskLevel.HIGH,
                stage=category["name"],
                stage_description="RASS -5",
                recommendations=(
                    "Rule out oversedation, neurologic event, metabolic derangement",
                    "Check pupils and consider neurologic exam",
                    "Consider reducing/holding sedation",
                    "If unexplained, consider CT head or EEG",
                ),
                warnings=(
                    "May indicate oversedation or neurologic emergency",
                    "Verify this is expected if on deep sedation protocol",
                    "Prolonged unresponsiveness requires investigation",
                ),
                next_steps=(
                    "Stop sedation and reassess",
                    "Neurologic assessment",
                    "Consider imaging if no improvement off sedation",
                ),
            )
