"""
ASA Physical Status Classification Calculator

The ASA Physical Status Classification System is used for assessing
the fitness of patients before surgery.

Reference:
    Mayhew D, Mendonca V, Murthy BVS. A review of ASA physical status – 
    historical perspectives and modern developments. Anaesthesia. 2019;74(3):373-379.
    DOI: 10.1111/anae.14569
    PMID: 30648259

    American Society of Anesthesiologists. ASA Physical Status Classification System.
    https://www.asahq.org/standards-and-guidelines/asa-physical-status-classification-system
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


ASA_CLASS = Literal[1, 2, 3, 4, 5, 6]


class AsaPhysicalStatusCalculator(BaseCalculator):
    """
    ASA Physical Status Classification System
    
    A system for assessing the fitness of patients before surgery.
    Originally developed in 1941 and revised multiple times.
    
    Classes:
        ASA I: A normal healthy patient
        ASA II: A patient with mild systemic disease
        ASA III: A patient with severe systemic disease
        ASA IV: A patient with severe systemic disease that is a constant threat to life
        ASA V: A moribund patient who is not expected to survive without the operation
        ASA VI: A declared brain-dead patient whose organs are being removed for donor purposes
        
    The suffix "E" denotes emergency surgery.
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="asa_physical_status",
                name="ASA Physical Status Classification",
                purpose="Assess preoperative patient fitness and anesthetic risk",
                input_params=["asa_class", "is_emergency"],
                output_type="ASA Classification (I-VI, with optional E suffix)"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ANESTHESIOLOGY,
                    Specialty.SURGERY,
                    Specialty.CRITICAL_CARE,
                    Specialty.EMERGENCY_MEDICINE,
                ),
                conditions=(
                    "Preoperative Assessment",
                    "Surgical Risk",
                    "Anesthetic Risk",
                    "Perioperative Care",
                ),
                clinical_contexts=(
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.PROGNOSIS,
                ),
                clinical_questions=(
                    "What is the patient's surgical risk?",
                    "Is this patient fit for surgery?",
                    "What is the ASA class?",
                    "What is the anesthetic risk?",
                ),
                icd10_codes=(),
                keywords=(
                    "ASA", "physical status", "preoperative", "surgical risk",
                    "anesthetic risk", "fitness for surgery", "perioperative",
                )
            ),
            references=(
                Reference(
                    citation="Mayhew D, Mendonca V, Murthy BVS. A review of ASA physical status – "
                             "historical perspectives and modern developments. Anaesthesia. "
                             "2019;74(3):373-379.",
                    doi="10.1111/anae.14569",
                    pmid="30648259",
                    year=2019
                ),
                Reference(
                    citation="American Society of Anesthesiologists. ASA Physical Status "
                             "Classification System. Last amended October 2019.",
                    url="https://www.asahq.org/standards-and-guidelines/asa-physical-status-classification-system",
                    year=2019
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )
    
    def calculate(
        self,
        asa_class: ASA_CLASS,
        is_emergency: bool = False
    ) -> ScoreResult:
        """
        Classify patient using ASA Physical Status.
        
        Args:
            asa_class: ASA class (1-6)
            is_emergency: Whether this is an emergency procedure
            
        Returns:
            ScoreResult with ASA classification and perioperative mortality risk
        """
        if asa_class not in (1, 2, 3, 4, 5, 6):
            raise ValueError("ASA class must be 1, 2, 3, 4, 5, or 6")
        
        # Get interpretation
        interpretation = self._get_interpretation(asa_class, is_emergency)
        
        # Format display value
        display_value = f"ASA {self._to_roman(asa_class)}"
        if is_emergency:
            display_value += "E"
        
        return ScoreResult(
            value=float(asa_class),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "asa_class": asa_class,
                "is_emergency": is_emergency
            },
            calculation_details={
                "classification": display_value,
                "emergency_suffix": "E" if is_emergency else None
            },
            notes=[
                "The 'E' suffix indicates emergency surgery",
                "Emergency surgery increases perioperative risk",
            ] if is_emergency else []
        )
    
    def _to_roman(self, num: int) -> str:
        """Convert number to Roman numeral"""
        roman = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}
        return roman.get(num, str(num))
    
    def _get_interpretation(self, asa_class: int, is_emergency: bool) -> Interpretation:
        """Get clinical interpretation for ASA class"""
        
        # Approximate perioperative mortality rates
        mortality_rates = {
            1: 0.1,   # ~0.1%
            2: 0.2,   # ~0.2%
            3: 1.8,   # ~1.8%
            4: 7.8,   # ~7.8%
            5: 9.4,   # ~9.4%
            6: 100.0  # Brain dead - organ donor
        }
        
        if asa_class == 1:
            return Interpretation(
                summary="ASA I: Normal healthy patient",
                detail="Healthy, non-smoking, no or minimal alcohol use. "
                       "No significant medical history.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.VERY_LOW,
                stage="ASA I",
                stage_description="Normal healthy patient",
                recommendations=(
                    "Standard preoperative preparation",
                    "No specific anesthetic modifications needed",
                ),
                next_steps=(
                    "Proceed with standard anesthetic plan",
                    "Routine monitoring",
                )
            )
        elif asa_class == 2:
            return Interpretation(
                summary="ASA II: Mild systemic disease",
                detail="Mild diseases only without substantive functional limitations. "
                       "Examples: current smoker, social alcohol drinker, pregnancy, "
                       "obesity (BMI 30-40), well-controlled DM/HTN, mild lung disease.",
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="ASA II",
                stage_description="Patient with mild systemic disease",
                recommendations=(
                    "Optimize chronic conditions preoperatively",
                    "Continue most regular medications",
                    "Standard monitoring usually sufficient",
                ),
                next_steps=(
                    "Review and optimize medications",
                    "Consider regional anesthesia if appropriate",
                )
            )
        elif asa_class == 3:
            return Interpretation(
                summary="ASA III: Severe systemic disease",
                detail="Substantive functional limitations. One or more moderate to severe diseases. "
                       "Examples: poorly controlled DM/HTN, COPD, morbid obesity (BMI ≥40), "
                       "active hepatitis, alcohol dependence, pacemaker, moderate reduction in EF, "
                       "ESRD on dialysis, history of MI/CVA/TIA >3 months.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="ASA III",
                stage_description="Patient with severe systemic disease",
                recommendations=(
                    "Thorough preoperative optimization essential",
                    "Consider cardiology/pulmonology consultation",
                    "Plan for invasive monitoring if indicated",
                    "Postoperative ICU admission may be needed",
                ),
                warnings=(
                    "Increased perioperative morbidity and mortality",
                    "May need additional monitoring",
                ),
                next_steps=(
                    "Optimize all comorbidities",
                    "Order appropriate preoperative testing",
                    "Plan postoperative care level",
                )
            )
        elif asa_class == 4:
            return Interpretation(
                summary="ASA IV: Severe systemic disease that is a constant threat to life",
                detail="Examples: recent MI/CVA/TIA (<3 months), ongoing cardiac ischemia, "
                       "severe valve dysfunction, severe reduction in EF, sepsis, DIC, "
                       "ARDS, ESRD not on dialysis.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage="ASA IV",
                stage_description="Severe systemic disease that is a constant threat to life",
                recommendations=(
                    "Multidisciplinary preoperative planning",
                    "Invasive monitoring likely required",
                    "ICU bed must be secured",
                    "Consider if surgery can be delayed for optimization",
                    "Blood products should be available",
                ),
                warnings=(
                    "High perioperative mortality risk (~8%)",
                    "Life-threatening comorbidities present",
                    "Careful risk-benefit discussion with patient/family",
                ),
                next_steps=(
                    "ICU bed reservation",
                    "Invasive line placement plan",
                    "Informed consent with detailed risk discussion",
                )
            )
        elif asa_class == 5:
            return Interpretation(
                summary="ASA V: Moribund patient not expected to survive without surgery",
                detail="Not expected to survive >24 hours without surgery. "
                       "Examples: ruptured AAA, massive trauma, intracranial bleed with mass effect, "
                       "ischemic bowel with cardiac pathology, multiorgan dysfunction.",
                severity=Severity.CRITICAL,
                risk_level=RiskLevel.VERY_HIGH,
                stage="ASA V",
                stage_description="Moribund patient not expected to survive without the operation",
                recommendations=(
                    "Surgery is life-saving attempt",
                    "Full invasive monitoring",
                    "Blood products immediately available",
                    "Prepare for prolonged ICU stay",
                    "Early family discussion about prognosis",
                ),
                warnings=(
                    "Very high mortality risk regardless of intervention",
                    "Surgery is a last resort life-saving measure",
                    "Goals of care discussion essential",
                ),
                next_steps=(
                    "Emergency surgery preparation",
                    "Massive transfusion protocol availability",
                    "Family communication and support",
                )
            )
        else:  # asa_class == 6
            return Interpretation(
                summary="ASA VI: Brain-dead patient for organ donation",
                detail="Declared brain-dead patient whose organs are being removed for donor purposes.",
                severity=Severity.CRITICAL,
                stage="ASA VI",
                stage_description="Declared brain-dead patient for organ procurement",
                recommendations=(
                    "Coordinate with organ procurement organization",
                    "Maintain physiologic stability for organ viability",
                    "Standard organ procurement protocols",
                ),
                next_steps=(
                    "Follow organ procurement protocols",
                    "Maintain donor hemodynamic stability",
                )
            )
