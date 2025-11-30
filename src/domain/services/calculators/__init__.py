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
]
