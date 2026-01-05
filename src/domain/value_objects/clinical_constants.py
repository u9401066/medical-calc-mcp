"""
Clinical Constants

Shared clinical constants and reference values used across multiple calculators.
This ensures consistency and provides a single source of truth.
"""


from typing import Any


# =============================================================================
# Estimated Blood Volume (EBV) by Patient Type
# =============================================================================
# Reference: Cote CJ, Lerman J, Anderson BJ. A Practice of Anesthesia for
#            Infants and Children. 6th ed. Philadelphia: Elsevier; 2019.
#            Miller RD, et al. Miller's Anesthesia. 9th ed. 2020.

EBV_ML_PER_KG: dict[str, int] = {
    "preterm_neonate": 90,      # Premature infant (<37 weeks)
    "term_neonate": 85,         # Full-term newborn (0-28 days)
    "infant": 80,               # 1-12 months
    "child": 75,                # 1-12 years
    "adolescent": 70,           # >12 years
    "adult_male": 70,           # Adult male
    "adult_female": 65,         # Adult female
    "obese_adult": 60,          # Obese adult (use IBW)
    "elderly": 65,              # >65 years
}


# =============================================================================
# Blood Product Specifications
# =============================================================================
# Reference: AABB Technical Manual, 20th Edition
#            Roseff SD, et al. Transfusion 2002

BLOOD_PRODUCTS: dict[str, dict[str, Any]] = {
    "prbc": {
        "name": "Packed Red Blood Cells (PRBC)",
        "hematocrit": 60,  # Typical Hct of PRBC is 55-65%
        "volume_per_unit_ml": 300,
        "expected_hct_rise_per_unit": 3,  # % rise per unit in 70kg adult
    },
    "whole_blood": {
        "name": "Whole Blood",
        "hematocrit": 40,  # Hct of whole blood ~40%
        "volume_per_unit_ml": 450,
        "expected_hct_rise_per_unit": 3,
    },
    "platelets": {
        "name": "Platelets (Apheresis)",
        "platelet_count": 300,  # ×10⁹/L per unit
        "volume_per_unit_ml": 250,
        "expected_plt_rise_per_unit": 30,  # ×10⁹/L rise per unit in 70kg adult
    },
    "platelet_concentrate": {
        "name": "Platelet Concentrate (Random Donor)",
        "platelet_count": 60,  # ×10⁹/L per unit (pooled = 4-6 units)
        "volume_per_unit_ml": 50,
        "expected_plt_rise_per_unit": 5,  # per single unit
    },
    "ffp": {
        "name": "Fresh Frozen Plasma (FFP)",
        "volume_per_unit_ml": 250,
        "dose_ml_per_kg": 15,  # 10-15 mL/kg typical dose
    },
    "cryoprecipitate": {
        "name": "Cryoprecipitate",
        "volume_per_unit_ml": 15,
        "fibrinogen_per_unit_mg": 250,  # ~250 mg fibrinogen per unit
        "dose_units_per_10kg": 1,  # 1 unit per 10 kg body weight
    },
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_ebv_per_kg(patient_type: str, default: int = 70) -> int:
    """
    Get estimated blood volume per kg for a patient type.

    Args:
        patient_type: Patient category (e.g., 'adult_male', 'infant')
        default: Default value if patient type not found

    Returns:
        EBV in mL/kg
    """
    normalized = patient_type.lower().replace(" ", "_").replace("-", "_")
    return EBV_ML_PER_KG.get(normalized, default)


def get_blood_product(product_type: str) -> dict[str, Any]:
    """
    Get blood product specifications.

    Args:
        product_type: Product type (e.g., 'prbc', 'ffp')

    Returns:
        Product specifications dictionary

    Raises:
        ValueError: If product type not found
    """
    normalized = product_type.lower()
    if normalized not in BLOOD_PRODUCTS:
        available = ", ".join(BLOOD_PRODUCTS.keys())
        raise ValueError(f"Unknown product: {product_type}. Available: {available}")
    return BLOOD_PRODUCTS[normalized]
