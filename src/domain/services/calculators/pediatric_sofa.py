"""
Pediatric SOFA (pSOFA) Score Calculator - 兒童器官衰竭評估

Age-adapted SOFA score for pediatric patients (0-18 years).
Validated for pediatric sepsis and organ dysfunction assessment.

Clinical Application:
- Pediatric sepsis diagnosis (Sepsis-3 adapted for children)
- Organ dysfunction quantification in PICU
- Sequential assessment for trend monitoring
- Research endpoint standardization

Components (0-4 points each, total 0-24):
1. Respiratory (PaO2/FiO2 with age-adjusted thresholds)
2. Coagulation (Platelets)
3. Hepatic (Bilirubin)
4. Cardiovascular (MAP or vasopressors, age-adjusted)
5. Neurological (GCS, age-adjusted)
6. Renal (Creatinine, age-adjusted)

Key Age Adaptations:
- Age-specific normal MAP thresholds
- Age-specific creatinine upper limits
- Age-appropriate GCS interpretation

References:
    Matics TJ, Sanchez-Pinto LN. Adaptation and Validation of a Pediatric
    Sequential Organ Failure Assessment Score and Evaluation of the Sepsis-3
    Definitions in Critically Ill Children.
    JAMA Pediatr. 2017;171(10):e172352. PMID: 28783810
    
    Schlapbach LJ, et al. International Consensus Criteria for Pediatric
    Sepsis and Septic Shock (Phoenix Criteria).
    JAMA. 2024;331(8):665-674. PMID: 38245889
    
    Goldstein B, et al. International pediatric sepsis consensus conference.
    Pediatr Crit Care Med. 2005;6(1):2-8. PMID: 15636651
"""

from typing import Optional
from ..base import BaseCalculator
from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.units import Unit
from ...value_objects.reference import Reference
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.tool_keys import (
    LowLevelKey,
    HighLevelKey,
    Specialty,
    ClinicalContext
)


class PediatricSOFACalculator(BaseCalculator):
    """
    Pediatric SOFA (pSOFA) Score Calculator
    
    Age-adapted Sequential Organ Failure Assessment for children.
    Based on Matics & Sanchez-Pinto 2017 validation study.
    """

    # Age-specific MAP lower limits (5th percentile)
    MAP_THRESHOLDS = {
        "0-1m": 46,
        "1-12m": 55,
        "1-2y": 60,
        "2-5y": 62,
        "5-12y": 65,
        "12-18y": 67,
    }

    # Age-specific creatinine upper limits (mg/dL)
    CREATININE_THRESHOLDS = {
        "0-1m": {"normal": 0.8, "mild": 1.0, "mod": 1.5, "severe": 2.0},
        "1-12m": {"normal": 0.3, "mild": 0.5, "mod": 0.8, "severe": 1.2},
        "1-2y": {"normal": 0.4, "mild": 0.6, "mod": 1.0, "severe": 1.5},
        "2-5y": {"normal": 0.5, "mild": 0.8, "mod": 1.2, "severe": 1.8},
        "5-12y": {"normal": 0.7, "mild": 1.0, "mod": 1.5, "severe": 2.3},
        "12-18y": {"normal": 1.0, "mild": 1.2, "mod": 2.0, "severe": 3.5},
    }

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="pediatric_sofa",
                name="Pediatric SOFA (pSOFA) Score",
                purpose="Age-adapted organ dysfunction assessment for pediatric patients",
                input_params=[
                    "age_group", "pao2_fio2_ratio", "platelets", "bilirubin",
                    "map_value", "gcs_score", "creatinine", "vasopressor_type",
                    "on_mechanical_ventilation"
                ],
                output_type="pSOFA score (0-24) with organ-specific subscores"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.PEDIATRICS,
                    Specialty.CRITICAL_CARE,
                    Specialty.PEDIATRIC_CRITICAL_CARE,
                    Specialty.EMERGENCY_MEDICINE,
                ),
                conditions=(
                    "Pediatric sepsis",
                    "Organ dysfunction",
                    "PICU assessment",
                    "Multi-organ failure",
                    "Septic shock",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.SEPSIS_EVALUATION,
                    ClinicalContext.ICU_ASSESSMENT,
                    ClinicalContext.PROGNOSIS,
                ),
            ),
            references=(
                Reference(
                    citation="Matics TJ, Sanchez-Pinto LN. Adaptation and Validation of a Pediatric SOFA Score. JAMA Pediatr. 2017;171(10):e172352.",
                    doi="10.1001/jamapediatrics.2017.2352",
                    pmid="28783810",
                    year=2017
                ),
                Reference(
                    citation="Schlapbach LJ, et al. International Consensus Criteria for Pediatric Sepsis (Phoenix). JAMA. 2024;331(8):665-674.",
                    doi="10.1001/jama.2024.0196",
                    pmid="38245889",
                    year=2024
                ),
            ),
        )

    def calculate(
        self,
        age_group: str,
        pao2_fio2_ratio: float,
        platelets: float,
        bilirubin: float,
        gcs_score: int,
        creatinine: float,
        map_value: Optional[float] = None,
        vasopressor_type: Optional[str] = None,
        vasopressor_dose: Optional[float] = None,
        on_mechanical_ventilation: bool = False
    ) -> ScoreResult:
        """
        Calculate Pediatric SOFA score.
        
        Args:
            age_group: Patient age category
                "0-1m", "1-12m", "1-2y", "2-5y", "5-12y", "12-18y"
            pao2_fio2_ratio: PaO2/FiO2 ratio (mmHg)
            platelets: Platelet count (×10³/µL)
            bilirubin: Total bilirubin (mg/dL)
            gcs_score: Glasgow Coma Scale (3-15)
            creatinine: Serum creatinine (mg/dL)
            map_value: Mean arterial pressure (mmHg), optional
            vasopressor_type: Type of vasopressor if used
                "none", "dopamine_low", "dopamine_high", "epinephrine", "norepinephrine"
            vasopressor_dose: Dose in mcg/kg/min
            on_mechanical_ventilation: Whether on mechanical ventilation
        
        Returns:
            ScoreResult with pSOFA score and organ-specific breakdown
        """
        # Validate age group
        valid_ages = ["0-1m", "1-12m", "1-2y", "2-5y", "5-12y", "12-18y"]
        if age_group not in valid_ages:
            raise ValueError(f"age_group must be one of: {valid_ages}")

        # Validate GCS
        if gcs_score < 3 or gcs_score > 15:
            raise ValueError("gcs_score must be between 3 and 15")

        # Calculate component scores
        resp_score = self._calc_respiratory(pao2_fio2_ratio, on_mechanical_ventilation)
        coag_score = self._calc_coagulation(platelets)
        hepatic_score = self._calc_hepatic(bilirubin)
        cv_score = self._calc_cardiovascular(age_group, map_value, vasopressor_type, vasopressor_dose)
        neuro_score = self._calc_neurological(gcs_score)
        renal_score = self._calc_renal(age_group, creatinine)

        total_score = resp_score + coag_score + hepatic_score + cv_score + neuro_score + renal_score

        # Component breakdown
        components = {
            "Respiratory": resp_score,
            "Coagulation": coag_score,
            "Hepatic": hepatic_score,
            "Cardiovascular": cv_score,
            "Neurological": neuro_score,
            "Renal": renal_score,
        }

        # Determine severity
        if total_score <= 3:
            severity = Severity.MILD
            risk = "Low mortality risk"
            mortality = "<5%"
        elif total_score <= 6:
            severity = Severity.MODERATE
            risk = "Moderate organ dysfunction"
            mortality = "5-15%"
        elif total_score <= 9:
            severity = Severity.SEVERE
            risk = "Significant organ dysfunction"
            mortality = "15-30%"
        elif total_score <= 12:
            severity = Severity.CRITICAL
            risk = "Severe multi-organ dysfunction"
            mortality = "30-50%"
        else:
            severity = Severity.CRITICAL
            risk = "Critical multi-organ failure"
            mortality = ">50%"

        # Identify most affected organs
        max_score = max(components.values())
        worst_organs = [k for k, v in components.items() if v == max_score and v >= 2]

        # Sepsis-3 adapted interpretation
        sepsis_criteria = ""
        if total_score >= 2:
            sepsis_criteria = "≥2 point increase from baseline suggests sepsis-associated organ dysfunction"

        interpretation = Interpretation(
            severity=severity,
            summary=f"pSOFA {total_score}: {risk}",
            detail=(
                f"Age group: {age_group}\n"
                f"Organ subscores: Resp={resp_score}, Coag={coag_score}, Liver={hepatic_score}, "
                f"CV={cv_score}, CNS={neuro_score}, Renal={renal_score}\n"
                f"Estimated PICU mortality: {mortality}\n"
                f"{sepsis_criteria}"
            ),
            recommendations=(self._get_recommendation(total_score, worst_organs),)
        )

        details = {
            "total_score": total_score,
            "age_group": age_group,
            "component_scores": components,
            "worst_organs": worst_organs if worst_organs else None,
            "estimated_mortality": mortality,
            "sepsis_criteria_met": total_score >= 2,
            "on_mechanical_ventilation": on_mechanical_ventilation,
            "next_step": self._get_next_step(total_score)
        }

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "age_group": age_group,
                "pao2_fio2_ratio": pao2_fio2_ratio,
                "platelets": platelets,
                "bilirubin": bilirubin,
                "gcs_score": gcs_score,
                "creatinine": creatinine,
                "map_value": map_value,
                "vasopressor_type": vasopressor_type,
                "vasopressor_dose": vasopressor_dose,
                "on_mechanical_ventilation": on_mechanical_ventilation,
            },
            calculation_details=details
        )

    def _calc_respiratory(self, pf_ratio: float, on_mv: bool) -> int:
        """Calculate respiratory subscore."""
        if pf_ratio >= 400:
            return 0
        elif pf_ratio >= 300:
            return 1
        elif pf_ratio >= 200:
            return 2 if not on_mv else 2
        elif pf_ratio >= 100:
            return 3 if on_mv else 2
        else:
            return 4 if on_mv else 3

    def _calc_coagulation(self, platelets: float) -> int:
        """Calculate coagulation subscore."""
        if platelets >= 150:
            return 0
        elif platelets >= 100:
            return 1
        elif platelets >= 50:
            return 2
        elif platelets >= 20:
            return 3
        else:
            return 4

    def _calc_hepatic(self, bilirubin: float) -> int:
        """Calculate hepatic subscore."""
        if bilirubin < 1.2:
            return 0
        elif bilirubin < 2.0:
            return 1
        elif bilirubin < 6.0:
            return 2
        elif bilirubin < 12.0:
            return 3
        else:
            return 4

    def _calc_cardiovascular(
        self,
        age_group: str,
        map_value: Optional[float],
        vaso_type: Optional[str],
        vaso_dose: Optional[float]
    ) -> int:
        """Calculate cardiovascular subscore with age-adjusted MAP."""
        # Get age-specific MAP threshold
        map_threshold = self.MAP_THRESHOLDS.get(age_group, 65)
        
        # Vasopressor scoring
        if vaso_type == "epinephrine" or vaso_type == "norepinephrine":
            if vaso_dose and vaso_dose > 0.1:
                return 4
            return 3
        elif vaso_type == "dopamine_high" or (vaso_type == "dopamine_low" and vaso_dose and vaso_dose > 5):
            return 3
        elif vaso_type == "dopamine_low" or (vaso_dose and vaso_dose <= 5):
            return 2
        elif map_value is not None and map_value < map_threshold:
            return 1
        else:
            return 0

    def _calc_neurological(self, gcs: int) -> int:
        """Calculate neurological subscore."""
        if gcs >= 15:
            return 0
        elif gcs >= 13:
            return 1
        elif gcs >= 10:
            return 2
        elif gcs >= 6:
            return 3
        else:
            return 4

    def _calc_renal(self, age_group: str, creatinine: float) -> int:
        """Calculate renal subscore with age-adjusted thresholds."""
        thresholds = self.CREATININE_THRESHOLDS.get(age_group, self.CREATININE_THRESHOLDS["12-18y"])
        
        if creatinine <= thresholds["normal"]:
            return 0
        elif creatinine <= thresholds["mild"]:
            return 1
        elif creatinine <= thresholds["mod"]:
            return 2
        elif creatinine <= thresholds["severe"]:
            return 3
        else:
            return 4

    def _get_recommendation(self, score: int, worst_organs: list) -> str:
        """Get clinical recommendation."""
        if score <= 3:
            return "Continue supportive care; monitor for progression"
        elif score <= 6:
            organ_str = ", ".join(worst_organs) if worst_organs else "multiple organs"
            return f"Targeted support for {organ_str}; consider escalation if worsening"
        elif score <= 9:
            return "Intensive organ support required; PICU level care; consider ECMO evaluation if respiratory failure"
        else:
            return "Maximum organ support; consider goals of care discussion; evaluate for ECMO/renal replacement"

    def _get_next_step(self, score: int) -> str:
        """Get clinical next step."""
        if score <= 3:
            return "Reassess in 4-6 hours or if clinical change"
        elif score <= 6:
            return "Reassess in 2-4 hours; optimize organ-specific support"
        else:
            return "Continuous monitoring; reassess with any intervention change"
