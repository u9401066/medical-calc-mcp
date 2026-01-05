"""
Medical Calculators

Domain services implementing clinical calculators.
Each calculator inherits from BaseCalculator and provides:
- Metadata for tool discovery (LowLevelKey + HighLevelKey)
- References to original papers (Vancouver citation format)
- Calculate method returning ScoreResult
"""

from typing import Type
from ..base import BaseCalculator

from .aa_gradient import AaGradientCalculator
from .abcd2 import Abcd2Calculator
from .acef_ii_score import AcefIiScoreCalculator
from .aims65 import AIMS65Calculator
from .aldrete_score import AldreteScoreCalculator

# Phase 9: Acid-Base & Electrolytes
from .anion_gap import AnionGapCalculator
from .apache_ii import ApacheIiCalculator

# Phase 12: Additional Anesthesiology Tools
from .apfel_ponv import ApfelPonvCalculator

# Phase 15: Pediatric Scores (Guideline-Recommended)
from .apgar_score import APGARScoreCalculator
from .asa_physical_status import AsaPhysicalStatusCalculator
from .ballard_score import BallardScoreCalculator

# Phase 17: Obstetrics & Neonatology (Classic Tools)
from .bishop_score import BishopScoreCalculator

# Phase 14: General Tools
from .body_surface_area import BodySurfaceAreaCalculator
from .cam_icu import CamIcuCalculator

# Phase 7: Surgery/Perioperative & Pulmonology
from .caprini_vte import CapriniVteCalculator
from .centor_score import CentorScoreCalculator
from .chads2_va import Chads2VaCalculator  # 2024 ESC - sex-neutral

# Phase 6: Cardiology
from .chads2_vasc import Chads2VascCalculator

# Phase 8: Guideline-Recommended Tools
from .child_pugh import ChildPughCalculator
from .ckd_epi_2021 import CkdEpi2021Calculator
from .cockcroft_gault import CockcroftGaultCalculator
from .corrected_calcium import CorrectedCalciumCalculator

# Phase 10: High-Priority Tools
from .corrected_qt import CorrectedQtCalculator
from .corrected_sodium import CorrectedSodiumCalculator
from .cpis import CpisCalculator

# Phase 6: Pulmonology
from .curb65 import Curb65Calculator
from .delta_ratio import DeltaRatioCalculator
from .fib4_index import Fib4IndexCalculator
from .fisher_grade import FisherGradeCalculator
from .four_score import FourScoreCalculator
from .four_ts_hit import FourTsHitCalculator
from .free_water_deficit import FreeWaterDeficitCalculator
from .gcs import GlasgowComaScaleCalculator

# Phase 18: High-Priority GI Bleeding & Trauma Tools (Guideline-Recommended)
from .glasgow_blatchford import GlasgowBlatchfordCalculator
from .grace_score import GraceScoreCalculator
from .has_bled import HasBledCalculator  # Phase 8: 2024 ESC recommended
from .heart_score import HeartScoreCalculator

# Phase 14: Extended Neurology (SAH & ICH)
from .hunt_hess import HuntHessCalculator
from .ich_score import IchScoreCalculator

# Phase 11: Upcoming Calculators (All Completed)
from .ideal_body_weight import IdealBodyWeightCalculator
from .iss import InjurySeverityScoreCalculator
from .kdigo_aki import KdigoAkiCalculator
from .mabl import MablCalculator
from .mallampati_score import MallampatiScoreCalculator

# Phase 16: Infectious Disease (Guideline-Recommended)
from .mascc_score import MasccScoreCalculator

# Phase 6: Hepatology
from .meld_score import MeldScoreCalculator
from .modified_rankin_scale import ModifiedRankinScaleCalculator
from .news_score import NewsScoreCalculator

# Phase 12: Neurology
from .nihss import NihssCalculator
from .osmolar_gap import OsmolarGapCalculator
from .parkland_formula import ParklandFormulaCalculator

# Phase 5: Pediatric & Anesthesia Calculators
from .pediatric_dosing import PediatricDosingCalculator
from .pediatric_gcs import PediatricGCSCalculator
from .pediatric_sofa import PediatricSOFACalculator
from .pews import PEWSCalculator
from .pf_ratio import PfRatioCalculator
from .pim3 import PIM3Calculator
from .pitt_bacteremia import PittBacteremiaCalculator
from .psi_port import PsiPortCalculator
from .qsofa_score import QsofaScoreCalculator
from .rass import RassCalculator
from .rcri import RcriCalculator
from .rockall_score import RockallScoreCalculator
from .rox_index import RoxIndexCalculator
from .shock_index import ShockIndexCalculator
from .sofa2_score import Sofa2ScoreCalculator  # SOFA-2 (JAMA 2025)

# Phase 4: ICU/Emergency Calculators
from .sofa_score import SofaScoreCalculator
from .spesi import SimplifiedPESICalculator
from .stop_bang import StopBangCalculator
from .tbsa import TbsaCalculator

# Phase 13: Additional Scores
from .timi_stemi import TimiStemiCalculator
from .transfusion_calc import TransfusionCalculator

# Phase 6: Emergency Medicine
from .wells_dvt import WellsDvtCalculator
from .wells_pe import WellsPeCalculator

# Phase 9b: Additional Acid-Base Calculators
from .winters_formula import WintersFormulaCalculator

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

    # Phase 14: Extended Neurology (SAH & ICH)
    "HuntHessCalculator",
    "FisherGradeCalculator",
    "FourScoreCalculator",
    "IchScoreCalculator",

    # Phase 14: General Tools
    "BodySurfaceAreaCalculator",
    "CockcroftGaultCalculator",
    "CorrectedCalciumCalculator",
    "ParklandFormulaCalculator",

    # Phase 15: Pediatric Scores (Guideline-Recommended)
    "APGARScoreCalculator",
    "PEWSCalculator",
    "PediatricSOFACalculator",
    "PIM3Calculator",
    "PediatricGCSCalculator",

    # Phase 16: Infectious Disease (Guideline-Recommended)
    "MasccScoreCalculator",
    "PittBacteremiaCalculator",
    "CentorScoreCalculator",
    "CpisCalculator",

    # Phase 17: Obstetrics & Neonatology (Classic Tools)
    "BishopScoreCalculator",
    "BallardScoreCalculator",

    # Phase 18: High-Priority GI Bleeding & Trauma Tools
    "GlasgowBlatchfordCalculator",
    "AIMS65Calculator",
    "TbsaCalculator",
    "InjurySeverityScoreCalculator",
    "SimplifiedPESICalculator",
]


# Calculator registry for easy iteration
CALCULATORS: list[Type[BaseCalculator]] = [
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
    # Phase 14: Extended Neurology (SAH & ICH)
    HuntHessCalculator,
    FisherGradeCalculator,
    FourScoreCalculator,
    IchScoreCalculator,
    # Phase 14: General Tools
    BodySurfaceAreaCalculator,
    CockcroftGaultCalculator,
    CorrectedCalciumCalculator,
    ParklandFormulaCalculator,
    # Phase 15: Pediatric Scores (Guideline-Recommended)
    APGARScoreCalculator,
    PEWSCalculator,
    PediatricSOFACalculator,
    PIM3Calculator,
    PediatricGCSCalculator,
    # Phase 16: Infectious Disease (Guideline-Recommended)
    MasccScoreCalculator,
    PittBacteremiaCalculator,
    CentorScoreCalculator,
    CpisCalculator,
    # Phase 17: Obstetrics & Neonatology (Classic Tools)
    BishopScoreCalculator,
    BallardScoreCalculator,
    # Phase 18: High-Priority GI Bleeding & Trauma Tools
    GlasgowBlatchfordCalculator,
    AIMS65Calculator,
    TbsaCalculator,
    InjurySeverityScoreCalculator,
    SimplifiedPESICalculator,
]
