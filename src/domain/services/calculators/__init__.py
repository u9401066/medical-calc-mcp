"""
Medical Calculators

Domain services implementing clinical calculators.
Each calculator inherits from BaseCalculator and provides:
- Metadata for tool discovery (LowLevelKey + HighLevelKey)
- References to original papers (Vancouver citation format)
- Calculate method returning ScoreResult
"""

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
from .barthel_index import BarthelIndexCalculator

# Phase 17: Obstetrics & Neonatology (Classic Tools)
from .bishop_score import BishopScoreCalculator

# Phase 14: General Tools
from .body_surface_area import BodySurfaceAreaCalculator
from .bosniak import BosniakClassificationCalculator
from .bsa_derm import BSADermatologyCalculator
from .cam_icu import CamIcuCalculator

# Phase 7: Surgery/Perioperative & Pulmonology
from .caprini_vte import CapriniVteCalculator
from .caps5 import CAPS5Calculator
from .cas_graves import CASCalculator
from .centor_score import CentorScoreCalculator

# Phase 30: Geriatrics (Guideline-Recommended)
from .cfs import ClinicalFrailtyScaleCalculator
from .chads2_va import Chads2VaCalculator  # 2024 ESC - sex-neutral

# Phase 6: Cardiology
from .chads2_vasc import Chads2VascCalculator

# MedCalc-Bench P0: Comorbidity Assessment
from .charlson_comorbidity import CharlsonComorbidityIndexCalculator

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
from .cushingoid import CushingoidScoreCalculator
from .das28 import DAS28Calculator
from .delta_ratio import DeltaRatioCalculator
from .dlqi import DLQICalculator

# Phase 21: Oncology & Geriatrics (Guideline-Recommended)
from .ecog_ps import ECOGPerformanceStatusCalculator

# Phase 28: OB/GYN (Guideline-Recommended)
from .epds import EPDSCalculator

# Phase 19: Guideline-Recommended Missing Tools (2025)
from .euroscore_ii import EuroSCOREIICalculator

# MedCalc-Bench P0: AKI Differential Diagnosis
from .fena import FENaCalculator
from .fib4_index import Fib4IndexCalculator

# Phase 26: Endocrinology (Guideline-Recommended)
from .findrisc import FINDRISCCalculator
from .fisher_grade import FisherGradeCalculator
from .four_at_delirium import FourATCalculator
from .four_score import FourScoreCalculator
from .four_ts_hit import FourTsHitCalculator

# MedCalc-Bench P0: Cardiovascular Risk Assessment
from .framingham import FraminghamRiskScoreCalculator
from .frax import FRAXCalculator
from .free_water_deficit import FreeWaterDeficitCalculator
from .gad7 import GAD7Calculator
from .gcs import GlasgowComaScaleCalculator

# Phase 18: High-Priority GI Bleeding & Trauma Tools (Guideline-Recommended)
from .glasgow_blatchford import GlasgowBlatchfordCalculator
from .grace_score import GraceScoreCalculator
from .hama import HAMACalculator
from .hamd import HAMDCalculator
from .has_bled import HasBledCalculator  # Phase 8: 2024 ESC recommended
from .heart_score import HeartScoreCalculator
from .hfa_peff import HFAPEFFCalculator

# Phase 14: Extended Neurology (SAH & ICH)
from .hunt_hess import HuntHessCalculator

# Phase 20: ICU & Cardiac (Existing Guideline Gaps)
from .icdsc import ICDSCCalculator
from .ich_score import IchScoreCalculator
from .iciq_sf import ICIQSFCalculator

# Phase 11: Upcoming Calculators (All Completed)
from .ideal_body_weight import IdealBodyWeightCalculator

# Phase 27: Urology (Guideline-Recommended)
from .ipss import IPSSCalculator
from .iss import InjurySeverityScoreCalculator
from .karnofsky import KarnofskyPerformanceScaleCalculator
from .kdigo_aki import KdigoAkiCalculator
from .lille_model import LilleModelCalculator
from .mabl import MablCalculator
from .maddrey_df import MaddreyDFCalculator
from .madrs import MADRSCalculator
from .mallampati_score import MallampatiScoreCalculator

# Phase 16: Infectious Disease (Guideline-Recommended)
from .mascc_score import MasccScoreCalculator

# Phase 6: Hepatology
from .meld_score import MeldScoreCalculator

# MedCalc-Bench P0: Opioid Risk Assessment
from .mme_calculator import MMECalculator
from .mmse import MMSECalculator
from .mna import MNACalculator
from .moca import MoCACalculator
from .modified_rankin_scale import ModifiedRankinScaleCalculator
from .murray_score import MurrayLungInjuryScoreCalculator
from .nds import NDSCalculator
from .news_score import NewsScoreCalculator

# Phase 12: Neurology
from .nihss import NihssCalculator

# Phase 22: Nutrition & Rheumatology (Guideline-Recommended)
from .nrs_2002 import NRS2002Calculator
from .nutric_score import NUTRICScoreCalculator
from .osmolar_gap import OsmolarGapCalculator
from .parkland_formula import ParklandFormulaCalculator

# Phase 25: Dermatology (Guideline-Recommended)
from .pasi import PASICalculator
from .pcl5 import PCL5Calculator

# Phase 5: Pediatric & Anesthesia Calculators
from .pediatric_dosing import PediatricDosingCalculator
from .pediatric_gcs import PediatricGCSCalculator
from .pediatric_sofa import PediatricSOFACalculator

# MedCalc-Bench P0: PE Rule-out
from .perc_rule import PERCRuleCalculator
from .pews import PEWSCalculator
from .pf_ratio import PfRatioCalculator

# Phase 24: Psychiatry (Guideline-Recommended)
from .phq9 import PHQ9Calculator
from .pim3 import PIM3Calculator
from .pitt_bacteremia import PittBacteremiaCalculator
from .pop_q import POPQCalculator
from .psi_port import PsiPortCalculator
from .qsofa_score import QsofaScoreCalculator
from .rass import RassCalculator
from .rcri import RcriCalculator
from .rockall_score import RockallScoreCalculator
from .rox_index import RoxIndexCalculator
from .rts import RevisedTraumaScoreCalculator
from .salt import SALTCalculator
from .scorad import SCORADCalculator

# Phase 23: CV Prevention & Bone Health (Guideline-Recommended)
from .score2 import SCORE2Calculator

# MedCalc-Bench P0: Laboratory Calculations
from .serum_osmolality import SerumOsmolalityCalculator
from .sflt_plgf import SFltPlGFRatioCalculator
from .shock_index import ShockIndexCalculator

# MedCalc-Bench P0: Sepsis Assessment
from .sirs import SIRSCriteriaCalculator
from .sofa2_score import Sofa2ScoreCalculator  # SOFA-2 (JAMA 2025)

# Phase 4: ICU/Emergency Calculators
from .sofa_score import SofaScoreCalculator
from .spesi import SimplifiedPESICalculator
from .stone_score import STONEScoreCalculator
from .stop_bang import StopBangCalculator
from .tbsa import TbsaCalculator

# Phase 13: Additional Scores
from .timi_stemi import TimiStemiCalculator
from .toronto_css import TorontoCSSCalculator
from .transfusion_calc import TransfusionCalculator
from .triss import TRISSCalculator
from .tug import TUGCalculator

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
    # Phase 19: Guideline-Recommended Missing Tools (2025)
    "RevisedTraumaScoreCalculator",
    "TRISSCalculator",
    "MaddreyDFCalculator",
    "LilleModelCalculator",
    "EuroSCOREIICalculator",
    # Phase 20: ICU & Cardiac (Existing Guideline Gaps)
    "ICDSCCalculator",
    "MurrayLungInjuryScoreCalculator",
    "HFAPEFFCalculator",
    # Phase 21: Oncology & Geriatrics (Guideline-Recommended)
    "ECOGPerformanceStatusCalculator",
    "KarnofskyPerformanceScaleCalculator",
    "FourATCalculator",
    # Phase 22: Nutrition & Rheumatology (Guideline-Recommended)
    "NRS2002Calculator",
    "DAS28Calculator",
    "NUTRICScoreCalculator",
    # Phase 23: CV Prevention & Bone Health (Guideline-Recommended)
    "SCORE2Calculator",
    "FRAXCalculator",
    # Phase 24: Psychiatry (Guideline-Recommended)
    "PHQ9Calculator",
    "GAD7Calculator",
    "HAMDCalculator",
    "HAMACalculator",
    "MADRSCalculator",
    "CAPS5Calculator",
    "PCL5Calculator",
    # Phase 25: Dermatology (Guideline-Recommended)
    "PASICalculator",
    "SCORADCalculator",
    "DLQICalculator",
    "SALTCalculator",
    "BSADermatologyCalculator",
    # Phase 26: Endocrinology (Guideline-Recommended)
    "FINDRISCCalculator",
    "NDSCalculator",
    "TorontoCSSCalculator",
    "CASCalculator",
    "CushingoidScoreCalculator",
    # Phase 27: Urology (Guideline-Recommended)
    "IPSSCalculator",
    "ICIQSFCalculator",
    "STONEScoreCalculator",
    "BosniakClassificationCalculator",
    # Phase 28: OB/GYN (Guideline-Recommended)
    "EPDSCalculator",
    "POPQCalculator",
    "SFltPlGFRatioCalculator",
    # Phase 30: Geriatrics (Guideline-Recommended)
    "ClinicalFrailtyScaleCalculator",
    "MMSECalculator",
    "MoCACalculator",
    "TUGCalculator",
    "BarthelIndexCalculator",
    "MNACalculator",
    # MedCalc-Bench P0: Comorbidity Assessment
    "CharlsonComorbidityIndexCalculator",
    # MedCalc-Bench P0: AKI Differential Diagnosis
    "FENaCalculator",
    # MedCalc-Bench P0: Sepsis Assessment
    "SIRSCriteriaCalculator",
    # MedCalc-Bench P0: Laboratory Calculations
    "SerumOsmolalityCalculator",
    # MedCalc-Bench P0: PE Rule-out
    "PERCRuleCalculator",
    # MedCalc-Bench P0: Opioid Risk Assessment
    "MMECalculator",
    # MedCalc-Bench P0: Cardiovascular Risk Assessment
    "FraminghamRiskScoreCalculator",
]


# Calculator registry for easy iteration
CALCULATORS: list[type[BaseCalculator]] = [
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
    # Phase 19: Guideline-Recommended Missing Tools (2025)
    RevisedTraumaScoreCalculator,
    TRISSCalculator,
    MaddreyDFCalculator,
    LilleModelCalculator,
    EuroSCOREIICalculator,
    # Phase 20: ICU & Cardiac (Existing Guideline Gaps)
    ICDSCCalculator,
    MurrayLungInjuryScoreCalculator,
    HFAPEFFCalculator,
    # Phase 21: Oncology & Geriatrics (Guideline-Recommended)
    ECOGPerformanceStatusCalculator,
    KarnofskyPerformanceScaleCalculator,
    FourATCalculator,
    # Phase 22: Nutrition & Rheumatology (Guideline-Recommended)
    NRS2002Calculator,
    DAS28Calculator,
    NUTRICScoreCalculator,
    # Phase 23: CV Prevention & Bone Health (Guideline-Recommended)
    SCORE2Calculator,
    FRAXCalculator,
    # Phase 24: Psychiatry (Guideline-Recommended)
    PHQ9Calculator,
    GAD7Calculator,
    HAMDCalculator,
    HAMACalculator,
    MADRSCalculator,
    CAPS5Calculator,
    PCL5Calculator,
    # Phase 25: Dermatology (Guideline-Recommended)
    PASICalculator,
    SCORADCalculator,
    DLQICalculator,
    SALTCalculator,
    BSADermatologyCalculator,
    # Phase 26: Endocrinology (Guideline-Recommended)
    FINDRISCCalculator,
    NDSCalculator,
    TorontoCSSCalculator,
    CASCalculator,
    CushingoidScoreCalculator,
    # Phase 27: Urology (Guideline-Recommended)
    IPSSCalculator,
    ICIQSFCalculator,
    STONEScoreCalculator,
    BosniakClassificationCalculator,
    # Phase 28: OB/GYN (Guideline-Recommended)
    EPDSCalculator,
    POPQCalculator,
    SFltPlGFRatioCalculator,
    # Phase 30: Geriatrics (Guideline-Recommended)
    ClinicalFrailtyScaleCalculator,
    MMSECalculator,
    MoCACalculator,
    TUGCalculator,
    BarthelIndexCalculator,
    MNACalculator,
    # MedCalc-Bench P0: Comorbidity Assessment
    CharlsonComorbidityIndexCalculator,
    # MedCalc-Bench P0: AKI Differential Diagnosis
    FENaCalculator,
    # MedCalc-Bench P0: Sepsis Assessment
    SIRSCriteriaCalculator,
    # MedCalc-Bench P0: Laboratory Calculations
    SerumOsmolalityCalculator,
    # MedCalc-Bench P0: PE Rule-out
    PERCRuleCalculator,
    # MedCalc-Bench P0: Opioid Risk Assessment
    MMECalculator,
    # MedCalc-Bench P0: Cardiovascular Risk Assessment
    FraminghamRiskScoreCalculator,
]
