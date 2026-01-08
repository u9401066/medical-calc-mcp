"""
Caprini VTE Risk Assessment Calculator

Stratifies risk of venous thromboembolism (VTE) in surgical patients
to guide prophylaxis decisions.

Original Reference:
    Caprini JA. Thrombosis risk assessment as a guide to quality patient care.
    Dis Mon. 2005;51(2-3):70-78.
    doi:10.1016/j.disamonth.2005.02.003. PMID: 15900257.

Validation Reference:
    Bahl V, Hu HM, Henke PK, Wakefield TW, Campbell DA Jr, Caprini JA.
    A validation study of a retrospective venous thromboembolism risk
    scoring method. Ann Surg. 2010;251(2):344-350.
    doi:10.1097/SLA.0b013e3181b7fca6. PMID: 19779324.

2010 Review:
    Caprini JA. Risk assessment as a guide for the prevention of the many
    faces of venous thromboembolism. Am J Surg. 2010;199(1 Suppl):S3-10.
    doi:10.1016/j.amjsurg.2009.10.006. PMID: 20103082.
"""

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


class CapriniVteCalculator(BaseCalculator):
    """
    Caprini VTE Risk Assessment Score

    Comprehensive risk stratification for VTE in surgical patients.

    Risk Factor Categories:

    1 Point Each:
    - Age 41-60 years
    - Minor surgery planned
    - History of prior major surgery (<1 month)
    - Varicose veins
    - History of inflammatory bowel disease
    - Swollen legs (current)
    - Obesity (BMI >25)
    - Acute MI
    - CHF (<1 month)
    - Sepsis (<1 month)
    - Serious lung disease (including pneumonia <1 month)
    - Abnormal pulmonary function (COPD)
    - Medical patient currently at bed rest
    - Leg plaster cast or brace
    - Central venous access

    2 Points Each:
    - Age 61-74 years
    - Arthroscopic surgery
    - Malignancy (present or previous)
    - Major surgery (>45 min)
    - Laparoscopic surgery (>45 min)
    - Patient confined to bed (>72 hours)
    - Immobilizing plaster cast (<1 month)

    3 Points Each:
    - Age ≥75 years
    - History of DVT/PE
    - Family history of thrombosis
    - Positive Factor V Leiden
    - Positive Prothrombin 20210A
    - Elevated serum homocysteine
    - Positive Lupus anticoagulant
    - Elevated anticardiolipin antibodies
    - HIT (heparin-induced thrombocytopenia)
    - Other congenital or acquired thrombophilia

    5 Points Each:
    - Stroke (<1 month)
    - Elective arthroplasty
    - Hip, pelvis, or leg fracture (<1 month)
    - Acute spinal cord injury (<1 month)

    For Women Only:
    - Oral contraceptives or HRT: +1
    - Pregnancy or postpartum (<1 month): +1
    - Unexplained stillbirth, recurrent spontaneous abortion (≥3),
      premature birth with toxemia or growth-restricted infant: +1

    Risk Stratification:
    - 0 points: Very Low Risk (VTE rate ~0.5%)
    - 1-2 points: Low Risk (VTE rate ~1.5%)
    - 3-4 points: Moderate Risk (VTE rate ~3%)
    - ≥5 points: High Risk (VTE rate ~6%)
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="caprini_vte",
                name="Caprini VTE Risk Assessment Score",
                purpose="Stratify VTE risk in surgical patients to guide prophylaxis",
                input_params=[
                    "age_years",
                    "minor_surgery",
                    "major_surgery",
                    "laparoscopic_surgery_gt_45min",
                    "arthroscopic_surgery",
                    "prior_major_surgery_lt_1mo",
                    "varicose_veins",
                    "inflammatory_bowel_disease",
                    "swollen_legs",
                    "obesity_bmi_gt_25",
                    "acute_mi",
                    "chf_lt_1mo",
                    "sepsis_lt_1mo",
                    "lung_disease",
                    "copd",
                    "bed_rest_medical",
                    "bed_confined_gt_72hr",
                    "leg_cast_or_brace",
                    "immobilizing_cast_lt_1mo",
                    "central_venous_access",
                    "malignancy",
                    "history_dvt_pe",
                    "family_history_thrombosis",
                    "factor_v_leiden",
                    "prothrombin_20210a",
                    "elevated_homocysteine",
                    "lupus_anticoagulant",
                    "anticardiolipin_antibodies",
                    "hit_history",
                    "other_thrombophilia",
                    "stroke_lt_1mo",
                    "elective_arthroplasty",
                    "hip_pelvis_leg_fracture_lt_1mo",
                    "spinal_cord_injury_lt_1mo",
                    "female",
                    "oral_contraceptives_or_hrt",
                    "pregnancy_or_postpartum",
                    "pregnancy_loss_history",
                ],
                output_type="Caprini score with VTE risk level and prophylaxis recommendations",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.SURGERY,
                    Specialty.ANESTHESIOLOGY,
                    Specialty.ORTHOPEDICS,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.HEMATOLOGY,
                ),
                conditions=(
                    "venous thromboembolism",
                    "VTE",
                    "deep vein thrombosis",
                    "DVT",
                    "pulmonary embolism",
                    "PE",
                    "thrombosis prophylaxis",
                    "perioperative VTE",
                    "surgical VTE risk",
                ),
                clinical_contexts=(
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What VTE prophylaxis should this surgical patient receive?",
                    "What is this patient's risk of DVT/PE after surgery?",
                    "Does this patient need chemoprophylaxis or mechanical prophylaxis?",
                    "How long should VTE prophylaxis continue postoperatively?",
                    "Should I use heparin or LMWH for this patient?",
                ),
                icd10_codes=(
                    "Z79.01",  # Long term use of anticoagulants
                    "I82.4",  # Acute embolism and thrombosis of deep veins of lower extremity
                    "I26.9",  # Pulmonary embolism without acute cor pulmonale
                    "Z87.2",  # Personal history of diseases of blood
                ),
                keywords=(
                    "Caprini score",
                    "Caprini risk assessment",
                    "VTE prophylaxis",
                    "DVT prophylaxis",
                    "surgical VTE risk",
                    "thromboprophylaxis",
                    "perioperative anticoagulation",
                    "LMWH prophylaxis",
                    "mechanical prophylaxis",
                    "SCDs",
                ),
            ),
            references=(
                Reference(
                    citation="Caprini JA. Thrombosis risk assessment as a guide to quality patient care. Dis Mon. 2005;51(2-3):70-78.",
                    doi="10.1016/j.disamonth.2005.02.003",
                    pmid="15900257",
                    year=2005,
                ),
                Reference(
                    citation="Bahl V, Hu HM, Henke PK, Wakefield TW, Campbell DA Jr, Caprini JA. "
                    "A validation study of a retrospective venous thromboembolism risk "
                    "scoring method. Ann Surg. 2010;251(2):344-350.",
                    doi="10.1097/SLA.0b013e3181b7fca6",
                    pmid="19779324",
                    year=2010,
                ),
                Reference(
                    citation="Caprini JA. Risk assessment as a guide for the prevention of "
                    "the many faces of venous thromboembolism. Am J Surg. "
                    "2010;199(1 Suppl):S3-10.",
                    doi="10.1016/j.amjsurg.2009.10.006",
                    pmid="20103082",
                    year=2010,
                ),
            ),
            version="2005",
            validation_status="validated",
        )

    def calculate(
        self,
        age_years: int,
        # 1-point surgical/medical factors
        minor_surgery: bool = False,
        major_surgery: bool = False,
        laparoscopic_surgery_gt_45min: bool = False,
        arthroscopic_surgery: bool = False,
        prior_major_surgery_lt_1mo: bool = False,
        varicose_veins: bool = False,
        inflammatory_bowel_disease: bool = False,
        swollen_legs: bool = False,
        obesity_bmi_gt_25: bool = False,
        acute_mi: bool = False,
        chf_lt_1mo: bool = False,
        sepsis_lt_1mo: bool = False,
        lung_disease: bool = False,
        copd: bool = False,
        bed_rest_medical: bool = False,
        bed_confined_gt_72hr: bool = False,
        leg_cast_or_brace: bool = False,
        immobilizing_cast_lt_1mo: bool = False,
        central_venous_access: bool = False,
        # 2-3 point factors
        malignancy: bool = False,
        history_dvt_pe: bool = False,
        family_history_thrombosis: bool = False,
        factor_v_leiden: bool = False,
        prothrombin_20210a: bool = False,
        elevated_homocysteine: bool = False,
        lupus_anticoagulant: bool = False,
        anticardiolipin_antibodies: bool = False,
        hit_history: bool = False,
        other_thrombophilia: bool = False,
        # 5-point factors
        stroke_lt_1mo: bool = False,
        elective_arthroplasty: bool = False,
        hip_pelvis_leg_fracture_lt_1mo: bool = False,
        spinal_cord_injury_lt_1mo: bool = False,
        # Female-specific factors
        female: bool = False,
        oral_contraceptives_or_hrt: bool = False,
        pregnancy_or_postpartum: bool = False,
        pregnancy_loss_history: bool = False,
    ) -> ScoreResult:
        """
        Calculate Caprini VTE Risk Assessment Score.

        Args:
            age_years: Patient age in years
            minor_surgery: Minor surgery planned
            major_surgery: Major surgery (>45 min)
            laparoscopic_surgery_gt_45min: Laparoscopic surgery >45 min
            arthroscopic_surgery: Arthroscopic surgery
            prior_major_surgery_lt_1mo: History of major surgery <1 month
            varicose_veins: Varicose veins present
            inflammatory_bowel_disease: History of IBD
            swollen_legs: Current leg swelling
            obesity_bmi_gt_25: BMI >25
            acute_mi: Acute myocardial infarction
            chf_lt_1mo: Congestive heart failure <1 month
            sepsis_lt_1mo: Sepsis <1 month
            lung_disease: Serious lung disease including pneumonia <1 month
            copd: COPD or abnormal pulmonary function
            bed_rest_medical: Medical patient currently at bed rest
            bed_confined_gt_72hr: Confined to bed >72 hours
            leg_cast_or_brace: Leg plaster cast or brace
            immobilizing_cast_lt_1mo: Immobilizing plaster cast <1 month
            central_venous_access: Central venous access
            malignancy: Present or previous malignancy
            history_dvt_pe: History of DVT or PE
            family_history_thrombosis: Family history of thrombosis
            factor_v_leiden: Positive Factor V Leiden
            prothrombin_20210a: Positive Prothrombin 20210A
            elevated_homocysteine: Elevated serum homocysteine
            lupus_anticoagulant: Positive lupus anticoagulant
            anticardiolipin_antibodies: Elevated anticardiolipin antibodies
            hit_history: History of heparin-induced thrombocytopenia
            other_thrombophilia: Other congenital or acquired thrombophilia
            stroke_lt_1mo: Stroke <1 month
            elective_arthroplasty: Elective major lower extremity arthroplasty
            hip_pelvis_leg_fracture_lt_1mo: Hip, pelvis, or leg fracture <1 month
            spinal_cord_injury_lt_1mo: Acute spinal cord injury <1 month
            female: Patient is female
            oral_contraceptives_or_hrt: Oral contraceptives or HRT
            pregnancy_or_postpartum: Pregnancy or postpartum <1 month
            pregnancy_loss_history: Unexplained stillborn, recurrent spontaneous abortion (≥3),
                                    premature birth with toxemia or growth-restricted infant

        Returns:
            ScoreResult with Caprini score, VTE risk level, and prophylaxis recommendations
        """
        score = 0
        components = {}

        # Age scoring
        if age_years >= 75:
            score += 3
            components["Age ≥75 years"] = 3
        elif age_years >= 61:
            score += 2
            components["Age 61-74 years"] = 2
        elif age_years >= 41:
            score += 1
            components["Age 41-60 years"] = 1
        else:
            components["Age ≤40 years"] = 0

        # 1-point factors
        if minor_surgery:
            score += 1
            components["Minor surgery planned"] = 1
        if prior_major_surgery_lt_1mo:
            score += 1
            components["Prior major surgery <1 month"] = 1
        if varicose_veins:
            score += 1
            components["Varicose veins"] = 1
        if inflammatory_bowel_disease:
            score += 1
            components["Inflammatory bowel disease"] = 1
        if swollen_legs:
            score += 1
            components["Swollen legs (current)"] = 1
        if obesity_bmi_gt_25:
            score += 1
            components["Obesity (BMI >25)"] = 1
        if acute_mi:
            score += 1
            components["Acute MI"] = 1
        if chf_lt_1mo:
            score += 1
            components["CHF <1 month"] = 1
        if sepsis_lt_1mo:
            score += 1
            components["Sepsis <1 month"] = 1
        if lung_disease:
            score += 1
            components["Serious lung disease/pneumonia <1 mo"] = 1
        if copd:
            score += 1
            components["COPD/abnormal pulmonary function"] = 1
        if bed_rest_medical:
            score += 1
            components["Medical patient at bed rest"] = 1
        if leg_cast_or_brace:
            score += 1
            components["Leg plaster cast or brace"] = 1
        if central_venous_access:
            score += 1
            components["Central venous access"] = 1

        # 2-point factors
        if arthroscopic_surgery:
            score += 2
            components["Arthroscopic surgery"] = 2
        if major_surgery:
            score += 2
            components["Major surgery (>45 min)"] = 2
        if laparoscopic_surgery_gt_45min:
            score += 2
            components["Laparoscopic surgery >45 min"] = 2
        if malignancy:
            score += 2
            components["Malignancy (present or previous)"] = 2
        if bed_confined_gt_72hr:
            score += 2
            components["Confined to bed >72 hours"] = 2
        if immobilizing_cast_lt_1mo:
            score += 2
            components["Immobilizing plaster cast <1 month"] = 2

        # 3-point factors
        if history_dvt_pe:
            score += 3
            components["History of DVT/PE"] = 3
        if family_history_thrombosis:
            score += 3
            components["Family history of thrombosis"] = 3
        if factor_v_leiden:
            score += 3
            components["Factor V Leiden positive"] = 3
        if prothrombin_20210a:
            score += 3
            components["Prothrombin 20210A positive"] = 3
        if elevated_homocysteine:
            score += 3
            components["Elevated serum homocysteine"] = 3
        if lupus_anticoagulant:
            score += 3
            components["Lupus anticoagulant positive"] = 3
        if anticardiolipin_antibodies:
            score += 3
            components["Anticardiolipin antibodies elevated"] = 3
        if hit_history:
            score += 3
            components["Heparin-induced thrombocytopenia history"] = 3
        if other_thrombophilia:
            score += 3
            components["Other thrombophilia"] = 3

        # 5-point factors
        if stroke_lt_1mo:
            score += 5
            components["Stroke <1 month"] = 5
        if elective_arthroplasty:
            score += 5
            components["Elective arthroplasty"] = 5
        if hip_pelvis_leg_fracture_lt_1mo:
            score += 5
            components["Hip/pelvis/leg fracture <1 month"] = 5
        if spinal_cord_injury_lt_1mo:
            score += 5
            components["Acute spinal cord injury <1 month"] = 5

        # Female-specific factors (only if female)
        if female:
            if oral_contraceptives_or_hrt:
                score += 1
                components["Oral contraceptives or HRT"] = 1
            if pregnancy_or_postpartum:
                score += 1
                components["Pregnancy or postpartum <1 month"] = 1
            if pregnancy_loss_history:
                score += 1
                components["Pregnancy loss history"] = 1

        # Generate interpretation
        interpretation = self._interpret_score(score, hit_history)

        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            calculation_details=components,
            references=list(self.references),
        )

    def _interpret_score(self, score: int, hit_history: bool) -> Interpretation:
        """Generate interpretation based on Caprini score"""

        if score == 0:
            severity = Severity.NORMAL
            risk_level = RiskLevel.VERY_LOW
            vte_rate = "~0.5%"
            category = "Very Low Risk"
            recommendations = [
                "Early ambulation",
                "No specific prophylaxis typically required",
            ]
            prophylaxis = "No pharmacologic prophylaxis indicated"
            duration = "N/A"

        elif score <= 2:
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            vte_rate = "~1.5%"
            category = "Low Risk"
            recommendations = [
                "Mechanical prophylaxis (SCDs or graduated compression stockings)",
                "Early ambulation",
            ]
            prophylaxis = "Mechanical prophylaxis recommended"
            duration = "Until ambulatory"

        elif score <= 4:
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            vte_rate = "~3%"
            category = "Moderate Risk"
            recommendations = [
                "Pharmacologic prophylaxis: LMWH, UFH, or fondaparinux",
                "OR mechanical prophylaxis if bleeding risk is high",
                "Early ambulation",
            ]
            prophylaxis = "LMWH (e.g., enoxaparin 40 mg SC daily) OR UFH 5000 units SC q8-12h"
            duration = "Until ambulatory or discharge"

        else:  # score >= 5
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            vte_rate = "~6%"
            category = "High Risk"
            recommendations = [
                "Pharmacologic prophylaxis: LMWH, UFH, or fondaparinux",
                "PLUS mechanical prophylaxis (SCDs)",
                "Consider extended prophylaxis (up to 4 weeks post-op)",
            ]
            prophylaxis = "LMWH (e.g., enoxaparin 40 mg SC daily) + mechanical prophylaxis"
            duration = "Continue 7-10 days minimum; consider 28 days for major orthopedic/cancer surgery"

        # Special considerations for HIT history
        if hit_history:
            recommendations.append("AVOID heparin products - use fondaparinux or direct oral anticoagulants")

        summary = f"Caprini = {score}: {category} (VTE rate {vte_rate})"
        detail = (
            f"Based on the Caprini VTE Risk Assessment, this patient has a {risk_level} risk "
            f"of developing venous thromboembolism with an estimated VTE rate of {vte_rate}."
        )

        next_steps = [
            f"Prophylaxis: {prophylaxis}",
            f"Duration: {duration}",
            "Reassess risk daily and with any change in clinical status",
            "Ensure adequate hydration and early mobilization",
        ]

        warnings: tuple[str, ...] = tuple()
        if score >= 5:
            warnings = (
                "High VTE risk - ensure both pharmacologic AND mechanical prophylaxis",
                "Consider extended prophylaxis for major surgery",
            )
        if hit_history:
            warnings = warnings + ("History of HIT - AVOID all heparin products",)

        return Interpretation(
            summary=summary,
            severity=severity,
            detail=detail,
            stage=f"Caprini Score = {score}",
            stage_description=category,
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
            warnings=warnings,
        )
