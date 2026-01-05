"""
Cockcroft-Gault Creatinine Clearance Calculator

Estimates creatinine clearance (CrCl) for drug dosing adjustments.
Still widely used for drug dosing despite availability of CKD-EPI eGFR.

References:
    Cockcroft DW, Gault MH. Prediction of creatinine clearance from
    serum creatinine. Nephron. 1976;16(1):31-41.
    DOI: 10.1159/000180580
    PMID: 1244564

    FDA Guidance for Industry: Pharmacokinetics in Patients with
    Impaired Renal Function — Study Design, Data Analysis, and
    Impact on Dosing and Labeling. 2020.

    Dowling TC, Matzke GR, Murphy JE, Burckart GJ. Evaluation of renal
    drug dosing: prescribing information and clinical pharmacist
    approaches. Pharmacotherapy. 2010;30(8):776-786.
    DOI: 10.1592/phco.30.8.776
    PMID: 20653353
"""

from typing import Any, Literal, Optional

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import (
    ClinicalContext,
    HighLevelKey,
    LowLevelKey,
    Specialty,
)
from ...value_objects.units import Unit
from ..base import BaseCalculator


class CockcroftGaultCalculator(BaseCalculator):
    """
    Cockcroft-Gault Creatinine Clearance Calculator

    Estimates creatinine clearance (CrCl) for drug dosing.

    Formula:
        CrCl (mL/min) = [(140 - age) × weight (kg)] / [72 × SCr (mg/dL)]
        For females: × 0.85

    Weight Considerations:
        - Actual body weight (ABW): Original formula
        - Ideal body weight (IBW): For obese patients (ABW > 130% IBW)
        - Adjusted body weight (AdjBW): IBW + 0.4 × (ABW - IBW)

    Clinical Use:
        - Drug dosing adjustments (many drugs still use CG-CrCl)
        - Direct thrombin inhibitors (dabigatran)
        - Low-molecular-weight heparin
        - Aminoglycosides
        - Many antibiotics and antivirals

    Note: FDA still recommends Cockcroft-Gault for drug dosing
    rather than CKD-EPI eGFR in many drug labels.

    Limitations:
        - Less accurate at extremes of age, weight, or muscle mass
        - Not validated in AKI
        - Overestimates in obese patients using actual weight
        - Underestimates in elderly or malnourished
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="cockcroft_gault",
                name="Cockcroft-Gault Creatinine Clearance",
                purpose="Calculate creatinine clearance for drug dosing adjustments",
                input_params=["age", "weight_kg", "creatinine_mg_dl", "sex", "height_cm"],
                output_type="CrCl (mL/min) with dosing recommendations"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.NEPHROLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.INFECTIOUS_DISEASE,
                    Specialty.CARDIOLOGY,
                    Specialty.GERIATRICS,
                ),
                conditions=(
                    "Chronic kidney disease",
                    "Drug dosing",
                    "Renal impairment",
                    "Antibiotic dosing",
                    "DOAC dosing",
                    "Aminoglycoside dosing",
                ),
                clinical_contexts=(
                    ClinicalContext.DRUG_DOSING,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "What is the creatinine clearance for drug dosing?",
                    "How do I adjust drug dose for renal function?",
                    "Should I use actual or ideal body weight?",
                    "What is the CrCl for LMWH dosing?",
                    "How do I calculate Cockcroft-Gault?",
                ),
                icd10_codes=(
                    "N18",  # Chronic kidney disease
                    "N17",  # Acute kidney failure
                    "Z79.01",  # Long-term anticoagulant use
                ),
            ),
            references=(
                Reference(
                    citation=(
                        "Cockcroft DW, Gault MH. Prediction of creatinine clearance from "
                        "serum creatinine. Nephron. 1976;16(1):31-41."
                    ),
                    doi="10.1159/000180580",
                    pmid="1244564",
                    year=1976,
                ),
                Reference(
                    citation=(
                        "FDA Guidance for Industry: Pharmacokinetics in Patients with "
                        "Impaired Renal Function. 2020."
                    ),
                    year=2020,
                ),
                Reference(
                    citation=(
                        "Dowling TC, Matzke GR, Murphy JE, Burckart GJ. Evaluation of "
                        "renal drug dosing: prescribing information and clinical "
                        "pharmacist approaches. Pharmacotherapy. 2010;30(8):776-786."
                    ),
                    doi="10.1592/phco.30.8.776",
                    pmid="20653353",
                    year=2010,
                ),
            ),
        )

    def calculate(
        self,
        age: int,
        weight_kg: float,
        creatinine_mg_dl: float,
        sex: Literal["male", "female"],
        height_cm: Optional[float] = None,
    ) -> ScoreResult:
        """
        Calculate creatinine clearance using Cockcroft-Gault equation.

        Args:
            age: Age in years (18-120)
            weight_kg: Actual body weight in kg (30-300)
            creatinine_mg_dl: Serum creatinine in mg/dL (0.2-20.0)
            sex: Biological sex ("male" or "female")
            height_cm: Height in cm (optional, for IBW calculation)

        Returns:
            ScoreResult with CrCl in mL/min

        Raises:
            ValueError: If parameters are out of valid range
        """
        # Validate inputs
        if not 18 <= age <= 120:
            raise ValueError(f"Age must be 18-120 years, got {age}")
        if not 30 <= weight_kg <= 300:
            raise ValueError(f"Weight must be 30-300 kg, got {weight_kg}")
        if not 0.2 <= creatinine_mg_dl <= 20.0:
            raise ValueError(f"Creatinine must be 0.2-20.0 mg/dL, got {creatinine_mg_dl}")
        if height_cm is not None and not (100 <= height_cm <= 250):
            raise ValueError(f"Height must be 100-250 cm, got {height_cm}")

        # Calculate with actual body weight (ABW)
        crcl_abw = self._calculate_crcl(age, weight_kg, creatinine_mg_dl, sex)

        # Calculate IBW and adjusted weight if height provided
        ibw = None
        adjbw = None
        crcl_ibw = None
        crcl_adjbw = None
        weight_recommendation = "actual"

        if height_cm is not None:
            # Devine formula for IBW
            height_inches = height_cm / 2.54
            if sex == "male":
                ibw = 50 + 2.3 * (height_inches - 60)
            else:
                ibw = 45.5 + 2.3 * (height_inches - 60)

            ibw = max(ibw, 30)  # Minimum IBW

            # Check if obese (ABW > 130% IBW)
            if weight_kg > 1.3 * ibw:
                # Calculate adjusted body weight
                adjbw = ibw + 0.4 * (weight_kg - ibw)
                crcl_adjbw = self._calculate_crcl(age, adjbw, creatinine_mg_dl, sex)
                weight_recommendation = "adjusted"
            elif weight_kg < ibw:
                # Underweight - use actual weight
                weight_recommendation = "actual"

            crcl_ibw = self._calculate_crcl(age, ibw, creatinine_mg_dl, sex)

        # Determine primary CrCl to report
        if weight_recommendation == "adjusted" and crcl_adjbw is not None:
            primary_crcl = crcl_adjbw
        else:
            primary_crcl = crcl_abw

        # Get interpretation
        interpretation = self._get_interpretation(primary_crcl, weight_recommendation)

        # Build calculation details
        calc_details: dict[str, Any] = {
            "age": age,
            "weight_actual_kg": weight_kg,
            "creatinine_mg_dl": creatinine_mg_dl,
            "sex": sex,
            "crcl_actual_weight": round(crcl_abw, 1),
            "weight_used": weight_recommendation,
            "formula": "(140 - age) × weight / (72 × SCr)" + (" × 0.85" if sex == "female" else ""),
        }

        if height_cm is not None:
            calc_details["height_cm"] = height_cm
            calc_details["ibw_kg"] = round(ibw, 1) if ibw else None
            calc_details["crcl_ibw"] = round(crcl_ibw, 1) if crcl_ibw else None

            if adjbw is not None:
                calc_details["adjbw_kg"] = round(adjbw, 1)
                calc_details["crcl_adjbw"] = round(crcl_adjbw, 1) if crcl_adjbw else None
                calc_details["obesity_note"] = (
                    f"ABW ({weight_kg:.1f} kg) > 130% IBW ({ibw:.1f} kg). "
                    f"Using adjusted body weight for dosing."
                )

        calc_details["dosing_category"] = self._get_dosing_category(primary_crcl)

        return ScoreResult(
            tool_id=self.tool_id,
            tool_name=self.name,
            value=float(round(primary_crcl, 1)),
            unit=Unit.ML_MIN,
            interpretation=interpretation,
            references=list(self.references),
            calculation_details=calc_details,
        )

    def _calculate_crcl(
        self,
        age: int,
        weight: float,
        creatinine: float,
        sex: str
    ) -> float:
        """Calculate CrCl using Cockcroft-Gault formula"""
        crcl = ((140 - age) * weight) / (72 * creatinine)
        if sex == "female":
            crcl *= 0.85
        return crcl

    def _get_dosing_category(self, crcl: float) -> dict[str, str]:
        """Get dosing category based on CrCl"""
        if crcl >= 90:
            return {"category": "Normal", "adjustment": "No adjustment needed"}
        elif crcl >= 60:
            return {"category": "Mild impairment", "adjustment": "Usually no adjustment"}
        elif crcl >= 30:
            return {"category": "Moderate impairment", "adjustment": "Often requires 50% reduction"}
        elif crcl >= 15:
            return {"category": "Severe impairment", "adjustment": "Often requires 50-75% reduction"}
        else:
            return {"category": "Kidney failure", "adjustment": "Often contraindicated or dialysis dosing"}

    def _get_interpretation(self, crcl: float, weight_used: str) -> Interpretation:
        """Generate interpretation based on CrCl value"""
        recommendations: tuple[str, ...]

        if crcl >= 90:
            stage = "Normal renal function"
            severity = Severity.NORMAL
            recommendations = (
                "No dose adjustment typically required for renal function",
                "Standard dosing for renally eliminated drugs",
                "Monitor renal function periodically",
            )
        elif crcl >= 60:
            stage = "Mild renal impairment"
            severity = Severity.MILD
            recommendations = (
                "Most drugs: no adjustment needed",
                "Check specific drug labeling for CrCl thresholds",
                "Consider dose reduction for drugs with narrow therapeutic index",
                "Monitor for drug accumulation",
            )
        elif crcl >= 30:
            stage = "Moderate renal impairment"
            severity = Severity.MODERATE
            recommendations = (
                "Many drugs require dose reduction (typically 50%)",
                "Extend dosing interval for some drugs",
                "Avoid nephrotoxic combinations",
                "Monitor drug levels where available (vancomycin, aminoglycosides)",
                "DOACs: reduced doses (check specific thresholds)",
            )
        elif crcl >= 15:
            stage = "Severe renal impairment"
            severity = Severity.SEVERE
            recommendations = (
                "Significant dose reductions required for most renally cleared drugs",
                "Many drugs contraindicated or require TDM",
                "DOACs: dabigatran contraindicated, others at reduced dose",
                "Aminoglycosides: extended interval dosing with TDM",
                "Consider nephrology/pharmacy consultation",
            )
        else:
            stage = "Kidney failure"
            severity = Severity.CRITICAL
            recommendations = (
                "Most renally cleared drugs contraindicated or require dialysis dosing",
                "Consult nephrology and clinical pharmacy",
                "Consider dialyzability of drugs",
                "Many drugs need post-dialysis supplemental dosing",
                "Avoid nephrotoxins absolutely",
            )

        weight_note = ""
        if weight_used == "adjusted":
            weight_note = " Using adjusted body weight for obese patient."
        elif weight_used == "ibw":
            weight_note = " Using ideal body weight."

        return Interpretation(
            summary=f"CrCl: {crcl:.1f} mL/min - {stage}",
            detail=(
                f"Creatinine Clearance (Cockcroft-Gault): {crcl:.1f} mL/min. "
                f"{stage}.{weight_note} "
                f"FDA recommends Cockcroft-Gault for drug dosing adjustments."
            ),
            severity=severity,
            stage=stage,
            stage_description=f"CrCl {crcl:.1f} mL/min",
            recommendations=recommendations,
            warnings=(
                "Cockcroft-Gault may overestimate GFR in obese patients",
                "May underestimate GFR in elderly or malnourished",
                "Not validated for acute kidney injury",
                "Different drugs use different CrCl thresholds - check labeling",
            ) if crcl < 60 else (
                "This is NOT the same as CKD-EPI eGFR",
                "Many drug labels specifically require CG-CrCl",
            ),
            next_steps=(
                "Apply drug-specific dosing adjustments",
                "Consult pharmacist for complex regimens",
                "Monitor renal function and drug levels as indicated",
            ),
        )
