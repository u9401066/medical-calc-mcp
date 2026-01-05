"""
SOFA-2 Score (Sequential Organ Failure Assessment - 2025 Update)

The SOFA-2 score is the updated version of the classic SOFA score, developed
and validated using data from 3.34 million ICU patients across 9 countries.
It provides improved calibration for contemporary ICU populations.

Key Updates from SOFA-1:
- Respiratory: New P/F thresholds (300, 225, 150, 75 vs. 400, 300, 200, 100)
- Liver: Updated bilirubin thresholds (1.2, 3.0, 6.0, 12.0 mg/dL)
- Hemostasis: New platelet thresholds (150, 100, 80, 50 vs. 150, 100, 50, 20 ×10³/μL)
- Cardiovascular: Combined norepinephrine + epinephrine dose-based scoring
- Brain: Includes sedation/delirium drugs consideration
- Added ECMO and RRT as scoring criteria

Reference:
    Ranzani OT, Singer M, Salluh JIF, et al. Development and Validation of the
    Sequential Organ Failure Assessment (SOFA)-2 Score.
    JAMA. Published Online October 29, 2025.
    DOI: 10.1001/jama.2025.20516
    PMID: 39476328
"""

from typing import Optional

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class Sofa2ScoreCalculator(BaseCalculator):
    """
    SOFA-2 Score Calculator (2025 Update)

    The Sequential Organ Failure Assessment (SOFA)-2 score assesses the
    function of six organ systems with updated thresholds based on
    contemporary ICU data from 3.34 million patients:

    1. Brain (GCS, sedation/delirium drugs)
    2. Respiratory (PaO2/FiO2 with advanced ventilatory support/ECMO)
    3. Cardiovascular (MAP and norepinephrine + epinephrine dose)
    4. Liver (Bilirubin)
    5. Kidney (Creatinine, urine output, RRT)
    6. Hemostasis (Platelets)

    Each organ system is scored 0-4, for a total score of 0-24.

    Validation: AUROC 0.79 (95% CI 0.76-0.81) for ICU mortality.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="sofa2_score",
                name="SOFA-2 Score (2025 Update)",
                purpose="Assess organ dysfunction with updated 2025 thresholds based on 3.3M patients",
                input_params=[
                    "gcs_score", "receiving_sedation_or_delirium_drugs",
                    "pao2_fio2_ratio", "advanced_ventilatory_support", "on_ecmo",
                    "map_value", "norepinephrine_epinephrine_dose",
                    "bilirubin", "creatinine", "urine_output_6h", "urine_output_12h",
                    "urine_output_24h", "on_rrt", "platelets"
                ],
                output_type="SOFA-2 score (0-24) with mortality prediction"
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
                    "ARDS",
                    "Acute Kidney Injury",
                    "Liver Failure",
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
                    "What is the updated SOFA score?",
                ),
                icd10_codes=("A41", "R65.20", "R65.21", "J96", "N17", "K72"),
                keywords=(
                    "SOFA-2", "SOFA2", "SOFA 2", "sepsis", "organ failure",
                    "organ dysfunction", "ICU", "mortality", "sequential organ failure",
                    "Sepsis-3", "infection", "critical care", "ECMO", "RRT",
                    "2025", "updated SOFA",
                )
            ),
            references=(
                Reference(
                    citation="Ranzani OT, Singer M, Salluh JIF, et al. Development and Validation "
                             "of the Sequential Organ Failure Assessment (SOFA)-2 Score. "
                             "JAMA. Published Online October 29, 2025.",
                    doi="10.1001/jama.2025.20516",
                    pmid="39476328",
                    year=2025
                ),
                Reference(
                    citation="Vincent JL, Moreno R, Takala J, et al. The SOFA (Sepsis-related "
                             "Organ Failure Assessment) score to describe organ dysfunction/failure. "
                             "Intensive Care Med. 1996;22(7):707-710. [Original SOFA score]",
                    doi="10.1007/BF01709751",
                    pmid="8844239",
                    year=1996
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )

    def calculate(
        self,
        gcs_score: int,
        pao2_fio2_ratio: float,
        bilirubin: float,
        creatinine: float,
        platelets: float,
        map_value: Optional[float] = None,
        norepinephrine_epinephrine_dose: Optional[float] = None,
        receiving_sedation_or_delirium_drugs: bool = False,
        advanced_ventilatory_support: bool = False,
        on_ecmo: bool = False,
        urine_output_6h: Optional[float] = None,
        urine_output_12h: Optional[float] = None,
        urine_output_24h: Optional[float] = None,
        on_rrt: bool = False,
    ) -> ScoreResult:
        """
        Calculate SOFA-2 score (2025 Update).

        Args:
            gcs_score: Glasgow Coma Scale (3-15)
            pao2_fio2_ratio: PaO2/FiO2 ratio (mmHg)
            bilirubin: Total bilirubin (mg/dL)
            creatinine: Serum creatinine (mg/dL)
            platelets: Platelet count (×10³/µL)
            map_value: Mean arterial pressure (mmHg), if no vasopressors
            norepinephrine_epinephrine_dose: Combined norepinephrine + epinephrine dose (µg/kg/min)
            receiving_sedation_or_delirium_drugs: Whether receiving sedative/delirium medications
            advanced_ventilatory_support: High FiO2, high PEEP, or proning
            on_ecmo: Whether on ECMO support
            urine_output_6h: Urine output in mL/kg/h over 6 hours (for <0.5 criterion)
            urine_output_12h: Urine output in mL/kg/h over 12 hours (for <0.5 criterion)
            urine_output_24h: Urine output in mL/kg/h over 24 hours (for <0.3 criterion)
            on_rrt: Whether on renal replacement therapy

        Returns:
            ScoreResult with SOFA-2 score and mortality prediction
        """
        # Calculate individual organ scores
        brain_score = self._brain_score(gcs_score, receiving_sedation_or_delirium_drugs)
        resp_score = self._respiratory_score(pao2_fio2_ratio, advanced_ventilatory_support, on_ecmo)
        cardio_score = self._cardiovascular_score(map_value, norepinephrine_epinephrine_dose)
        liver_score = self._liver_score(bilirubin)
        kidney_score = self._kidney_score(
            creatinine,
            urine_output_6h,
            urine_output_12h,
            urine_output_24h,
            on_rrt
        )
        hemostasis_score = self._hemostasis_score(platelets)

        # Total SOFA-2 score
        total_score = (
            brain_score + resp_score + cardio_score +
            liver_score + kidney_score + hemostasis_score
        )

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
                "gcs_score": gcs_score,
                "receiving_sedation_or_delirium_drugs": receiving_sedation_or_delirium_drugs,
                "pao2_fio2_ratio": pao2_fio2_ratio,
                "advanced_ventilatory_support": advanced_ventilatory_support,
                "on_ecmo": on_ecmo,
                "map_value": map_value,
                "norepinephrine_epinephrine_dose": norepinephrine_epinephrine_dose,
                "bilirubin": bilirubin,
                "creatinine": creatinine,
                "urine_output_6h": urine_output_6h,
                "urine_output_12h": urine_output_12h,
                "urine_output_24h": urine_output_24h,
                "on_rrt": on_rrt,
                "platelets": platelets,
            },
            calculation_details={
                "brain": brain_score,
                "respiratory": resp_score,
                "cardiovascular": cardio_score,
                "liver": liver_score,
                "kidney": kidney_score,
                "hemostasis": hemostasis_score,
                "total": total_score,
                "sofa_version": "SOFA-2 (2025)",
            },
            formula_used=(
                "SOFA-2 = Brain + Respiratory + Cardiovascular + Liver + Kidney + Hemostasis "
                "(each 0-4, total 0-24)"
            )
        )

    def _brain_score(self, gcs: int, on_sedation_delirium_drugs: bool) -> int:
        """
        Calculate Brain component (GCS with sedation consideration)

        Score 0: GCS 15
        Score 1: GCS 13-14 OR receiving sedative medications for delirium
        Score 2: GCS 9-12
        Score 3: GCS 6-8
        Score 4: GCS 3-5
        """
        if gcs == 15:
            # Score 1 if on sedation/delirium drugs even with normal GCS
            return 1 if on_sedation_delirium_drugs else 0
        elif gcs >= 13:  # 13-14
            return 1
        elif gcs >= 9:   # 9-12
            return 2
        elif gcs >= 6:   # 6-8
            return 3
        else:            # 3-5
            return 4

    def _respiratory_score(
        self,
        pao2_fio2: float,
        advanced_support: bool,
        on_ecmo: bool
    ) -> int:
        """
        Calculate Respiratory component (PaO2/FiO2)

        Score 0: P/F > 300
        Score 1: P/F ≤ 300
        Score 2: P/F ≤ 225
        Score 3: P/F ≤ 150 AND advanced ventilatory support
        Score 4: P/F ≤ 75 AND advanced ventilatory support OR ECMO

        Advanced ventilatory support: High FiO2 (>0.6), High PEEP, or proning
        """
        if on_ecmo:
            return 4

        if pao2_fio2 > 300:
            return 0
        elif pao2_fio2 > 225:  # ≤ 300
            return 1
        elif pao2_fio2 > 150:  # ≤ 225
            return 2
        elif pao2_fio2 > 75:   # ≤ 150
            return 3 if advanced_support else 2
        else:                   # ≤ 75
            return 4 if advanced_support else 3

    def _cardiovascular_score(
        self,
        map_value: Optional[float],
        ne_epi_dose: Optional[float]
    ) -> int:
        """
        Calculate Cardiovascular component

        Score 0: MAP ≥ 70 mmHg, no vasopressor
        Score 1: MAP < 70 mmHg, no vasopressor
        Score 2: NE + Epi ≤ 0.2 µg/kg/min (low dose)
        Score 3: NE + Epi > 0.2 to ≤ 0.4 µg/kg/min (medium dose)
        Score 4: NE + Epi > 0.4 µg/kg/min (high dose)

        Note: SOFA-2 combines norepinephrine and epinephrine doses
        Other vasopressors (vasopressin, dopamine, etc.) are not directly scored
        """
        # Check vasopressor dose first
        if ne_epi_dose is not None and ne_epi_dose > 0:
            if ne_epi_dose > 0.4:
                return 4
            elif ne_epi_dose > 0.2:
                return 3
            else:  # ≤ 0.2
                return 2

        # No vasopressors, check MAP
        if map_value is not None:
            return 1 if map_value < 70 else 0

        return 0

    def _liver_score(self, bilirubin: float) -> int:
        """
        Calculate Liver component (Bilirubin mg/dL)

        Score 0: ≤ 1.2
        Score 1: ≤ 3.0 (> 1.2)
        Score 2: ≤ 6.0 (> 3.0)
        Score 3: ≤ 12.0 (> 6.0)
        Score 4: > 12.0
        """
        if bilirubin <= 1.2:
            return 0
        elif bilirubin <= 3.0:
            return 1
        elif bilirubin <= 6.0:
            return 2
        elif bilirubin <= 12.0:
            return 3
        else:  # > 12.0
            return 4

    def _kidney_score(
        self,
        creatinine: float,
        uo_6h: Optional[float],
        uo_12h: Optional[float],
        uo_24h: Optional[float],
        on_rrt: bool
    ) -> int:
        """
        Calculate Kidney component (Creatinine and/or Urine Output)

        Score 0: Cr ≤ 1.2
        Score 1: Cr ≤ 2.0 (> 1.2) OR UO < 0.5 mL/kg/h for 6-12 hours
        Score 2: Cr ≤ 3.5 (> 2.0) OR UO < 0.5 mL/kg/h for ≥ 12 hours
        Score 3: Cr > 3.5 OR UO < 0.3 mL/kg/h for ≥ 24 hours
        Score 4: RRT or meeting criteria for RRT

        Use worst score from creatinine or urine output
        """
        if on_rrt:
            return 4

        # Calculate creatinine-based score
        cr_score = self._creatinine_score(creatinine)

        # Calculate urine output-based score
        uo_score = self._urine_output_score(uo_6h, uo_12h, uo_24h)

        # Return worst score
        return max(cr_score, uo_score)

    def _creatinine_score(self, creatinine: float) -> int:
        """Score based on creatinine alone"""
        if creatinine <= 1.2:
            return 0
        elif creatinine <= 2.0:
            return 1
        elif creatinine <= 3.5:
            return 2
        else:  # > 3.5
            return 3

    def _urine_output_score(
        self,
        uo_6h: Optional[float],
        uo_12h: Optional[float],
        uo_24h: Optional[float]
    ) -> int:
        """
        Score based on urine output.

        UO parameters are in mL/kg/h.
        - uo_6h: UO over 6 hours (<0.5 for 6-12h = score 1)
        - uo_12h: UO over 12 hours (<0.5 for ≥12h = score 2)
        - uo_24h: UO over 24 hours (<0.3 for ≥24h = score 3)
        """
        # Check 24h output first (for score 3)
        if uo_24h is not None and uo_24h < 0.3:
            return 3

        # Check 12h output (for score 2)
        if uo_12h is not None and uo_12h < 0.5:
            return 2

        # Check 6h output (for score 1)
        if uo_6h is not None and uo_6h < 0.5:
            return 1

        return 0

    def _hemostasis_score(self, platelets: float) -> int:
        """
        Calculate Hemostasis component (Platelets ×10³/µL)

        SOFA-2 updated thresholds:
        Score 0: > 150
        Score 1: ≤ 150
        Score 2: ≤ 100
        Score 3: ≤ 80
        Score 4: ≤ 50

        Note: SOFA-1 used: 150, 100, 50, 20
        """
        if platelets > 150:
            return 0
        elif platelets > 100:  # ≤ 150
            return 1
        elif platelets > 80:   # ≤ 100
            return 2
        elif platelets > 50:   # ≤ 80
            return 3
        else:                   # ≤ 50
            return 4

    def _get_interpretation(self, score: int) -> Interpretation:
        """Get interpretation based on total SOFA-2 score"""

        # Mortality estimates from SOFA-2 validation (AUROC 0.79)
        if score <= 1:
            mortality = "< 5%"
            severity = Severity.NORMAL
            summary = "Minimal organ dysfunction"
        elif score <= 3:
            mortality = "~5-10%"
            severity = Severity.MILD
            summary = "Mild organ dysfunction"
        elif score <= 6:
            mortality = "~15-25%"
            severity = Severity.MILD
            summary = "Moderate organ dysfunction"
        elif score <= 9:
            mortality = "~25-40%"
            severity = Severity.MODERATE
            summary = "Significant organ dysfunction"
        elif score <= 12:
            mortality = "~40-55%"
            severity = Severity.SEVERE
            summary = "Severe organ dysfunction"
        elif score <= 15:
            mortality = "~55-70%"
            severity = Severity.SEVERE
            summary = "Very severe organ dysfunction"
        else:  # > 15
            mortality = "> 75%"
            severity = Severity.CRITICAL
            summary = "Critical organ dysfunction"

        # Sepsis interpretation
        sepsis_note = ""
        if score >= 2:
            sepsis_note = (
                "SOFA-2 ≥2 indicates significant organ dysfunction. "
                "Consistent with Sepsis-3 criteria in suspected infection. "
            )

        return Interpretation(
            summary=f"SOFA-2 Score {score}: {summary}",
            detail=(
                f"{sepsis_note}Estimated ICU mortality: {mortality}. "
                f"SOFA-2 uses 2025 updated thresholds validated on 3.34 million ICU patients. "
                f"Calculate at admission and every 24 hours."
            ),
            severity=severity,
            stage=f"SOFA-2 {score}",
            stage_description=summary,
            recommendations=self._get_recommendations(score),
            warnings=self._get_warnings(score),
            next_steps=self._get_next_steps(score)
        )

    def _get_recommendations(self, score: int) -> tuple[str, ...]:
        if score >= 2:
            return (
                "SOFA-2 ≥2 indicates organ dysfunction in suspected infection",
                "Follow Surviving Sepsis Campaign Hour-1 Bundle if sepsis suspected",
                "Reassess SOFA-2 every 24 hours to monitor trajectory",
                "Consider early goal-directed therapy and source control",
                "Track delta SOFA-2 (change over time) for prognosis",
            )
        return (
            "Continue monitoring",
            "Reassess if clinical condition changes",
        )

    def _get_warnings(self, score: int) -> tuple[str, ...]:
        if score >= 12:
            return (
                "Very high mortality risk (>50%)",
                "Consider goals of care discussion with family",
                "Maximum supportive therapy indicated",
                "Consider palliative care consultation",
            )
        elif score >= 6:
            return (
                "Significant mortality risk (>20%)",
                "ICU-level care required",
                "Close monitoring essential",
            )
        return tuple()

    def _get_next_steps(self, score: int) -> tuple[str, ...]:
        if score >= 2:
            return (
                "Obtain blood cultures if not already done",
                "Administer broad-spectrum antibiotics within 1 hour if sepsis",
                "Begin fluid resuscitation (30 mL/kg crystalloid)",
                "Measure serum lactate",
                "Initiate vasopressors if hypotensive after fluid resuscitation",
                "Re-evaluate every 24 hours with SOFA-2",
            )
        return (
            "Continue routine ICU monitoring",
            "Repeat SOFA-2 in 24 hours",
        )
