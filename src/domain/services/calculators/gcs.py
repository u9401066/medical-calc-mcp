"""
Glasgow Coma Scale (GCS)

The Glasgow Coma Scale is a neurological scale used to assess the level of
consciousness in patients with acute brain injury. It is one of the most
widely used coma scales.

Reference (Original):
    Teasdale G, Jennett B. Assessment of coma and impaired consciousness. 
    A practical scale. Lancet. 1974;2(7872):81-84.
    DOI: 10.1016/s0140-6736(74)91639-0
    PMID: 4136544

Reference (40-year update):
    Teasdale G, Maas A, Lecky F, et al. The Glasgow Coma Scale at 40 years: 
    standing the test of time. Lancet Neurol. 2014;13(8):844-854.
    DOI: 10.1016/S1474-4422(14)70120-6
    PMID: 25030516
"""


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


class GlasgowComaScaleCalculator(BaseCalculator):
    """
    Glasgow Coma Scale (GCS) Calculator
    
    The GCS assesses three aspects of responsiveness:
    1. Eye Opening (E): 1-4
    2. Verbal Response (V): 1-5
    3. Motor Response (M): 1-6
    
    Total score range: 3-15
    
    Classification:
    - Severe (GCS ≤ 8): Coma
    - Moderate (GCS 9-12): Moderate brain injury
    - Mild (GCS 13-15): Mild brain injury or normal
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="glasgow_coma_scale",
                name="Glasgow Coma Scale (GCS)",
                purpose="Assess level of consciousness and brain injury severity",
                input_params=["eye_response", "verbal_response", "motor_response"],
                output_type="GCS score (3-15) with injury classification"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.NEUROLOGY,
                    Specialty.CRITICAL_CARE,
                    Specialty.ANESTHESIOLOGY,
                    Specialty.SURGERY,
                ),
                conditions=(
                    "Traumatic Brain Injury",
                    "TBI",
                    "Altered Mental Status",
                    "Coma",
                    "Stroke",
                    "Intracranial Hemorrhage",
                    "Head Injury",
                    "Loss of Consciousness",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.MONITORING,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.SEDATION_ASSESSMENT,
                ),
                clinical_questions=(
                    "What is the patient's level of consciousness?",
                    "How severe is this brain injury?",
                    "Should this patient be intubated for airway protection?",
                    "Is the patient's mental status improving or worsening?",
                ),
                icd10_codes=("S06", "R40.20", "R40.21", "R40.22", "R40.23", "R40.24"),
                keywords=(
                    "GCS", "Glasgow Coma Scale", "consciousness", "coma",
                    "brain injury", "TBI", "mental status", "neurological",
                    "head injury", "intubation", "airway",
                )
            ),
            references=(
                Reference(
                    citation="Teasdale G, Jennett B. Assessment of coma and impaired consciousness. "
                             "A practical scale. Lancet. 1974;2(7872):81-84.",
                    doi="10.1016/s0140-6736(74)91639-0",
                    pmid="4136544",
                    year=1974
                ),
                Reference(
                    citation="Teasdale G, Maas A, Lecky F, et al. The Glasgow Coma Scale at 40 years: "
                             "standing the test of time. Lancet Neurol. 2014;13(8):844-854.",
                    doi="10.1016/S1474-4422(14)70120-6",
                    pmid="25030516",
                    year=2014
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )
    
    def calculate(
        self,
        eye_response: int,
        verbal_response: int,
        motor_response: int,
        is_intubated: bool = False,
    ) -> ScoreResult:
        """
        Calculate Glasgow Coma Scale score.
        
        Args:
            eye_response: Eye opening response (1-4)
                1 = None
                2 = To pressure/pain
                3 = To voice/sound
                4 = Spontaneous
            verbal_response: Verbal response (1-5)
                1 = None
                2 = Incomprehensible sounds
                3 = Inappropriate words
                4 = Confused
                5 = Oriented
            motor_response: Motor response (1-6)
                1 = None
                2 = Extension to pain (decerebrate)
                3 = Abnormal flexion (decorticate)
                4 = Withdrawal from pain
                5 = Localizes pain
                6 = Obeys commands
            is_intubated: If patient is intubated, verbal score cannot be assessed
                
        Returns:
            ScoreResult with GCS score and injury classification
        """
        # Validate inputs
        if not 1 <= eye_response <= 4:
            raise ValueError("Eye response must be between 1 and 4")
        if not 1 <= verbal_response <= 5:
            raise ValueError("Verbal response must be between 1 and 5")
        if not 1 <= motor_response <= 6:
            raise ValueError("Motor response must be between 1 and 6")
        
        # Calculate total score
        total_score = eye_response + verbal_response + motor_response
        
        # Format GCS notation (e.g., "E4V5M6 = 15")
        gcs_notation = f"E{eye_response}V{'T' if is_intubated else verbal_response}M{motor_response}"
        
        # Get interpretation
        interpretation = self._get_interpretation(
            total_score, eye_response, verbal_response, motor_response, is_intubated
        )
        
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
                "is_intubated": is_intubated,
            },
            calculation_details={
                "eye_response": {
                    "score": eye_response,
                    "description": self._get_eye_description(eye_response)
                },
                "verbal_response": {
                    "score": verbal_response,
                    "description": self._get_verbal_description(verbal_response),
                    "note": "Intubated - verbal cannot be assessed" if is_intubated else None
                },
                "motor_response": {
                    "score": motor_response,
                    "description": self._get_motor_description(motor_response)
                },
                "notation": gcs_notation,
                "total": total_score,
            },
            formula_used="GCS = Eye (1-4) + Verbal (1-5) + Motor (1-6)"
        )
    
    def _get_eye_description(self, score: int) -> str:
        descriptions = {
            1: "None - no eye opening",
            2: "To pressure - eye opening to painful stimuli",
            3: "To sound - eye opening to verbal command",
            4: "Spontaneous - eyes open spontaneously",
        }
        return descriptions.get(score, "Unknown")
    
    def _get_verbal_description(self, score: int) -> str:
        descriptions = {
            1: "None - no verbal response",
            2: "Sounds - incomprehensible sounds/moaning",
            3: "Words - inappropriate words, random speech",
            4: "Confused - confused but conversational",
            5: "Oriented - oriented, appropriate responses",
        }
        return descriptions.get(score, "Unknown")
    
    def _get_motor_description(self, score: int) -> str:
        descriptions = {
            1: "None - no motor response",
            2: "Extension - decerebrate posturing",
            3: "Abnormal flexion - decorticate posturing",
            4: "Withdrawal - withdraws from painful stimuli",
            5: "Localizing - localizes to painful stimuli",
            6: "Obeys - obeys commands",
        }
        return descriptions.get(score, "Unknown")
    
    def _get_interpretation(
        self,
        total: int,
        eye: int,
        verbal: int,
        motor: int,
        intubated: bool
    ) -> Interpretation:
        """Get interpretation based on GCS score"""
        
        if total <= 8:
            return Interpretation(
                summary=f"GCS {total}: Severe brain injury / Coma",
                detail=f"GCS ≤ 8 indicates coma. Patient cannot follow commands and has "
                       f"severely impaired consciousness. Airway protection is typically required.",
                severity=Severity.CRITICAL,
                stage="Severe",
                stage_description="Severe brain injury / Coma",
                recommendations=(
                    "Immediate airway management - consider intubation if not already done",
                    "Head CT if not already obtained",
                    "Neurosurgical consultation",
                    "ICU admission",
                    "Maintain MAP > 80 mmHg, CPP > 60 mmHg if ICP monitored",
                ),
                warnings=(
                    "GCS ≤ 8: Traditional threshold for intubation",
                    "High mortality risk",
                    "Unable to protect airway",
                ),
                next_steps=(
                    "Secure airway",
                    "Neuroimaging",
                    "Neurosurgery consult",
                    "ICP monitoring consideration",
                    "Frequent neuro checks",
                )
            )
        elif total <= 12:
            return Interpretation(
                summary=f"GCS {total}: Moderate brain injury",
                detail=f"GCS 9-12 indicates moderate brain injury. Patient may follow simple "
                       f"commands but has impaired consciousness.",
                severity=Severity.SEVERE,
                stage="Moderate",
                stage_description="Moderate brain injury",
                recommendations=(
                    "Close neurological monitoring",
                    "Consider head CT",
                    "Neurosurgical consultation if not improving",
                    "Airway assessment - may need protection",
                    "Serial GCS monitoring every 1-2 hours",
                ),
                warnings=(
                    "May deteriorate to severe injury",
                    "May need airway protection if worsening",
                ),
                next_steps=(
                    "Serial GCS assessments",
                    "Consider ICU/step-down admission",
                    "Neuroimaging if indicated",
                    "Watch for signs of herniation",
                )
            )
        elif total <= 14:
            return Interpretation(
                summary=f"GCS {total}: Mild brain injury",
                detail=f"GCS 13-14 indicates mild brain injury. Patient is conscious but may "
                       f"be confused or have minor neurological deficits.",
                severity=Severity.MILD,
                stage="Mild",
                stage_description="Mild brain injury",
                recommendations=(
                    "Observation and serial neurological exams",
                    "Consider head CT based on clinical scenario",
                    "Follow head injury observation protocols",
                    "Patient/family education on warning signs",
                ),
                warnings=(
                    "Watch for deterioration",
                    "Return precautions should be given",
                ),
                next_steps=(
                    "Serial GCS assessments every 2-4 hours",
                    "Consider CT based on Canadian/New Orleans criteria",
                    "Discharge with instructions if appropriate",
                )
            )
        else:  # GCS 15
            return Interpretation(
                summary=f"GCS {total}: Normal consciousness",
                detail=f"GCS 15 indicates normal level of consciousness. Patient is fully alert "
                       f"and oriented with normal responses.",
                severity=Severity.NORMAL,
                stage="Normal",
                stage_description="Normal consciousness",
                recommendations=(
                    "Routine assessment as clinically indicated",
                    "Consider other causes if concern for brain injury",
                    "Clinical decision rules for neuroimaging if head trauma",
                ),
                next_steps=(
                    "Continue routine care",
                    "Evaluate for other pathology if clinically concerning",
                )
            )
