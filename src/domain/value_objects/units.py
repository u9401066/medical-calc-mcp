"""
Medical Units Value Objects

Defines standard units used in medical calculations.
"""

from enum import Enum


class Unit(Enum):
    """Standard medical measurement units"""
    
    # Renal
    ML_MIN_1_73M2 = "mL/min/1.73m²"  # GFR
    ML_MIN = "mL/min"  # Creatinine clearance
    MG_DL = "mg/dL"  # Creatinine, BUN
    UMOL_L = "µmol/L"  # Creatinine (SI)
    
    # General
    PERCENT = "%"
    SCORE = "points"
    RATIO = "ratio"
    
    # Cardiovascular
    PERCENT_PER_YEAR = "%/year"  # Annual risk
    MMHG = "mmHg"  # Blood pressure
    BPM = "bpm"  # Heart rate
    
    # Pulmonary
    L = "L"  # Volume
    L_MIN = "L/min"  # Flow
    MM = "mm"  # e.g., tracheal diameter
    
    # Volume (for transfusion, MABL)
    ML = "mL"  # Milliliters
    
    # Mass (for drug dosing)
    MG = "mg"  # Milligrams
    MG_DOSE = "mg/dose"  # Milligrams per dose
    MG_KG = "mg/kg"  # Dose per kg
    
    # Laboratory
    MEQ_L = "mEq/L"  # Electrolytes
    MMOL_L = "mmol/L"  # Glucose, etc.
    G_DL = "g/dL"  # Hemoglobin
    CELLS_UL = "cells/µL"  # Cell counts
    
    # Time
    DAYS = "days"
    MONTHS = "months"
    YEARS = "years"
    
    # Temperature
    CELSIUS = "°C"
    FAHRENHEIT = "°F"
    
    # Other
    KG = "kg"
    KG_M2 = "kg/m²"  # BMI
    CM = "cm"
    M = "m"
    
    # Dimensionless
    NONE = ""
    
    # Boolean/Binary
    BINARY = "present/absent"  # For yes/no results (e.g., delirium present)
    
    def __str__(self) -> str:
        return self.value
