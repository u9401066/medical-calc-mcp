"""
Calculator Data Modules

This package contains reference data used by calculators:
- pediatric_drugs.py: Pediatric drug dosing database
"""

from .pediatric_drugs import (
    PEDIATRIC_DRUGS,
    PediatricDrugInfo,
    get_drug_info,
    list_available_drugs,
    list_drugs_by_category,
)

__all__ = [
    "PediatricDrugInfo",
    "PEDIATRIC_DRUGS",
    "get_drug_info",
    "list_available_drugs",
    "list_drugs_by_category",
]
