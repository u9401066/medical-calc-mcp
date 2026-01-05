"""
Taxonomy Definitions

Defines the taxonomy used for tool classification and discovery.
"""


from ..value_objects.tool_keys import ClinicalContext, Specialty

# Specialty groupings for easier discovery
SPECIALTY_GROUPS: dict[str, list[Specialty]] = {
    "anesthesia_critical_care": [
        Specialty.ANESTHESIOLOGY,
        Specialty.CRITICAL_CARE,
        Specialty.EMERGENCY_MEDICINE,
        Specialty.PAIN_MEDICINE,
        Specialty.CARDIAC_ANESTHESIA,
        Specialty.NEUROANESTHESIA,
        Specialty.PEDIATRIC_ANESTHESIA,
        Specialty.OBSTETRIC_ANESTHESIA,
        Specialty.REGIONAL_ANESTHESIA,
    ],
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
RELATED_SPECIALTIES: dict[Specialty, set[Specialty]] = {
    # Anesthesia connections
    Specialty.ANESTHESIOLOGY: {
        Specialty.CRITICAL_CARE,
        Specialty.SURGERY,
        Specialty.PAIN_MEDICINE,
        Specialty.EMERGENCY_MEDICINE
    },
    Specialty.CRITICAL_CARE: {
        Specialty.ANESTHESIOLOGY,
        Specialty.EMERGENCY_MEDICINE,
        Specialty.INTERNAL_MEDICINE,
        Specialty.PULMONOLOGY
    },
    Specialty.PAIN_MEDICINE: {
        Specialty.ANESTHESIOLOGY,
        Specialty.NEUROLOGY,
        Specialty.RHEUMATOLOGY,
        Specialty.REGIONAL_ANESTHESIA
    },
    Specialty.CARDIAC_ANESTHESIA: {
        Specialty.ANESTHESIOLOGY,
        Specialty.CARDIOLOGY,
        Specialty.SURGERY
    },

    # Internal medicine connections
    Specialty.NEPHROLOGY: {Specialty.INTERNAL_MEDICINE, Specialty.CRITICAL_CARE},
    Specialty.CARDIOLOGY: {Specialty.INTERNAL_MEDICINE, Specialty.CRITICAL_CARE, Specialty.SURGERY},
    Specialty.PULMONOLOGY: {Specialty.INTERNAL_MEDICINE, Specialty.CRITICAL_CARE, Specialty.ANESTHESIOLOGY},
    Specialty.HEPATOLOGY: {Specialty.GASTROENTEROLOGY, Specialty.INTERNAL_MEDICINE},
    Specialty.EMERGENCY_MEDICINE: {Specialty.CRITICAL_CARE, Specialty.INTERNAL_MEDICINE, Specialty.ANESTHESIOLOGY},
}


# Clinical context descriptions
CONTEXT_DESCRIPTIONS: dict[ClinicalContext, str] = {
    # General
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

    # Anesthesia / ICU specific
    ClinicalContext.PREOPERATIVE_ASSESSMENT: "Tools for preoperative risk assessment (ASA, RCRI, etc.)",
    ClinicalContext.AIRWAY_MANAGEMENT: "Tools for airway assessment and management (Mallampati, etc.)",
    ClinicalContext.VENTILATOR_MANAGEMENT: "Tools for ventilator settings and weaning",
    ClinicalContext.FLUID_MANAGEMENT: "Tools for fluid and electrolyte management",
    ClinicalContext.HEMODYNAMIC_MONITORING: "Tools for hemodynamic assessment and monitoring",
    ClinicalContext.SEDATION_ASSESSMENT: "Tools for sedation level assessment (RASS, SAS, etc.)",
    ClinicalContext.PAIN_ASSESSMENT: "Tools for pain assessment (NRS, CPOT, BPS, etc.)",
    ClinicalContext.NEUROMUSCULAR_MONITORING: "Tools for neuromuscular blockade assessment",
    ClinicalContext.TRANSFUSION_DECISION: "Tools for transfusion threshold and decision",
    ClinicalContext.WEANING_ASSESSMENT: "Tools for ventilator weaning readiness (RSBI, etc.)",
    ClinicalContext.DELIRIUM_ASSESSMENT: "Tools for ICU delirium screening (CAM-ICU, etc.)",
    ClinicalContext.NUTRITION_ASSESSMENT: "Tools for nutritional assessment in critical illness",
}


def get_specialty_display_name(specialty: Specialty) -> str:
    """Get human-readable display name for specialty"""
    return specialty.value.replace("_", " ").title()


def get_context_display_name(context: ClinicalContext) -> str:
    """Get human-readable display name for clinical context"""
    return context.value.replace("_", " ").title()
