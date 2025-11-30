"""
Taxonomy Definitions

Defines the taxonomy used for tool classification and discovery.
"""

from typing import Dict, List, Set

from ..value_objects.tool_keys import Specialty, ClinicalContext


# Specialty groupings for easier discovery
SPECIALTY_GROUPS: Dict[str, List[Specialty]] = {
    "internal_medicine": [
        Specialty.INTERNAL_MEDICINE,
        Specialty.CARDIOLOGY,
        Specialty.NEPHROLOGY,
        Specialty.PULMONOLOGY,
        Specialty.GASTROENTEROLOGY,
        Specialty.HEPATOLOGY,
        Specialty.ENDOCRINOLOGY,
        Specialty.RHEUMATOLOGY,
        Specialty.INFECTIOUS_DISEASE,
        Specialty.HEMATOLOGY,
    ],
    "critical_care": [
        Specialty.CRITICAL_CARE,
        Specialty.EMERGENCY_MEDICINE,
    ],
    "surgical": [
        Specialty.SURGERY,
        Specialty.ORTHOPEDICS,
    ],
    "other": [
        Specialty.ONCOLOGY,
        Specialty.NEUROLOGY,
        Specialty.PSYCHIATRY,
        Specialty.PEDIATRICS,
        Specialty.OBSTETRICS,
        Specialty.GERIATRICS,
        Specialty.TOXICOLOGY,
    ],
}


# Related specialties for cross-referencing
RELATED_SPECIALTIES: Dict[Specialty, Set[Specialty]] = {
    Specialty.NEPHROLOGY: {Specialty.INTERNAL_MEDICINE, Specialty.CRITICAL_CARE},
    Specialty.CARDIOLOGY: {Specialty.INTERNAL_MEDICINE, Specialty.CRITICAL_CARE, Specialty.SURGERY},
    Specialty.PULMONOLOGY: {Specialty.INTERNAL_MEDICINE, Specialty.CRITICAL_CARE},
    Specialty.HEPATOLOGY: {Specialty.GASTROENTEROLOGY, Specialty.INTERNAL_MEDICINE},
    Specialty.CRITICAL_CARE: {Specialty.EMERGENCY_MEDICINE, Specialty.INTERNAL_MEDICINE},
    Specialty.EMERGENCY_MEDICINE: {Specialty.CRITICAL_CARE, Specialty.INTERNAL_MEDICINE},
}


# Clinical context descriptions
CONTEXT_DESCRIPTIONS: Dict[ClinicalContext, str] = {
    ClinicalContext.DIAGNOSIS: "Tools that help establish or confirm a diagnosis",
    ClinicalContext.SCREENING: "Tools for population or individual screening",
    ClinicalContext.STAGING: "Tools that classify disease severity or stage",
    ClinicalContext.PROGNOSIS: "Tools that predict clinical outcomes",
    ClinicalContext.RISK_STRATIFICATION: "Tools that assess and stratify risk levels",
    ClinicalContext.DRUG_DOSING: "Tools for medication dosing calculations",
    ClinicalContext.TREATMENT_DECISION: "Tools that guide treatment choices",
    ClinicalContext.MONITORING: "Tools for disease monitoring and follow-up",
    ClinicalContext.SEVERITY_ASSESSMENT: "Tools that assess current severity",
    ClinicalContext.DISPOSITION: "Tools that guide admission/discharge decisions",
    ClinicalContext.ELIGIBILITY: "Tools that assess eligibility for trials/treatments",
    ClinicalContext.PHYSIOLOGIC: "Tools for normal physiologic calculations",
}


def get_specialty_display_name(specialty: Specialty) -> str:
    """Get human-readable display name for specialty"""
    return specialty.value.replace("_", " ").title()


def get_context_display_name(context: ClinicalContext) -> str:
    """Get human-readable display name for clinical context"""
    return context.value.replace("_", " ").title()
