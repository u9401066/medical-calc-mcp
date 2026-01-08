"""
AIMS65 Score Calculator

上消化道出血死亡率預測工具，使用5個簡單指標。
適用於急診快速風險分層。

References:
- Saltzman JR, et al. Gastrointest Endosc. 2011;74(6):1215-1224. PMID: 21907980
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class AIMS65Calculator(BaseCalculator):
    """
    AIMS65 Score for Upper GI Bleeding Mortality

    簡便的上消化道出血死亡率預測工具，僅需 5 項臨床指標。
    命名來自五項指標的首字母: Albumin, INR, Mental status, SBP, age ≥65

    評分範圍: 0-5 分
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="aims65",
                name="AIMS65 Score",
                purpose="Predict in-hospital mortality for upper GI bleeding",
                input_params=["albumin_lt_3", "inr_gt_1_5", "altered_mental_status", "sbp_lte_90", "age_gte_65"],
                output_type="AIMS65 Score (0-5) with mortality risk",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.GASTROENTEROLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                ),
                conditions=("Upper GI Bleeding", "UGIB", "Hematemesis", "Melena", "GI Hemorrhage"),
                clinical_contexts=(
                    ClinicalContext.EMERGENCY,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.DISPOSITION,
                ),
                clinical_questions=(
                    "What is the mortality risk for this UGIB patient?",
                    "Should this GI bleed patient go to ICU?",
                    "How severe is this upper GI bleeding?",
                ),
                icd10_codes=("K92.0", "K92.1", "K92.2"),
                keywords=("AIMS65", "upper GI bleeding", "UGIB mortality", "hematemesis", "melena", "GI hemorrhage", "in-hospital mortality", "prognosis"),
            ),
            references=(
                Reference(
                    citation="Saltzman JR, Tabak YP, Hyett BH, et al. A simple risk score accurately predicts in-hospital mortality, length of stay, and cost in acute upper GI bleeding. Gastrointest Endosc. 2011;74(6):1215-1224.",
                    doi="10.1016/j.gie.2011.06.024",
                    pmid="21907980",
                    year=2011,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        albumin_lt_3: bool,
        inr_gt_1_5: bool,
        altered_mental_status: bool,
        sbp_lte_90: bool,
        age_gte_65: bool,
    ) -> ScoreResult:
        """
        Calculate AIMS65 Score

        Args:
            albumin_lt_3: Albumin <3.0 g/dL
            inr_gt_1_5: INR >1.5
            altered_mental_status: GCS <14 or disorientation/lethargy/stupor/coma
            sbp_lte_90: Systolic BP ≤90 mmHg
            age_gte_65: Age ≥65 years

        Returns:
            ScoreResult with AIMS65 score and mortality risk
        """
        score = 0
        components = []

        # A - Albumin <3.0 g/dL (+1)
        if albumin_lt_3:
            score += 1
            components.append("Albumin <3.0 g/dL: +1")
        else:
            components.append("Albumin ≥3.0 g/dL: +0")

        # I - INR >1.5 (+1)
        if inr_gt_1_5:
            score += 1
            components.append("INR >1.5: +1")
        else:
            components.append("INR ≤1.5: +0")

        # M - Altered Mental status (+1)
        if altered_mental_status:
            score += 1
            components.append("Altered mental status: +1")
        else:
            components.append("Normal mental status: +0")

        # S - Systolic BP ≤90 mmHg (+1)
        if sbp_lte_90:
            score += 1
            components.append("SBP ≤90 mmHg: +1")
        else:
            components.append("SBP >90 mmHg: +0")

        # 65 - Age ≥65 (+1)
        if age_gte_65:
            score += 1
            components.append("Age ≥65: +1")
        else:
            components.append("Age <65: +0")

        # Mortality risk based on original study
        mortality_rates = {
            0: ("0.3%", "Very Low"),
            1: ("1.2%", "Low"),
            2: ("5.3%", "Intermediate"),
            3: ("10.3%", "High"),
            4: ("16.5%", "Very High"),
            5: ("24.5%", "Critical"),
        }

        mortality_risk, risk_category = mortality_rates[score]

        # Interpretation and recommendations
        if score == 0:
            interpretation = Interpretation(
                summary=f"AIMS65 {score}/5: Very Low Risk - Mortality {mortality_risk}",
                detail=(
                    "AIMS65 = 0: Very low in-hospital mortality risk. Standard ward admission typically appropriate. Consider early endoscopy within 24 hours."
                ),
                severity=Severity.NORMAL,
                risk_level=RiskLevel.VERY_LOW,
                stage="Very Low Risk",
                stage_description="AIMS65 = 0",
                recommendations=(
                    "Standard ward admission appropriate",
                    "Endoscopy within 24 hours",
                    "Standard resuscitation",
                ),
                next_steps=(
                    "Arrange endoscopy within 24h",
                    "Monitor vital signs",
                    "Serial hemoglobin if needed",
                ),
            )
            disposition = "Low mortality risk, standard care"
        elif score == 1:
            interpretation = Interpretation(
                summary=f"AIMS65 {score}/5: Low Risk - Mortality {mortality_risk}",
                detail=("AIMS65 = 1: Low in-hospital mortality risk. Standard monitoring appropriate. Endoscopy within 24 hours recommended."),
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="Low Risk",
                stage_description="AIMS65 = 1",
                recommendations=(
                    "Standard monitoring appropriate",
                    "Endoscopy within 24 hours",
                    "IV access and resuscitation",
                ),
                next_steps=(
                    "Arrange endoscopy within 24h",
                    "Monitor clinical status",
                ),
            )
            disposition = "Low risk, standard care with monitoring"
        elif score == 2:
            interpretation = Interpretation(
                summary=f"AIMS65 {score}/5: Intermediate Risk - Mortality {mortality_risk}",
                detail=("AIMS65 = 2: Intermediate mortality risk. Close monitoring recommended. Consider early endoscopy (<12-24 hours)."),
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Intermediate Risk",
                stage_description="AIMS65 = 2",
                recommendations=(
                    "Close monitoring recommended",
                    "Early endoscopy (<12-24 hours)",
                    "Type and screen blood products",
                ),
                warnings=(
                    "Monitor for clinical deterioration",
                    "Be prepared to escalate care",
                ),
                next_steps=(
                    "Arrange early endoscopy",
                    "Close monitoring",
                    "Consider step-down unit",
                ),
            )
            disposition = "Intermediate risk, close monitoring"
        elif score == 3:
            interpretation = Interpretation(
                summary=f"AIMS65 {score}/5: High Risk - Mortality {mortality_risk}",
                detail=("AIMS65 = 3: High mortality risk. ICU or step-down unit consideration. Urgent endoscopy recommended (<12 hours)."),
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage="High Risk",
                stage_description="AIMS65 = 3",
                recommendations=(
                    "ICU or step-down unit consideration",
                    "Urgent endoscopy (<12 hours)",
                    "Aggressive resuscitation",
                    "Type and crossmatch blood products",
                ),
                warnings=(
                    "High mortality risk",
                    "Monitor for hemodynamic instability",
                ),
                next_steps=(
                    "Arrange urgent endoscopy",
                    "Consider ICU admission",
                    "Prepare for transfusion",
                ),
            )
            disposition = "High risk, consider ICU admission"
        else:  # score >= 4
            interpretation = Interpretation(
                summary=f"AIMS65 {score}/5: Critical Risk - Mortality {mortality_risk}",
                detail=(
                    f"AIMS65 = {score}: Very high/critical mortality risk. ICU admission strongly recommended. Emergent endoscopy and aggressive resuscitation."
                ),
                severity=Severity.CRITICAL,
                risk_level=RiskLevel.VERY_HIGH,
                stage="Critical Risk",
                stage_description=f"AIMS65 = {score}",
                recommendations=(
                    "ICU admission strongly recommended",
                    "Emergent endoscopy",
                    "Aggressive resuscitation",
                    "Massive transfusion protocol if needed",
                    "Surgical/IR consultation",
                ),
                warnings=(
                    "Very high mortality risk",
                    "Prepare for massive transfusion",
                    "Consider surgical intervention",
                ),
                next_steps=(
                    "Emergent endoscopy",
                    "ICU admission",
                    "Surgical consultation",
                ),
            )
            disposition = "Very high risk, ICU admission recommended"

        return ScoreResult(
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs={
                "albumin_lt_3": albumin_lt_3,
                "inr_gt_1_5": inr_gt_1_5,
                "altered_mental_status": altered_mental_status,
                "sbp_lte_90": sbp_lte_90,
                "age_gte_65": age_gte_65,
            },
            calculation_details={
                "score_name": "AIMS65 Score",
                "score_range": "0-5",
                "in_hospital_mortality": mortality_risk,
                "risk_category": risk_category,
                "disposition": disposition,
                "components": components,
                "acronym_meaning": "A=Albumin<3, I=INR>1.5, M=Mental status, S=SBP≤90, 65=Age≥65",
            },
            formula_used="AIMS65 = sum of 5 binary criteria",
            notes=[
                "AIMS65 predicts mortality; use GBS for intervention risk",
                f"Consider {'ICU admission and emergent endoscopy' if score >= 3 else 'endoscopy within 24h'}",
            ],
        )
