"""
Medical Calculators

Domain services implementing clinical calculators.
Each calculator inherits from BaseCalculator and provides:
- Metadata for tool discovery (LowLevelKey + HighLevelKey)
- References to original papers (Vancouver citation format)
- Calculate method returning ScoreResult
"""

from .ckd_epi_2021 import CkdEpi2021Calculator
from .asa_physical_status import AsaPhysicalStatusCalculator
from .mallampati_score import MallampatiScoreCalculator
from .rcri import RcriCalculator
from .apache_ii import ApacheIiCalculator
from .rass import RassCalculator

# Phase 4: ICU/Emergency Calculators
from .sofa_score import SofaScoreCalculator
from .qsofa_score import QsofaScoreCalculator
from .news_score import NewsScoreCalculator
from .gcs import GlasgowComaScaleCalculator
from .cam_icu import CamIcuCalculator

# Phase 5: Pediatric & Anesthesia Calculators
from .pediatric_dosing import PediatricDosingCalculator
from .mabl import MablCalculator
from .transfusion_calc import TransfusionCalculator

# Phase 6: Pulmonology
from .curb65 import Curb65Calculator

# Phase 6: Cardiology
from .chads2_vasc import Chads2VascCalculator
from .heart_score import HeartScoreCalculator

# Phase 6: Emergency Medicine
from .wells_dvt import WellsDvtCalculator
from .wells_pe import WellsPeCalculator

# Phase 6: Hepatology
from .meld_score import MeldScoreCalculator


__all__ = [
    # Nephrology
    "CkdEpi2021Calculator",
    
    # Anesthesiology / Preoperative
    "AsaPhysicalStatusCalculator",
    "MallampatiScoreCalculator",
    "RcriCalculator",
    
    # Critical Care / ICU
    "ApacheIiCalculator",
    "RassCalculator",
    "SofaScoreCalculator",
    "QsofaScoreCalculator",
    "NewsScoreCalculator",
    "GlasgowComaScaleCalculator",
    "CamIcuCalculator",
    
    # Pediatric & Anesthesia
    "PediatricDosingCalculator",
    "MablCalculator",
    "TransfusionCalculator",
    
    # Pulmonology
    "Curb65Calculator",
    
    # Cardiology
    "Chads2VascCalculator",
    "HeartScoreCalculator",
    
    # Emergency Medicine
    "WellsDvtCalculator",
    "WellsPeCalculator",
    
    # Hepatology
    "MeldScoreCalculator",
]


# Calculator registry for easy iteration
CALCULATORS = [
    CkdEpi2021Calculator,
    AsaPhysicalStatusCalculator,
    MallampatiScoreCalculator,
    RcriCalculator,
    ApacheIiCalculator,
    RassCalculator,
    # Phase 4: ICU/Emergency
    SofaScoreCalculator,
    QsofaScoreCalculator,
    NewsScoreCalculator,
    GlasgowComaScaleCalculator,
    CamIcuCalculator,
    # Phase 5: Pediatric & Anesthesia
    PediatricDosingCalculator,
    MablCalculator,
    TransfusionCalculator,
    # Phase 6: Pulmonology
    Curb65Calculator,
    # Phase 6: Cardiology
    Chads2VascCalculator,
    HeartScoreCalculator,
    # Phase 6: Emergency Medicine
    WellsDvtCalculator,
    WellsPeCalculator,
    # Phase 6: Hepatology
    MeldScoreCalculator,
]
