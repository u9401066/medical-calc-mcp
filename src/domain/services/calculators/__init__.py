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
from .sofa2_score import Sofa2ScoreCalculator  # SOFA-2 (JAMA 2025)
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
from .chads2_va import Chads2VaCalculator  # 2024 ESC - sex-neutral
from .heart_score import HeartScoreCalculator
from .has_bled import HasBledCalculator  # Phase 8: 2024 ESC recommended

# Phase 6: Emergency Medicine
from .wells_dvt import WellsDvtCalculator
from .wells_pe import WellsPeCalculator

# Phase 6: Hepatology
from .meld_score import MeldScoreCalculator

# Phase 7: Surgery/Perioperative & Pulmonology
from .caprini_vte import CapriniVteCalculator
from .psi_port import PsiPortCalculator

# Phase 8: Guideline-Recommended Tools
from .child_pugh import ChildPughCalculator
from .kdigo_aki import KdigoAkiCalculator

# Phase 9: Acid-Base & Electrolytes
from .anion_gap import AnionGapCalculator
from .delta_ratio import DeltaRatioCalculator
from .corrected_sodium import CorrectedSodiumCalculator

# Phase 9b: Additional Acid-Base Calculators
from .winters_formula import WintersFormulaCalculator
from .osmolar_gap import OsmolarGapCalculator
from .free_water_deficit import FreeWaterDeficitCalculator

# Phase 10: High-Priority Tools
from .corrected_qt import CorrectedQtCalculator
from .aa_gradient import AaGradientCalculator
from .shock_index import ShockIndexCalculator

# Phase 11: Upcoming Calculators (All Completed)
from .ideal_body_weight import IdealBodyWeightCalculator
from .pf_ratio import PfRatioCalculator
from .rox_index import RoxIndexCalculator
from .grace_score import GraceScoreCalculator
from .four_ts_hit import FourTsHitCalculator
from .acef_ii_score import AcefIiScoreCalculator

# Phase 12: Additional Anesthesiology Tools
from .apfel_ponv import ApfelPonvCalculator
from .stop_bang import StopBangCalculator
from .aldrete_score import AldreteScoreCalculator

# Phase 12: Neurology
from .nihss import NihssCalculator
from .abcd2 import Abcd2Calculator
from .modified_rankin_scale import ModifiedRankinScaleCalculator

# Phase 13: Additional Scores
from .timi_stemi import TimiStemiCalculator
from .rockall_score import RockallScoreCalculator
from .fib4_index import Fib4IndexCalculator


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
    "Sofa2ScoreCalculator",  # SOFA-2 (JAMA 2025)
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
    "Chads2VaCalculator",  # 2024 ESC
    "HeartScoreCalculator",
    "HasBledCalculator",  # 2024 ESC recommended
    
    # Emergency Medicine
    "WellsDvtCalculator",
    "WellsPeCalculator",
    
    # Hepatology
    "MeldScoreCalculator",
    "ChildPughCalculator",  # Phase 8
    
    # Nephrology (additional)
    "KdigoAkiCalculator",  # Phase 8
    
    # Surgery/Perioperative
    "CapriniVteCalculator",
    
    # Pulmonology (additional)
    "PsiPortCalculator",
    
    # Phase 9: Acid-Base & Electrolytes
    "AnionGapCalculator",
    "DeltaRatioCalculator",
    "CorrectedSodiumCalculator",
    
    # Phase 9b: Additional Acid-Base Calculators
    "WintersFormulaCalculator",
    "OsmolarGapCalculator",
    "FreeWaterDeficitCalculator",
    
    # Phase 10: High-Priority Tools
    "CorrectedQtCalculator",
    "AaGradientCalculator",
    "ShockIndexCalculator",
    
    # Phase 11: Upcoming Calculators (All Completed)
    "IdealBodyWeightCalculator",
    "PfRatioCalculator",
    "RoxIndexCalculator",
    "GraceScoreCalculator",
    "FourTsHitCalculator",
    "AcefIiScoreCalculator",
    
    # Phase 12: Additional Anesthesiology Tools
    "ApfelPonvCalculator",
    "StopBangCalculator",
    "AldreteScoreCalculator",
    
    # Phase 12: Neurology
    "NihssCalculator",
    "Abcd2Calculator",
    "ModifiedRankinScaleCalculator",
    
    # Phase 13: Additional Scores
    "TimiStemiCalculator",
    "RockallScoreCalculator",
    "Fib4IndexCalculator",
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
    Sofa2ScoreCalculator,  # SOFA-2 (JAMA 2025)
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
    Chads2VaCalculator,  # 2024 ESC
    HeartScoreCalculator,
    HasBledCalculator,  # Phase 8: 2024 ESC recommended
    # Phase 6: Emergency Medicine
    WellsDvtCalculator,
    WellsPeCalculator,
    # Phase 6: Hepatology
    MeldScoreCalculator,
    # Phase 7: Surgery/Perioperative & Pulmonology
    CapriniVteCalculator,
    PsiPortCalculator,
    # Phase 8: Guideline-Recommended Tools
    ChildPughCalculator,
    KdigoAkiCalculator,
    # Phase 9: Acid-Base & Electrolytes
    AnionGapCalculator,
    DeltaRatioCalculator,
    CorrectedSodiumCalculator,
    # Phase 9b: Additional Acid-Base Calculators
    WintersFormulaCalculator,
    OsmolarGapCalculator,
    FreeWaterDeficitCalculator,
    # Phase 10: High-Priority Tools
    CorrectedQtCalculator,
    AaGradientCalculator,
    ShockIndexCalculator,
    # Phase 11: Upcoming Calculators (All Completed)
    IdealBodyWeightCalculator,
    PfRatioCalculator,
    RoxIndexCalculator,
    GraceScoreCalculator,
    FourTsHitCalculator,
    AcefIiScoreCalculator,
    # Phase 12: Additional Anesthesiology Tools
    ApfelPonvCalculator,
    StopBangCalculator,
    AldreteScoreCalculator,
    # Phase 12: Neurology
    NihssCalculator,
    Abcd2Calculator,
    ModifiedRankinScaleCalculator,
    # Phase 13: Additional Scores
    TimiStemiCalculator,
    RockallScoreCalculator,
    Fib4IndexCalculator,
]
