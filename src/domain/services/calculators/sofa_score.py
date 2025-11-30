"""
SOFA Score (Sequential Organ Failure Assessment)

The SOFA score is used to track a patient's status during the stay in an ICU
and to determine the extent of organ dysfunction. It is the recommended
method for identifying organ dysfunction in the Sepsis-3 definition.

Reference (Original):
    Vincent JL, Moreno R, Takala J, et al. The SOFA (Sepsis-related Organ Failure 
    Assessment) score to describe organ dysfunction/failure. On behalf of the Working 
    Group on Sepsis-Related Problems of the European Society of Intensive Care Medicine. 
    Intensive Care Med. 1996;22(7):707-710.
    DOI: 10.1007/BF01709751
    PMID: 8844239

Reference (Sepsis-3):
    Singer M, Deutschman CS, Seymour CW, et al. The Third International Consensus 
    Definitions for Sepsis and Septic Shock (Sepsis-3). JAMA. 2016;315(8):801-810.
    DOI: 10.1001/jama.2016.0287
    PMID: 26903338

Guideline Citation:
    Evans L, Rhodes A, Alhazzani W, et al. Surviving Sepsis Campaign: International 
    Guidelines for Management of Sepsis and Septic Shock 2021. Crit Care Med. 
    2021;49(11):e1063-e1143.
    DOI: 10.1097/CCM.0000000000005337
    PMID: 34605781
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


class SofaScoreCalculator(BaseCalculator):
    """
    SOFA Score Calculator
    
    The Sequential Organ Failure Assessment (SOFA) score assesses the
    function of six organ systems:
    1. Respiratory (PaO2/FiO2)
    2. Coagulation (Platelets)
    3. Liver (Bilirubin)
    4. Cardiovascular (MAP and vasopressors)
    5. CNS (Glasgow Coma Scale)
    6. Renal (Creatinine or urine output)
    
    Each organ system is scored 0-4, for a total score of 0-24.
    
    According to Sepsis-3:
    - Sepsis is defined as a SOFA score increase of ≥2 points
    - A SOFA score ≥2 is associated with >10% in-hospital mortality
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="sofa_score",
                name="SOFA Score (Sequential Organ Failure Assessment)",
                purpose="Assess organ dysfunction and predict ICU mortality in sepsis",
                input_params=[
                    "pao2_fio2_ratio", "is_mechanically_ventilated",
                    "platelets", "bilirubin", "map_or_vasopressors",
                    "gcs_score", "creatinine", "urine_output_24h"
                ],
                output_type="SOFA score (0-24) with mortality prediction"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.ANESTHESIOLOGY,
                    Specialty.PULMONOLOGY,
                ),
                conditions=(
                    "Sepsis",
                    "Septic Shock",
                    "Organ Dysfunction",
                    "Multi-Organ Failure",
                    "MODS",
                    "Critical Illness",
                    "Infection",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.MONITORING,
                    ClinicalContext.ICU_MANAGEMENT,
                    ClinicalContext.DIAGNOSIS,
                ),
                clinical_questions=(
                    "Does this patient have sepsis?",
                    "How severe is this patient's organ dysfunction?",
                    "What is the ICU mortality risk?",
                    "Is the patient getting better or worse?",
                    "Should I escalate care?",
                ),
                icd10_codes=("A41", "R65.20", "R65.21"),
                keywords=(
                    "SOFA", "sepsis", "organ failure", "organ dysfunction",
                    "ICU", "mortality", "sequential organ failure",
                    "Sepsis-3", "infection", "critical care",
                )
            ),
            references=(
                Reference(
                    citation="Vincent JL, Moreno R, Takala J, et al. The SOFA (Sepsis-related "
                             "Organ Failure Assessment) score to describe organ dysfunction/failure. "
                             "Intensive Care Med. 1996;22(7):707-710.",
                    doi="10.1007/BF01709751",
                    pmid="8844239",
                    year=1996
                ),
                Reference(
                    citation="Singer M, Deutschman CS, Seymour CW, et al. The Third International "
                             "Consensus Definitions for Sepsis and Septic Shock (Sepsis-3). "
                             "JAMA. 2016;315(8):801-810.",
                    doi="10.1001/jama.2016.0287",
                    pmid="26903338",
                    year=2016
                ),
                Reference(
                    citation="Evans L, Rhodes A, Alhazzani W, et al. Surviving Sepsis Campaign: "
                             "International Guidelines for Management of Sepsis and Septic Shock 2021. "
                             "Crit Care Med. 2021;49(11):e1063-e1143.",
                    doi="10.1097/CCM.0000000000005337",
                    pmid="34605781",
                    year=2021
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )
    
    def calculate(
        self,
        pao2_fio2_ratio: float,
        platelets: float,
        bilirubin: float,
        gcs_score: int,
        creatinine: float,
        map_value: Optional[float] = None,
        dopamine_dose: Optional[float] = None,
        dobutamine_any: bool = False,
        epinephrine_dose: Optional[float] = None,
        norepinephrine_dose: Optional[float] = None,
        is_mechanically_ventilated: bool = False,
        urine_output_24h: Optional[float] = None,
    ) -> ScoreResult:
        """
        Calculate SOFA score.
        
        Args:
            pao2_fio2_ratio: PaO2/FiO2 ratio (mmHg)
            platelets: Platelet count (×10³/µL)
            bilirubin: Total bilirubin (mg/dL)
            gcs_score: Glasgow Coma Scale (3-15)
            creatinine: Serum creatinine (mg/dL)
            map_value: Mean arterial pressure (mmHg), if no vasopressors
            dopamine_dose: Dopamine dose (µg/kg/min), if used
            dobutamine_any: Whether dobutamine is being used (any dose)
            epinephrine_dose: Epinephrine dose (µg/kg/min), if used
            norepinephrine_dose: Norepinephrine dose (µg/kg/min), if used
            is_mechanically_ventilated: Whether patient is on mechanical ventilation
            urine_output_24h: 24-hour urine output (mL), optional
            
        Returns:
            ScoreResult with SOFA score and mortality prediction
        """
        # Calculate individual organ scores
        resp_score = self._respiratory_score(pao2_fio2_ratio, is_mechanically_ventilated)
        coag_score = self._coagulation_score(platelets)
        liver_score = self._liver_score(bilirubin)
        cardio_score = self._cardiovascular_score(
            map_value, dopamine_dose, dobutamine_any, 
            epinephrine_dose, norepinephrine_dose
        )
        cns_score = self._cns_score(gcs_score)
        renal_score = self._renal_score(creatinine, urine_output_24h)
        
        # Total SOFA score
        total_score = resp_score + coag_score + liver_score + cardio_score + cns_score + renal_score
        
        # Get interpretation
        interpretation = self._get_interpretation(total_score)
        
        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "pao2_fio2_ratio": pao2_fio2_ratio,
                "platelets": platelets,
                "bilirubin": bilirubin,
                "gcs_score": gcs_score,
                "creatinine": creatinine,
                "map_value": map_value,
                "dopamine_dose": dopamine_dose,
                "dobutamine_any": dobutamine_any,
                "epinephrine_dose": epinephrine_dose,
                "norepinephrine_dose": norepinephrine_dose,
                "is_mechanically_ventilated": is_mechanically_ventilated,
                "urine_output_24h": urine_output_24h,
            },
            calculation_details={
                "respiratory": resp_score,
                "coagulation": coag_score,
                "liver": liver_score,
                "cardiovascular": cardio_score,
                "cns": cns_score,
                "renal": renal_score,
                "total": total_score,
            },
            formula_used="SOFA = Respiratory + Coagulation + Liver + Cardiovascular + CNS + Renal (each 0-4)"
        )
    
    def _respiratory_score(self, pao2_fio2: float, mechanically_ventilated: bool) -> int:
        """Calculate respiratory component (PaO2/FiO2)"""
        if pao2_fio2 >= 400:
            return 0
        elif pao2_fio2 >= 300:
            return 1
        elif pao2_fio2 >= 200:
            return 2
        elif pao2_fio2 >= 100:
            return 3 if mechanically_ventilated else 2
        else:  # < 100
            return 4 if mechanically_ventilated else 3
    
    def _coagulation_score(self, platelets: float) -> int:
        """Calculate coagulation component (Platelets ×10³/µL)"""
        if platelets >= 150:
            return 0
        elif platelets >= 100:
            return 1
        elif platelets >= 50:
            return 2
        elif platelets >= 20:
            return 3
        else:  # < 20
            return 4
    
    def _liver_score(self, bilirubin: float) -> int:
        """Calculate liver component (Bilirubin mg/dL)"""
        if bilirubin < 1.2:
            return 0
        elif bilirubin < 2.0:
            return 1
        elif bilirubin < 6.0:
            return 2
        elif bilirubin < 12.0:
            return 3
        else:  # >= 12.0
            return 4
    
    def _cardiovascular_score(
        self,
        map_value: Optional[float],
        dopamine_dose: Optional[float],
        dobutamine_any: bool,
        epinephrine_dose: Optional[float],
        norepinephrine_dose: Optional[float]
    ) -> int:
        """Calculate cardiovascular component"""
        # Check for high-dose vasopressors first
        if (epinephrine_dose and epinephrine_dose > 0.1) or \
           (norepinephrine_dose and norepinephrine_dose > 0.1):
            return 4
        
        if (dopamine_dose and dopamine_dose > 15) or \
           (epinephrine_dose and epinephrine_dose <= 0.1) or \
           (norepinephrine_dose and norepinephrine_dose <= 0.1):
            return 3
        
        if (dopamine_dose and dopamine_dose > 5) or dobutamine_any:
            return 2
        
        if dopamine_dose and dopamine_dose <= 5:
            return 1
        
        # No vasopressors, check MAP
        if map_value is not None and map_value < 70:
            return 1
        
        return 0
    
    def _cns_score(self, gcs: int) -> int:
        """Calculate CNS component (Glasgow Coma Scale)"""
        if gcs >= 15:
            return 0
        elif gcs >= 13:
            return 1
        elif gcs >= 10:
            return 2
        elif gcs >= 6:
            return 3
        else:  # < 6
            return 4
    
    def _renal_score(self, creatinine: float, urine_output: Optional[float]) -> int:
        """Calculate renal component (Creatinine mg/dL or urine output mL/day)"""
        # Check urine output if available (takes precedence for severe scores)
        if urine_output is not None:
            if urine_output < 200:
                return 4
            elif urine_output < 500:
                return max(3, self._creatinine_score(creatinine))
        
        return self._creatinine_score(creatinine)
    
    def _creatinine_score(self, creatinine: float) -> int:
        """Score based on creatinine alone"""
        if creatinine < 1.2:
            return 0
        elif creatinine < 2.0:
            return 1
        elif creatinine < 3.5:
            return 2
        elif creatinine < 5.0:
            return 3
        else:  # >= 5.0
            return 4
    
    def _get_interpretation(self, score: int) -> Interpretation:
        """Get interpretation based on total SOFA score"""
        
        # Mortality estimates from original Vincent paper and Sepsis-3 validation
        if score <= 1:
            mortality = "< 5%"
            severity = Severity.NORMAL
            summary = "Minimal organ dysfunction"
        elif score <= 3:
            mortality = "~5-10%"
            severity = Severity.MILD
            summary = "Mild organ dysfunction"
        elif score <= 6:
            mortality = "~15-20%"
            severity = Severity.MILD
            summary = "Moderate organ dysfunction"
        elif score <= 9:
            mortality = "~25-35%"
            severity = Severity.MODERATE
            summary = "Significant organ dysfunction"
        elif score <= 12:
            mortality = "~40-50%"
            severity = Severity.SEVERE
            summary = "Severe organ dysfunction"
        elif score <= 15:
            mortality = "~50-70%"
            severity = Severity.SEVERE
            summary = "Very severe organ dysfunction"
        else:  # > 15
            mortality = "> 70%"
            severity = Severity.CRITICAL
            summary = "Critical organ dysfunction"
        
        # Sepsis-3 specific interpretation
        sepsis_note = ""
        if score >= 2:
            sepsis_note = "SOFA ≥2 meets Sepsis-3 criteria for organ dysfunction. "
        
        return Interpretation(
            summary=f"SOFA Score {score}: {summary}",
            detail=f"{sepsis_note}Estimated ICU mortality: {mortality}. "
                   f"The SOFA score should be calculated at ICU admission and every 24 hours.",
            severity=severity,
            stage=f"SOFA {score}",
            stage_description=summary,
            recommendations=self._get_recommendations(score),
            warnings=self._get_warnings(score),
            next_steps=self._get_next_steps(score)
        )
    
    def _get_recommendations(self, score: int) -> tuple:
        if score >= 2:
            return (
                "Per Sepsis-3: SOFA ≥2 indicates organ dysfunction in suspected infection",
                "Follow Surviving Sepsis Campaign Hour-1 Bundle if sepsis suspected",
                "Reassess SOFA every 24 hours to monitor trajectory",
                "Consider early goal-directed therapy and source control",
            )
        return (
            "Continue monitoring",
            "Reassess if clinical condition changes",
        )
    
    def _get_warnings(self, score: int) -> tuple:
        if score >= 12:
            return (
                "Very high mortality risk (>50%)",
                "Consider goals of care discussion with family",
                "Maximum supportive therapy indicated",
            )
        elif score >= 6:
            return (
                "Significant mortality risk",
                "ICU-level care required",
            )
        return tuple()
    
    def _get_next_steps(self, score: int) -> tuple:
        if score >= 2:
            return (
                "Obtain blood cultures if not already done",
                "Administer broad-spectrum antibiotics within 1 hour if sepsis",
                "Begin fluid resuscitation (30 mL/kg crystalloid)",
                "Measure serum lactate",
                "Initiate vasopressors if hypotensive after fluid resuscitation",
            )
        return (
            "Continue routine ICU monitoring",
            "Repeat SOFA in 24 hours",
        )
