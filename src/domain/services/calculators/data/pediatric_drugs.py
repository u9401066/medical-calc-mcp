"""
Pediatric Drug Database

Reference drug dosing information for common pediatric medications.
Used by the PediatricDosingCalculator.

References:
    Taketomo CK, Hodding JH, Kraus DM. Pediatric & Neonatal Dosage Handbook. 
    29th ed. Hudson, OH: Lexicomp; 2022.
    
    Neofax: A Manual of Drugs Used in Neonatal Care. 24th ed. 
    Montvale, NJ: Thomson Reuters; 2011.

    British National Formulary for Children (BNFC). London: BMJ Group and 
    Pharmaceutical Press; 2023.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class PediatricDrugInfo:
    """
    Information for a pediatric drug.
    
    Attributes:
        name: Full drug name with common alternatives
        dose_per_kg: Standard dose in mg/kg
        max_single_dose: Maximum single dose in mg
        frequency: Dosing frequency (e.g., "q8h", "single dose")
        route: Route of administration (e.g., "PO", "IV", "IM")
        notes: Additional clinical notes and warnings
    """
    name: str
    dose_per_kg: float  # mg/kg
    max_single_dose: float  # mg
    frequency: str
    route: str
    notes: str = ""


# =============================================================================
# Pediatric Drug Database
# =============================================================================

PEDIATRIC_DRUGS: Dict[str, PediatricDrugInfo] = {
    # =========================================================================
    # Analgesics / Antipyretics
    # =========================================================================
    "acetaminophen": PediatricDrugInfo(
        name="Acetaminophen (Paracetamol)",
        dose_per_kg=15.0,
        max_single_dose=1000.0,
        frequency="q4-6h",
        route="PO/PR",
        notes="Max 75 mg/kg/day or 4000 mg/day"
    ),
    "ibuprofen": PediatricDrugInfo(
        name="Ibuprofen",
        dose_per_kg=10.0,
        max_single_dose=400.0,
        frequency="q6-8h",
        route="PO",
        notes="Max 40 mg/kg/day or 2400 mg/day. Avoid in infants <6 months"
    ),
    
    # =========================================================================
    # Antibiotics
    # =========================================================================
    "amoxicillin": PediatricDrugInfo(
        name="Amoxicillin",
        dose_per_kg=25.0,
        max_single_dose=500.0,
        frequency="q8h",
        route="PO",
        notes="High dose: 40-50 mg/kg/dose for resistant organisms"
    ),
    "amoxicillin_clavulanate": PediatricDrugInfo(
        name="Amoxicillin-Clavulanate (Augmentin)",
        dose_per_kg=25.0,
        max_single_dose=500.0,
        frequency="q8h",
        route="PO",
        notes="Based on amoxicillin component"
    ),
    "azithromycin": PediatricDrugInfo(
        name="Azithromycin",
        dose_per_kg=10.0,
        max_single_dose=500.0,
        frequency="q24h",
        route="PO",
        notes="Day 1: 10 mg/kg, Days 2-5: 5 mg/kg"
    ),
    "ceftriaxone": PediatricDrugInfo(
        name="Ceftriaxone",
        dose_per_kg=50.0,
        max_single_dose=2000.0,
        frequency="q24h",
        route="IV/IM",
        notes="Meningitis: 100 mg/kg/day divided q12h"
    ),
    "cefazolin": PediatricDrugInfo(
        name="Cefazolin",
        dose_per_kg=25.0,
        max_single_dose=1000.0,
        frequency="q8h",
        route="IV",
        notes="Surgical prophylaxis: 30 mg/kg, max 2g"
    ),
    
    # =========================================================================
    # Anesthesia Induction Agents
    # =========================================================================
    "propofol": PediatricDrugInfo(
        name="Propofol (Induction)",
        dose_per_kg=2.5,
        max_single_dose=200.0,
        frequency="single dose",
        route="IV",
        notes="Induction: 2-3 mg/kg. Infants may need higher doses (3-4 mg/kg)"
    ),
    "ketamine": PediatricDrugInfo(
        name="Ketamine (IV)",
        dose_per_kg=1.5,
        max_single_dose=100.0,
        frequency="single dose",
        route="IV",
        notes="IV: 1-2 mg/kg, IM: 4-6 mg/kg"
    ),
    
    # =========================================================================
    # Opioids
    # =========================================================================
    "fentanyl": PediatricDrugInfo(
        name="Fentanyl",
        dose_per_kg=0.001,  # 1 mcg/kg
        max_single_dose=0.1,  # 100 mcg
        frequency="prn",
        route="IV",
        notes="1-2 mcg/kg for analgesia; dose in mcg not mg"
    ),
    "morphine": PediatricDrugInfo(
        name="Morphine",
        dose_per_kg=0.1,
        max_single_dose=10.0,
        frequency="q4h prn",
        route="IV",
        notes="0.05-0.1 mg/kg IV; 0.2-0.5 mg/kg PO"
    ),
    
    # =========================================================================
    # Neuromuscular Blocking Agents
    # =========================================================================
    "rocuronium": PediatricDrugInfo(
        name="Rocuronium",
        dose_per_kg=0.6,
        max_single_dose=50.0,
        frequency="single dose",
        route="IV",
        notes="RSI: 1.2 mg/kg; Maintenance: 0.1-0.2 mg/kg"
    ),
    "succinylcholine": PediatricDrugInfo(
        name="Succinylcholine",
        dose_per_kg=2.0,
        max_single_dose=150.0,
        frequency="single dose",
        route="IV",
        notes="Infants: 2-3 mg/kg; Children: 1-2 mg/kg. Contraindicated in hyperkalemia risk"
    ),
    
    # =========================================================================
    # Anticholinergics
    # =========================================================================
    "atropine": PediatricDrugInfo(
        name="Atropine",
        dose_per_kg=0.02,
        max_single_dose=0.5,
        frequency="single dose",
        route="IV",
        notes="Minimum dose: 0.1 mg; Max: 0.5 mg (child), 1 mg (adolescent)"
    ),
    "glycopyrrolate": PediatricDrugInfo(
        name="Glycopyrrolate",
        dose_per_kg=0.01,
        max_single_dose=0.2,
        frequency="single dose",
        route="IV",
        notes="Antisialagogue: 0.004-0.01 mg/kg"
    ),
    
    # =========================================================================
    # Antiemetics
    # =========================================================================
    "ondansetron": PediatricDrugInfo(
        name="Ondansetron",
        dose_per_kg=0.15,
        max_single_dose=4.0,
        frequency="q8h",
        route="IV/PO",
        notes="PONV prophylaxis: 0.1-0.15 mg/kg"
    ),
    "dexamethasone": PediatricDrugInfo(
        name="Dexamethasone (PONV)",
        dose_per_kg=0.15,
        max_single_dose=8.0,
        frequency="single dose",
        route="IV",
        notes="PONV: 0.1-0.15 mg/kg; Croup: 0.6 mg/kg"
    ),
    
    # =========================================================================
    # Emergency / Resuscitation Drugs
    # =========================================================================
    "epinephrine": PediatricDrugInfo(
        name="Epinephrine (Cardiac Arrest)",
        dose_per_kg=0.01,
        max_single_dose=1.0,
        frequency="q3-5min",
        route="IV/IO",
        notes="0.01 mg/kg (0.1 mL/kg of 1:10,000); Max 1 mg. ETT: 0.1 mg/kg"
    ),
    "adenosine": PediatricDrugInfo(
        name="Adenosine",
        dose_per_kg=0.1,
        max_single_dose=6.0,
        frequency="prn",
        route="IV rapid push",
        notes="1st dose: 0.1 mg/kg (max 6 mg); 2nd dose: 0.2 mg/kg (max 12 mg)"
    ),
    "amiodarone": PediatricDrugInfo(
        name="Amiodarone",
        dose_per_kg=5.0,
        max_single_dose=300.0,
        frequency="prn",
        route="IV",
        notes="VF/pVT: 5 mg/kg; May repeat x2"
    ),
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_drug_info(drug_name: str) -> PediatricDrugInfo:
    """
    Get drug information by name.
    
    Args:
        drug_name: Drug name (case-insensitive)
        
    Returns:
        PediatricDrugInfo for the drug
        
    Raises:
        KeyError: If drug not found
    """
    normalized = drug_name.lower().replace(" ", "_").replace("-", "_")
    if normalized not in PEDIATRIC_DRUGS:
        raise KeyError(f"Drug '{drug_name}' not found. Use list_available_drugs()")
    return PEDIATRIC_DRUGS[normalized]


def list_available_drugs() -> list[str]:
    """Return list of available drug names in database"""
    return sorted(PEDIATRIC_DRUGS.keys())


def list_drugs_by_category() -> dict[str, list[str]]:
    """Return drugs grouped by category"""
    return {
        "analgesics_antipyretics": ["acetaminophen", "ibuprofen"],
        "antibiotics": ["amoxicillin", "amoxicillin_clavulanate", "azithromycin", 
                        "ceftriaxone", "cefazolin"],
        "anesthesia_induction": ["propofol", "ketamine"],
        "opioids": ["fentanyl", "morphine"],
        "neuromuscular_blockers": ["rocuronium", "succinylcholine"],
        "anticholinergics": ["atropine", "glycopyrrolate"],
        "antiemetics": ["ondansetron", "dexamethasone"],
        "emergency": ["epinephrine", "adenosine", "amiodarone"],
    }
