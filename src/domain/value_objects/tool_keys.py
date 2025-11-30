"""
Tool Keys Value Objects

Defines Low Level and High Level Keys for Tool Discovery.

- LowLevelKey: For precise tool selection by AI agents
- HighLevelKey: For exploration and discovery based on clinical context
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class Specialty(Enum):
    """Medical specialties"""
    
    # Primary specialties
    ANESTHESIOLOGY = "anesthesiology"  # 麻醉科
    CARDIOLOGY = "cardiology"
    CRITICAL_CARE = "critical_care"  # ICU
    EMERGENCY_MEDICINE = "emergency_medicine"
    ENDOCRINOLOGY = "endocrinology"
    GASTROENTEROLOGY = "gastroenterology"
    GERIATRICS = "geriatrics"
    HEMATOLOGY = "hematology"
    HEPATOLOGY = "hepatology"
    INFECTIOUS_DISEASE = "infectious_disease"
    INTERNAL_MEDICINE = "internal_medicine"
    NEPHROLOGY = "nephrology"
    NEUROLOGY = "neurology"
    OBSTETRICS = "obstetrics"
    ONCOLOGY = "oncology"
    ORTHOPEDICS = "orthopedics"
    PEDIATRICS = "pediatrics"
    PSYCHIATRY = "psychiatry"
    PULMONOLOGY = "pulmonology"
    RHEUMATOLOGY = "rheumatology"
    SURGERY = "surgery"
    TOXICOLOGY = "toxicology"
    
    # Subspecialties
    PAIN_MEDICINE = "pain_medicine"  # 疼痛醫學
    CARDIAC_ANESTHESIA = "cardiac_anesthesia"  # 心臟麻醉
    NEUROANESTHESIA = "neuroanesthesia"  # 神經麻醉
    PEDIATRIC_ANESTHESIA = "pediatric_anesthesia"  # 小兒麻醉
    OBSTETRIC_ANESTHESIA = "obstetric_anesthesia"  # 產科麻醉
    REGIONAL_ANESTHESIA = "regional_anesthesia"  # 區域麻醉
    
    OTHER = "other"


class ClinicalContext(Enum):
    """Clinical use contexts for calculators"""
    
    # General
    DIAGNOSIS = "diagnosis"  # Helps establish a diagnosis
    SCREENING = "screening"  # Population screening
    STAGING = "staging"  # Disease staging/classification
    PROGNOSIS = "prognosis"  # Predict outcomes
    RISK_STRATIFICATION = "risk_stratification"  # Assess risk levels
    DRUG_DOSING = "drug_dosing"  # Medication dosing
    TREATMENT_DECISION = "treatment_decision"  # Guide treatment choices
    MONITORING = "monitoring"  # Disease monitoring
    SEVERITY_ASSESSMENT = "severity_assessment"  # Assess severity
    DISPOSITION = "disposition"  # Admission/discharge decisions
    ELIGIBILITY = "eligibility"  # Trial/treatment eligibility
    PHYSIOLOGIC = "physiologic"  # Normal physiology calculations
    
    # Anesthesia / ICU specific
    PREOPERATIVE_ASSESSMENT = "preoperative_assessment"  # 術前評估
    AIRWAY_MANAGEMENT = "airway_management"  # 氣道管理
    VENTILATOR_MANAGEMENT = "ventilator_management"  # 呼吸器設定
    FLUID_MANAGEMENT = "fluid_management"  # 輸液管理
    HEMODYNAMIC_MONITORING = "hemodynamic_monitoring"  # 血流動力學監測
    SEDATION_ASSESSMENT = "sedation_assessment"  # 鎮靜評估
    PAIN_ASSESSMENT = "pain_assessment"  # 疼痛評估
    NEUROMUSCULAR_MONITORING = "neuromuscular_monitoring"  # 神經肌肉監測
    TRANSFUSION_DECISION = "transfusion_decision"  # 輸血決策
    WEANING_ASSESSMENT = "weaning_assessment"  # 脫機評估
    DELIRIUM_ASSESSMENT = "delirium_assessment"  # 譫妄評估
    NUTRITION_ASSESSMENT = "nutrition_assessment"  # 營養評估


@dataclass(frozen=True)
class LowLevelKey:
    """
    Low Level Key for precise tool identification.
    
    Used by AI agents for exact tool selection when they know
    which specific calculator they need.
    
    Attributes:
        tool_id: Unique identifier (e.g., "ckd_epi_2021")
        name: Human-readable name (e.g., "CKD-EPI 2021")
        purpose: What it calculates (e.g., "Calculate estimated GFR")
        input_params: List of required parameters
        output_type: Description of the result
    """
    
    tool_id: str
    name: str
    purpose: str
    input_params: List[str]
    output_type: str
    
    def __post_init__(self):
        if not self.tool_id:
            raise ValueError("tool_id is required")
        if not self.name:
            raise ValueError("name is required")
    
    def to_dict(self) -> dict:
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "purpose": self.purpose,
            "input_params": self.input_params,
            "output_type": self.output_type
        }


@dataclass(frozen=True)
class HighLevelKey:
    """
    High Level Key for tool exploration and discovery.
    
    Used by AI agents to find relevant tools based on:
    - Medical specialty
    - Clinical conditions/diseases
    - Use context (diagnosis, prognosis, etc.)
    - Natural language clinical questions
    - ICD-10 codes
    - Keywords
    
    This enables intelligent tool discovery when the agent
    doesn't know exactly which calculator to use.
    """
    
    specialties: tuple[Specialty, ...] = field(default_factory=tuple)
    conditions: tuple[str, ...] = field(default_factory=tuple)
    clinical_contexts: tuple[ClinicalContext, ...] = field(default_factory=tuple)
    clinical_questions: tuple[str, ...] = field(default_factory=tuple)
    icd10_codes: tuple[str, ...] = field(default_factory=tuple)
    keywords: tuple[str, ...] = field(default_factory=tuple)
    
    def to_dict(self) -> dict:
        return {
            "specialties": [s.value for s in self.specialties],
            "conditions": list(self.conditions),
            "clinical_contexts": [c.value for c in self.clinical_contexts],
            "clinical_questions": list(self.clinical_questions),
            "icd10_codes": list(self.icd10_codes),
            "keywords": list(self.keywords)
        }
    
    def matches_specialty(self, specialty: Specialty) -> bool:
        """Check if this tool matches a specialty"""
        return specialty in self.specialties
    
    def matches_condition(self, condition: str) -> bool:
        """Check if this tool matches a condition (case-insensitive)"""
        condition_lower = condition.lower()
        return any(c.lower() == condition_lower for c in self.conditions)
    
    def matches_context(self, context: ClinicalContext) -> bool:
        """Check if this tool matches a clinical context"""
        return context in self.clinical_contexts
    
    def matches_keyword(self, keyword: str) -> bool:
        """Check if this tool matches a keyword (case-insensitive)"""
        keyword_lower = keyword.lower()
        return any(k.lower() == keyword_lower for k in self.keywords)
