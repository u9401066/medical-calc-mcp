"""
Hunt and Hess Scale

The Hunt and Hess Scale is a clinical grading system for subarachnoid
hemorrhage (SAH) that predicts patient outcomes based on clinical
presentation on admission.

Reference (Original):
    Hunt WE, Hess RM. Surgical risk as related to time of intervention
    in the repair of intracranial aneurysms. J Neurosurg. 1968;28(1):14-20.
    DOI: 10.3171/jns.1968.28.1.0014
    PMID: 5635959

Clinical Notes:
- Grade I-III: Generally considered for early surgery (within 72 hours)
- Grade IV-V: Often delayed surgery until clinical improvement
- Perioperative mortality increases significantly with each grade
- Modified versions exist but original scale remains widely used
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class HuntHessCalculator(BaseCalculator):
    """
    Hunt and Hess Scale Calculator

    Grades subarachnoid hemorrhage severity based on clinical presentation.

    Grading:
    - Grade I: Asymptomatic or minimal headache, slight nuchal rigidity
    - Grade II: Moderate to severe headache, nuchal rigidity, no deficit
                except cranial nerve palsy
    - Grade III: Drowsiness, confusion, or mild focal deficit
    - Grade IV: Stupor, moderate to severe hemiparesis, possible early
                decerebrate rigidity, vegetative disturbances
    - Grade V: Deep coma, decerebrate rigidity, moribund appearance

    Mortality by Grade (approximate):
    - Grade I: 1-2%
    - Grade II: 5%
    - Grade III: 15-20%
    - Grade IV: 30-40%
    - Grade V: 50-80%
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="hunt_hess",
                name="Hunt and Hess Scale",
                purpose="Grade subarachnoid hemorrhage severity and predict surgical risk",
                input_params=["grade"],
                output_type="Hunt & Hess Grade (I-V) with mortality prediction",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.NEUROLOGY,
                    Specialty.NEUROSURGERY,
                    Specialty.CRITICAL_CARE,
                    Specialty.EMERGENCY_MEDICINE,
                ),
                conditions=(
                    "Subarachnoid Hemorrhage",
                    "SAH",
                    "Intracranial Aneurysm",
                    "Aneurysmal SAH",
                    "Cerebral Aneurysm",
                    "Brain Hemorrhage",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.SURGICAL_PLANNING,
                ),
                clinical_questions=(
                    "How severe is this subarachnoid hemorrhage?",
                    "What is the surgical risk for this SAH patient?",
                    "Should surgery be performed early or delayed?",
                    "What is the expected mortality for this SAH grade?",
                ),
                icd10_codes=("I60", "I60.0", "I60.9", "I67.1"),
                keywords=(
                    "Hunt and Hess",
                    "Hunt Hess",
                    "SAH",
                    "subarachnoid",
                    "hemorrhage",
                    "aneurysm",
                    "grading",
                    "neurosurgery",
                    "brain bleed",
                    "surgery timing",
                ),
            ),
            references=(
                Reference(
                    citation="Hunt WE, Hess RM. Surgical risk as related to time of "
                    "intervention in the repair of intracranial aneurysms. "
                    "J Neurosurg. 1968;28(1):14-20.",
                    doi="10.3171/jns.1968.28.1.0014",
                    pmid="5635959",
                    year=1968,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        grade: int,
    ) -> ScoreResult:
        """
        Calculate Hunt and Hess Score.

        Args:
            grade: Hunt & Hess grade (1-5)
                1 = Asymptomatic or minimal headache, slight nuchal rigidity
                2 = Moderate-severe headache, nuchal rigidity, ± cranial nerve palsy
                3 = Drowsiness, confusion, or mild focal deficit
                4 = Stupor, moderate-severe hemiparesis, early decerebrate rigidity
                5 = Deep coma, decerebrate rigidity, moribund appearance

        Returns:
            ScoreResult with grade and mortality prediction
        """
        # Validate input
        if not 1 <= grade <= 5:
            raise ValueError("Hunt and Hess grade must be between 1 and 5")

        # Get interpretation
        interpretation = self._get_interpretation(grade)

        return ScoreResult(
            value=grade,
            unit=Unit.GRADE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={"grade": grade},
            calculation_details={
                "grade": grade,
                "grade_roman": self._to_roman(grade),
                "description": self._get_grade_description(grade),
                "mortality_risk": self._get_mortality(grade),
                "surgery_timing": self._get_surgery_timing(grade),
            },
        )

    def _to_roman(self, grade: int) -> str:
        """Convert grade to Roman numeral"""
        roman_map = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}
        return roman_map.get(grade, str(grade))

    def _get_grade_description(self, grade: int) -> str:
        """Get clinical description for each grade"""
        descriptions = {
            1: "Asymptomatic or minimal headache, slight nuchal rigidity",
            2: "Moderate to severe headache, nuchal rigidity, no neurological deficit except cranial nerve palsy",
            3: "Drowsiness, confusion, or mild focal neurological deficit",
            4: "Stupor, moderate to severe hemiparesis, possible early decerebrate rigidity, vegetative disturbances",
            5: "Deep coma, decerebrate rigidity, moribund appearance",
        }
        return descriptions.get(grade, "Unknown grade")

    def _get_mortality(self, grade: int) -> dict[str, str]:
        """Get mortality risk for each grade"""
        mortality: dict[int, dict[str, str]] = {
            1: {"operative": "1-2%", "overall": "2-5%"},
            2: {"operative": "5%", "overall": "5-10%"},
            3: {"operative": "15-20%", "overall": "15-25%"},
            4: {"operative": "30-40%", "overall": "40-50%"},
            5: {"operative": "50-80%", "overall": "70-90%"},
        }
        return mortality.get(grade, {})

    def _get_surgery_timing(self, grade: int) -> str:
        """Get recommended surgery timing"""
        if grade <= 3:
            return "Early surgery (within 72 hours) generally recommended"
        elif grade == 4:
            return "Surgery timing controversial; may delay until improvement"
        else:  # grade 5
            return "Surgery typically delayed; medical stabilization first"

    def _get_interpretation(self, grade: int) -> Interpretation:
        """Generate interpretation based on grade"""
        if grade == 1:
            return Interpretation(
                summary="Hunt & Hess Grade I - Minimal symptoms",
                detail="Asymptomatic or minimal headache with slight nuchal rigidity. Excellent prognosis with low surgical risk.",
                severity=Severity.MILD,
                stage="Grade I",
                stage_description="Minimal symptoms - excellent prognosis",
                recommendations=(
                    "Early surgery (within 72 hours) recommended to prevent rebleeding",
                    "Nimodipine 60mg q4h for vasospasm prophylaxis",
                    "ICU monitoring for vasospasm period (days 3-14)",
                    "Blood pressure management",
                ),
                next_steps=(
                    "Aneurysm securing (coiling or clipping)",
                    "Daily TCD monitoring for vasospasm",
                    "Serial neurological exams",
                ),
            )
        elif grade == 2:
            return Interpretation(
                summary="Hunt & Hess Grade II - Moderate symptoms",
                detail="Moderate to severe headache with nuchal rigidity. No neurological deficit except possible cranial nerve palsy. Good prognosis.",
                severity=Severity.MILD,
                stage="Grade II",
                stage_description="Moderate symptoms - good prognosis",
                recommendations=(
                    "Early surgery recommended",
                    "Nimodipine 60mg q4h x 21 days",
                    "Monitor for vasospasm - TCD daily",
                    "Aggressive blood pressure control",
                ),
                next_steps=(
                    "Secure aneurysm within 72 hours",
                    "Vasospasm surveillance",
                    "Pain management",
                ),
            )
        elif grade == 3:
            return Interpretation(
                summary="Hunt & Hess Grade III - Significant neurological impairment",
                detail="Drowsiness, confusion, or mild focal neurological deficit. Moderate surgical risk. Intensive monitoring required.",
                severity=Severity.MODERATE,
                stage="Grade III",
                stage_description="Significant impairment - moderate risk",
                recommendations=(
                    "Early surgery still generally recommended",
                    "Vasospasm prophylaxis essential (nimodipine)",
                    "Consider EVD if hydrocephalus present",
                    "Aggressive neuro-ICU monitoring",
                ),
                warnings=(
                    "Increased surgical risk (15-20% mortality)",
                    "Higher vasospasm risk",
                    "May deteriorate before surgery",
                ),
                next_steps=(
                    "Aneurysm treatment planning",
                    "EVD placement if needed",
                    "Frequent neuro checks",
                ),
            )
        elif grade == 4:
            return Interpretation(
                summary="Hunt & Hess Grade IV - Severe impairment",
                detail="Stupor with moderate to severe hemiparesis. Possible early decerebrate rigidity and vegetative disturbances. High surgical risk.",
                severity=Severity.SEVERE,
                stage="Grade IV",
                stage_description="Severe impairment - high surgical risk",
                recommendations=(
                    "Surgery timing controversial - may delay until improvement",
                    "ICU monitoring essential",
                    "Consider EVD for hydrocephalus or elevated ICP",
                    "Aggressive medical management",
                ),
                warnings=(
                    "High surgical mortality (30-40%)",
                    "Poor neurological outcome likely",
                    "May require prolonged ICU care",
                ),
                next_steps=(
                    "Stabilize medically first",
                    "Reassess daily for improvement",
                    "Family goals of care discussion",
                ),
            )
        else:  # grade 5
            return Interpretation(
                summary="Hunt & Hess Grade V - Critical / Moribund",
                detail="Deep coma with decerebrate rigidity and moribund appearance. Very poor prognosis. Surgery typically delayed.",
                severity=Severity.CRITICAL,
                stage="Grade V",
                stage_description="Moribund - very high surgical risk",
                recommendations=(
                    "Surgery typically delayed until clinical improvement",
                    "Focus on medical stabilization",
                    "Goals of care discussion with family essential",
                    "Consider comfort-focused care if no improvement",
                ),
                warnings=(
                    "Very high surgical mortality (50-80%)",
                    "Rare neurological recovery",
                    "Consider palliative care consultation",
                ),
                next_steps=(
                    "Medical stabilization",
                    "Serial neurological assessment",
                    "Family meeting for prognosis discussion",
                ),
            )
