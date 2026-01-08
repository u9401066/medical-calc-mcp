"""
MELD Score Calculator

Model for End-Stage Liver Disease (MELD) score predicts 90-day mortality
in patients with end-stage liver disease and is used for liver transplant
prioritization.

Original Reference:
    Kamath PS, Wiesner RH, Malinchoc M, et al. A model to predict survival
    in patients with end-stage liver disease. Hepatology. 2001;33(2):464-470.
    doi:10.1053/jhep.2001.22172. PMID: 11172350.

MELD-Na Reference:
    Kim WR, Biggins SW, Kremers WK, et al. Hyponatremia and mortality among
    patients on the liver-transplant waiting list. N Engl J Med.
    2008;359(10):1018-1026.
    doi:10.1056/NEJMoa0801209. PMID: 18768945.

MELD 3.0 Reference:
    Kim WR, Mannalithara A, Heimbach JK, et al. MELD 3.0: The Model for
    End-Stage Liver Disease Updated for the Modern Era. Gastroenterology.
    2021;161(6):1887-1895.e4.
    doi:10.1053/j.gastro.2021.08.050. PMID: 34481845.
"""

import math

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import (
    ClinicalContext,
    HighLevelKey,
    LowLevelKey,
    Specialty,
)
from ...value_objects.units import Unit
from ..base import BaseCalculator


class MeldScoreCalculator(BaseCalculator):
    """
    MELD Score for End-Stage Liver Disease

    MELD (original) formula:
    MELD = 10 × [0.957 × ln(Cr) + 0.378 × ln(Bilirubin) + 1.120 × ln(INR)] + 6.43

    MELD-Na formula (UNOS 2016):
    MELD-Na = MELD + 1.32 × (137 - Na) - [0.033 × MELD × (137 - Na)]

    Scoring rules:
    - Minimum lab values: Cr, Bilirubin, INR set to 1.0 if <1.0
    - Maximum Creatinine: 4.0 mg/dL
    - Dialysis (≥2x/week or CVVHD): Creatinine set to 4.0
    - Sodium range: 125-137 mEq/L
    - Score range: 6-40

    Interpretation:
    - <9: 1.9% 90-day mortality
    - 10-19: 6.0% 90-day mortality
    - 20-29: 19.6% 90-day mortality
    - 30-39: 52.6% 90-day mortality
    - ≥40: 71.3% 90-day mortality
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="meld_score",
                name="MELD Score",
                purpose="Predict 90-day mortality in end-stage liver disease for transplant prioritization",
                input_params=[
                    "creatinine",
                    "bilirubin",
                    "inr",
                    "sodium",
                    "on_dialysis",
                ],
                output_type="MELD and MELD-Na scores with 90-day mortality risk",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.HEPATOLOGY,
                    Specialty.GASTROENTEROLOGY,
                    Specialty.SURGERY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                ),
                conditions=(
                    "end-stage liver disease",
                    "cirrhosis",
                    "liver failure",
                    "hepatic encephalopathy",
                    "portal hypertension",
                    "liver transplant",
                    "decompensated cirrhosis",
                ),
                clinical_contexts=(
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.ELIGIBILITY,
                ),
                clinical_questions=(
                    "Should this patient be listed for liver transplant?",
                    "What is the mortality risk for this cirrhotic patient?",
                    "What is the MELD score for transplant listing?",
                    "How severe is this patient's liver disease?",
                    "Does this patient need urgent liver transplant?",
                ),
                icd10_codes=(
                    "K74",  # Fibrosis and cirrhosis of liver
                    "K72",  # Hepatic failure, not elsewhere classified
                    "K76.7",  # Hepatorenal syndrome
                    "K70.3",  # Alcoholic cirrhosis of liver
                ),
                keywords=(
                    "MELD score",
                    "MELD-Na",
                    "liver transplant",
                    "end-stage liver disease",
                    "cirrhosis prognosis",
                    "hepatic failure",
                    "transplant listing",
                ),
            ),
            references=(
                Reference(
                    citation="Kamath PS, Wiesner RH, Malinchoc M, et al. A model to predict survival "
                    "in patients with end-stage liver disease. Hepatology. 2001;33(2):464-470.",
                    doi="10.1053/jhep.2001.22172",
                    pmid="11172350",
                    year=2001,
                ),
                Reference(
                    citation="Kim WR, Biggins SW, Kremers WK, et al. Hyponatremia and mortality among "
                    "patients on the liver-transplant waiting list. N Engl J Med. "
                    "2008;359(10):1018-1026.",
                    doi="10.1056/NEJMoa0801209",
                    pmid="18768945",
                    year=2008,
                ),
                Reference(
                    citation="Kim WR, Mannalithara A, Heimbach JK, et al. MELD 3.0: The Model for "
                    "End-Stage Liver Disease Updated for the Modern Era. Gastroenterology. "
                    "2021;161(6):1887-1895.e4.",
                    doi="10.1053/j.gastro.2021.08.050",
                    pmid="34481845",
                    year=2021,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        creatinine: float,
        bilirubin: float,
        inr: float,
        sodium: float = 137.0,
        on_dialysis: bool = False,
    ) -> ScoreResult:
        """
        Calculate MELD and MELD-Na scores.

        Args:
            creatinine: Serum creatinine (mg/dL)
            bilirubin: Total bilirubin (mg/dL)
            inr: International Normalized Ratio
            sodium: Serum sodium (mEq/L), default 137
            on_dialysis: Dialyzed ≥2x in past week or CVVHD (sets Cr to 4.0)

        Returns:
            ScoreResult with MELD and MELD-Na scores and mortality estimates
        """
        # Apply MELD scoring rules
        # Set dialysis patients to Cr 4.0
        if on_dialysis:
            creatinine = 4.0

        # Apply floor values (minimum 1.0)
        cr = max(creatinine, 1.0)
        bili = max(bilirubin, 1.0)
        inr_adj = max(inr, 1.0)

        # Cap creatinine at 4.0
        cr = min(cr, 4.0)

        # Cap sodium at bounds
        na = max(min(sodium, 137), 125)

        # Calculate original MELD score
        meld = 10 * (0.957 * math.log(cr) + 0.378 * math.log(bili) + 1.120 * math.log(inr_adj)) + 6.43

        # Round and cap MELD
        meld = round(meld)
        meld = max(min(meld, 40), 6)

        # Calculate MELD-Na
        meld_na = meld + 1.32 * (137 - na) - (0.033 * meld * (137 - na))
        meld_na = round(meld_na)
        meld_na = max(min(meld_na, 40), 6)

        # Determine interpretation
        interpretation = self._interpret_score(meld, meld_na)

        # Component details
        components = {
            "Creatinine (mg/dL)": creatinine,
            "Creatinine (adjusted)": cr,
            "Bilirubin (mg/dL)": bilirubin,
            "Bilirubin (adjusted)": bili,
            "INR": inr,
            "INR (adjusted)": inr_adj,
            "Sodium (mEq/L)": sodium,
            "Sodium (adjusted)": na,
            "On dialysis": "Yes" if on_dialysis else "No",
            "MELD Score": meld,
            "MELD-Na Score": meld_na,
        }

        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=meld_na,  # Return MELD-Na as primary value
            unit=Unit.SCORE,
            interpretation=interpretation,
            calculation_details=components,
            references=list(self.references),
        )

    def _interpret_score(self, meld: int, meld_na: int) -> Interpretation:
        """Generate interpretation based on MELD/MELD-Na score"""

        # Use MELD-Na for mortality estimation
        score = meld_na

        # 90-day mortality estimates
        if score < 10:
            mortality = "1.9%"
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
        elif score < 20:
            mortality = "6.0%"
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
        elif score < 30:
            mortality = "19.6%"
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
        elif score < 40:
            mortality = "52.6%"
            severity = Severity.SEVERE
            risk_level = RiskLevel.VERY_HIGH
        else:
            mortality = "71.3%"
            severity = Severity.CRITICAL
            risk_level = RiskLevel.VERY_HIGH

        summary = f"MELD = {meld}, MELD-Na = {meld_na}: {mortality} 90-day mortality"

        if score < 15:
            detail = f"Lower MELD score indicates less severe liver disease. The estimated 90-day mortality is {mortality}."
            recommendations = [
                "Continue medical management of cirrhosis",
                "Monitor for complications (ascites, encephalopathy, variceal bleeding)",
                "Regular follow-up with hepatology",
            ]
            next_steps = [
                "Reassess MELD score every 3-6 months",
                "Optimize nutrition and treat reversible causes",
                "Hepatocellular carcinoma surveillance if indicated",
                "Consider transplant evaluation if expected to deteriorate",
            ]
            urgency = "Routine evaluation"

        elif score < 25:
            detail = (
                f"Moderate MELD score indicates significant liver dysfunction. "
                f"The estimated 90-day mortality is {mortality}. "
                f"Transplant evaluation should be considered."
            )
            recommendations = [
                "Refer for liver transplant evaluation if not already listed",
                "Optimize management of cirrhosis complications",
                "Consider TIPS if indicated for refractory ascites/varices",
            ]
            next_steps = [
                "Complete transplant workup if candidate",
                "Reassess MELD score regularly (every 1-3 months)",
                "Manage hepatorenal syndrome, encephalopathy if present",
                "Address modifiable factors (alcohol cessation, nutrition)",
            ]
            urgency = "Transplant evaluation recommended"

        else:
            detail = (
                f"High MELD score indicates severe liver dysfunction with high mortality risk. "
                f"The estimated 90-day mortality is {mortality}. "
                f"Urgent transplant evaluation is indicated."
            )
            recommendations = [
                "Urgent liver transplant evaluation/listing",
                "Consider ICU admission if acute deterioration",
                "Aggressive management of complications",
                "Discuss goals of care with patient/family",
            ]
            next_steps = [
                "Expedite transplant listing if candidate",
                "Weekly MELD score updates for listing priority",
                "Consider living donor evaluation",
                "Manage hepatorenal syndrome, coagulopathy, encephalopathy",
            ]
            urgency = "Urgent transplant evaluation"

        return Interpretation(
            summary=summary,
            severity=severity,
            detail=detail,
            stage=f"MELD = {meld}, MELD-Na = {meld_na}",
            stage_description=f"90-day mortality: {mortality}",
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
            warnings=(f"High mortality risk ({mortality}) - {urgency}",) if score >= 25 else tuple(),
        )
