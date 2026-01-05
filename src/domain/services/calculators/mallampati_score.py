"""
Mallampati Score Calculator

The Modified Mallampati Classification is used for predicting difficult intubation
based on the visibility of oropharyngeal structures.

Reference:
    Mallampati SR, Gatt SP, Gugino LD, et al. A clinical sign to predict difficult
    tracheal intubation: a prospective study. Can Anaesth Soc J. 1985;32(4):429-434.
    DOI: 10.1007/BF03011357
    PMID: 4027773

    Samsoon GL, Young JR. Difficult tracheal intubation: a retrospective study.
    Anaesthesia. 1987;42(5):487-490.
    DOI: 10.1111/j.1365-2044.1987.tb04039.x
    PMID: 3592174
"""

from typing import Literal

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator

MALLAMPATI_CLASS = Literal[1, 2, 3, 4]


class MallampatiScoreCalculator(BaseCalculator):
    """
    Modified Mallampati Classification

    Used to assess and predict difficult intubation based on visualization
    of oropharyngeal structures with mouth fully opened and tongue protruded.

    The original Mallampati classification (1985) had 3 classes.
    Samsoon and Young (1987) modified it to 4 classes.

    Classes (Modified):
        Class I: Soft palate, fauces, uvula, anterior and posterior pillars visible
        Class II: Soft palate, fauces, uvula visible
        Class III: Soft palate, base of uvula visible
        Class IV: Soft palate not visible at all
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="mallampati_score",
                name="Mallampati Score (Modified)",
                purpose="Predict difficult intubation based on oropharyngeal visualization",
                input_params=["mallampati_class"],
                output_type="Mallampati Class I-IV with intubation difficulty prediction"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ANESTHESIOLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.PULMONOLOGY,
                    Specialty.ENT,
                ),
                conditions=(
                    "Difficult Airway",
                    "Difficult Intubation",
                    "Airway Assessment",
                    "Preoperative Evaluation",
                ),
                clinical_contexts=(
                    ClinicalContext.AIRWAY_MANAGEMENT,
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                    ClinicalContext.RISK_STRATIFICATION,
                ),
                clinical_questions=(
                    "Will this patient be difficult to intubate?",
                    "What is the Mallampati score?",
                    "What is the airway risk?",
                    "Can I visualize the oropharynx?",
                    "What is the difficult airway risk?",
                ),
                icd10_codes=(
                    "Z53.09",  # Procedure not carried out for other reasons
                    "T88.4",   # Failed or difficult intubation
                ),
                keywords=(
                    "Mallampati", "airway", "intubation", "difficult airway",
                    "oropharynx", "uvula", "soft palate", "visualization",
                    "airway assessment", "preoperative",
                )
            ),
            references=(
                Reference(
                    citation="Mallampati SR, Gatt SP, Gugino LD, et al. A clinical sign to predict "
                             "difficult tracheal intubation: a prospective study. Can Anaesth Soc J. "
                             "1985;32(4):429-434.",
                    doi="10.1007/BF03011357",
                    pmid="4027773",
                    year=1985
                ),
                Reference(
                    citation="Samsoon GL, Young JR. Difficult tracheal intubation: a retrospective "
                             "study. Anaesthesia. 1987;42(5):487-490.",
                    doi="10.1111/j.1365-2044.1987.tb04039.x",
                    pmid="3592174",
                    year=1987
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )

    def calculate(
        self,
        mallampati_class: MALLAMPATI_CLASS
    ) -> ScoreResult:
        """
        Classify patient using Modified Mallampati Classification.

        Args:
            mallampati_class: Mallampati class (1-4) based on visualization:
                1: Soft palate, uvula, fauces, pillars visible
                2: Soft palate, uvula, fauces visible
                3: Soft palate, base of uvula visible
                4: Hard palate only visible

        Returns:
            ScoreResult with Mallampati classification and intubation difficulty prediction
        """
        if mallampati_class not in (1, 2, 3, 4):
            raise ValueError("Mallampati class must be 1, 2, 3, or 4")

        # Get interpretation
        interpretation = self._get_interpretation(mallampati_class)

        return ScoreResult(
            value=float(mallampati_class),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "mallampati_class": mallampati_class
            },
            calculation_details={
                "classification": f"Class {self._to_roman(mallampati_class)}",
                "visible_structures": self._get_visible_structures(mallampati_class)
            },
            notes=[
                "Assessment performed with patient sitting upright",
                "Mouth fully open, tongue maximally protruded",
                "Without phonation (no 'ah' sound)",
                "Mallampati alone has limited sensitivity; combine with other predictors",
            ]
        )

    def _to_roman(self, num: int) -> str:
        """Convert number to Roman numeral"""
        roman = {1: "I", 2: "II", 3: "III", 4: "IV"}
        return roman.get(num, str(num))

    def _get_visible_structures(self, mallampati_class: int) -> list[str]:
        """Get list of visible structures for each class"""
        structures = {
            1: ["Hard palate", "Soft palate", "Uvula", "Fauces", "Anterior pillars", "Posterior pillars"],
            2: ["Hard palate", "Soft palate", "Uvula", "Fauces"],
            3: ["Hard palate", "Soft palate", "Base of uvula only"],
            4: ["Hard palate only"]
        }
        return structures.get(mallampati_class, [])

    def _get_interpretation(self, mallampati_class: int) -> Interpretation:
        """Get clinical interpretation for Mallampati class"""

        if mallampati_class == 1:
            return Interpretation(
                summary="Mallampati Class I: Full visualization",
                detail="Soft palate, fauces, uvula, anterior and posterior tonsillar pillars visible. "
                       "Suggests easy laryngoscopy and intubation.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.VERY_LOW,
                stage="Class I",
                stage_description="Full oropharyngeal visualization",
                recommendations=(
                    "Standard intubation approach likely successful",
                    "Normal airway equipment should suffice",
                ),
                next_steps=(
                    "Assess other difficult airway predictors (thyromental distance, neck mobility, etc.)",
                    "Proceed with standard airway management plan",
                )
            )
        elif mallampati_class == 2:
            return Interpretation(
                summary="Mallampati Class II: Partial visualization",
                detail="Soft palate, fauces, and uvula visible. Tonsillar pillars obscured. "
                       "Suggests likely easy laryngoscopy.",
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="Class II",
                stage_description="Partial oropharyngeal visualization",
                recommendations=(
                    "Standard intubation approach usually successful",
                    "Have backup airway equipment available",
                ),
                next_steps=(
                    "Complete difficult airway assessment",
                    "Standard airway management with backup plan",
                )
            )
        elif mallampati_class == 3:
            return Interpretation(
                summary="Mallampati Class III: Limited visualization",
                detail="Only soft palate and base of uvula visible. "
                       "Moderate predictor of difficult laryngoscopy.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Class III",
                stage_description="Limited oropharyngeal visualization",
                recommendations=(
                    "Anticipate potentially difficult laryngoscopy",
                    "Video laryngoscope recommended as primary device",
                    "Have difficult airway equipment immediately available",
                    "Consider awake intubation if other risk factors present",
                ),
                warnings=(
                    "Increased risk of Cormack-Lehane Grade III/IV view",
                    "Multiple intubation attempts may be needed",
                ),
                next_steps=(
                    "Thorough difficult airway assessment",
                    "Prepare difficult airway cart",
                    "Have experienced backup available",
                )
            )
        else:  # mallampati_class == 4
            return Interpretation(
                summary="Mallampati Class IV: No soft palate visualization",
                detail="Only hard palate visible; soft palate not visible at all. "
                       "Strong predictor of difficult intubation.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage="Class IV",
                stage_description="Minimal oropharyngeal visualization",
                recommendations=(
                    "High likelihood of difficult or failed intubation",
                    "Strongly consider awake fiberoptic intubation",
                    "Video laryngoscope mandatory if direct laryngoscopy attempted",
                    "Have all difficult airway equipment ready",
                    "Consider surgical airway backup",
                ),
                warnings=(
                    "High risk of difficult mask ventilation",
                    "High risk of failed intubation",
                    "Cannot intubate, cannot oxygenate (CICO) risk",
                ),
                next_steps=(
                    "Formulate difficult airway plan with team",
                    "Discuss awake intubation with patient",
                    "Ensure ENT/surgical backup if needed",
                    "Brief team on emergency airway protocol",
                )
            )
