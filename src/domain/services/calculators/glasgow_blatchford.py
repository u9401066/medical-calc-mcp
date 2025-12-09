"""
Glasgow-Blatchford Score (GBS) Calculator

上消化道出血風險分層工具，預測是否需要內視鏡干預或輸血。
ESGE 指引推薦作為 UGIB 首選評估工具。

References:
- Blatchford O, et al. Lancet. 2000;356(9238):1318-1321. PMID: 11073021
- ESGE Guideline. Endoscopy. 2021;53(3):300-332. PMID: 33567467
"""

from ..base import BaseCalculator
from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity, RiskLevel
from ...value_objects.reference import Reference
from ...value_objects.units import Unit
from ...value_objects.tool_keys import LowLevelKey, HighLevelKey, Specialty, ClinicalContext


class GlasgowBlatchfordCalculator(BaseCalculator):
    """
    Glasgow-Blatchford Score (GBS) for Upper GI Bleeding
    
    上消化道出血風險評估工具，預測需要干預（輸血、內視鏡、手術）的風險。
    GBS = 0 表示低風險，可考慮門診處理。
    
    評分範圍: 0-23 分
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="glasgow_blatchford",
                name="Glasgow-Blatchford Score (GBS)",
                purpose="Stratify upper GI bleeding risk and predict need for intervention",
                input_params=(
                    "bun_mg_dl", "hemoglobin_g_dl", "systolic_bp_mmhg", 
                    "heart_rate_bpm", "melena", "syncope", 
                    "hepatic_disease", "cardiac_failure", "sex"
                ),
                output_type="GBS (0-23) with intervention risk and disposition"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.GASTROENTEROLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                ),
                conditions=(
                    "Upper GI Bleeding", "UGIB", "Hematemesis", 
                    "Melena", "GI Hemorrhage"
                ),
                clinical_contexts=(
                    ClinicalContext.EMERGENCY,
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.DISPOSITION,
                    ClinicalContext.RISK_STRATIFICATION,
                ),
                clinical_questions=(
                    "Does this UGIB patient need urgent endoscopy?",
                    "Can this GI bleed patient be managed as outpatient?",
                    "What is the risk of needing intervention for this GI bleed?",
                    "Is this patient at low risk for upper GI bleeding?",
                ),
                icd10_codes=("K92.0", "K92.1", "K92.2"),
                keywords=(
                    "Glasgow-Blatchford", "GBS", "upper GI bleeding", "UGIB",
                    "hematemesis", "melena", "GI hemorrhage", "endoscopy",
                    "transfusion", "intervention risk"
                )
            ),
            references=(
                Reference(
                    citation="Blatchford O, Murray WR, Blatchford M. A risk score to predict need for treatment for upper-gastrointestinal haemorrhage. Lancet. 2000;356(9238):1318-1321.",
                    doi="10.1016/S0140-6736(00)02816-6",
                    pmid="11073021",
                    year=2000
                ),
                Reference(
                    citation="Gralnek IM, Stanley AJ, Morris AJ, et al. Endoscopic diagnosis and management of nonvariceal upper gastrointestinal hemorrhage (NVUGIH): European Society of Gastrointestinal Endoscopy (ESGE) Guideline - Update 2021. Endoscopy. 2021;53(3):300-332.",
                    doi="10.1055/a-1369-5274",
                    pmid="33567467",
                    year=2021
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )
    
    def calculate(
        self,
        bun_mg_dl: float,
        hemoglobin_g_dl: float,
        systolic_bp_mmhg: int,
        sex: str,  # "male" or "female"
        heart_rate_bpm: int = 100,
        melena: bool = False,
        syncope: bool = False,
        hepatic_disease: bool = False,
        cardiac_failure: bool = False,
    ) -> ScoreResult:
        """
        Calculate Glasgow-Blatchford Score
        
        Args:
            bun_mg_dl: Blood urea nitrogen (mg/dL), range 0-150
            hemoglobin_g_dl: Hemoglobin (g/dL), range 3-20
            systolic_bp_mmhg: Systolic blood pressure (mmHg), range 50-250
            sex: Patient sex ("male" or "female")
            heart_rate_bpm: Heart rate (bpm), default 100
            melena: Presentation with melena
            syncope: Presentation with syncope
            hepatic_disease: Known hepatic disease
            cardiac_failure: Known cardiac failure
            
        Returns:
            ScoreResult with GBS score and intervention risk
        """
        # Validate inputs
        if not 0 <= bun_mg_dl <= 150:
            raise ValueError("BUN must be between 0-150 mg/dL")
        if not 3 <= hemoglobin_g_dl <= 20:
            raise ValueError("Hemoglobin must be between 3-20 g/dL")
        if not 50 <= systolic_bp_mmhg <= 250:
            raise ValueError("Systolic BP must be between 50-250 mmHg")
        if sex.lower() not in ["male", "female"]:
            raise ValueError("Sex must be 'male' or 'female'")
        
        score = 0
        components = []
        
        # BUN scoring (mg/dL) - convert if needed
        # Score: 0 (<18.2), 2 (18.2-22.3), 3 (22.4-27.9), 4 (28-69.9), 6 (≥70)
        if bun_mg_dl >= 70:
            score += 6
            components.append("BUN ≥70: +6")
        elif bun_mg_dl >= 28:
            score += 4
            components.append("BUN 28-69.9: +4")
        elif bun_mg_dl >= 22.4:
            score += 3
            components.append("BUN 22.4-27.9: +3")
        elif bun_mg_dl >= 18.2:
            score += 2
            components.append("BUN 18.2-22.3: +2")
        else:
            components.append("BUN <18.2: +0")
        
        # Hemoglobin scoring
        is_male = sex.lower() == "male"
        if is_male:
            # Male: <10 (+6), 10-11.9 (+3), 12-12.9 (+1), ≥13 (+0)
            if hemoglobin_g_dl < 10:
                score += 6
                components.append("Hgb <10 (male): +6")
            elif hemoglobin_g_dl < 12:
                score += 3
                components.append("Hgb 10-11.9 (male): +3")
            elif hemoglobin_g_dl < 13:
                score += 1
                components.append("Hgb 12-12.9 (male): +1")
            else:
                components.append("Hgb ≥13 (male): +0")
        else:
            # Female: <10 (+6), 10-11.9 (+1), ≥12 (+0)
            if hemoglobin_g_dl < 10:
                score += 6
                components.append("Hgb <10 (female): +6")
            elif hemoglobin_g_dl < 12:
                score += 1
                components.append("Hgb 10-11.9 (female): +1")
            else:
                components.append("Hgb ≥12 (female): +0")
        
        # Systolic BP scoring
        # <90 (+3), 90-99 (+2), 100-109 (+1), ≥110 (+0)
        if systolic_bp_mmhg < 90:
            score += 3
            components.append("SBP <90: +3")
        elif systolic_bp_mmhg < 100:
            score += 2
            components.append("SBP 90-99: +2")
        elif systolic_bp_mmhg < 110:
            score += 1
            components.append("SBP 100-109: +1")
        else:
            components.append("SBP ≥110: +0")
        
        # Heart rate (Pulse ≥100 = +1)
        if heart_rate_bpm >= 100:
            score += 1
            components.append("HR ≥100: +1")
        else:
            components.append("HR <100: +0")
        
        # Melena (+1)
        if melena:
            score += 1
            components.append("Melena: +1")
        
        # Syncope (+2)
        if syncope:
            score += 2
            components.append("Syncope: +2")
        
        # Hepatic disease (+2)
        if hepatic_disease:
            score += 2
            components.append("Hepatic disease: +2")
        
        # Cardiac failure (+2)
        if cardiac_failure:
            score += 2
            components.append("Cardiac failure: +2")
        
        # Risk stratification
        if score == 0:
            risk_category = "Very Low Risk"
            intervention_risk = "<1%"
            disposition = "Consider outpatient management"
            interpretation = Interpretation(
                summary=f"GBS {score}/23: Very Low Risk - Outpatient management possible",
                detail=(
                    "GBS = 0 identifies patients at very low risk for needing intervention. "
                    "ESGE recommends these patients may be suitable for outpatient management. "
                    "No urgent endoscopy required."
                ),
                severity=Severity.NORMAL,
                risk_level=RiskLevel.VERY_LOW,
                stage="Very Low Risk",
                stage_description="GBS = 0",
                recommendations=(
                    "Consider outpatient management if social support adequate",
                    "No urgent endoscopy required",
                    "Ensure follow-up arranged within 24-48 hours",
                ),
                next_steps=(
                    "Arrange outpatient endoscopy if indicated",
                    "Provide patient with warning signs for return",
                    "Ensure PPI therapy if appropriate",
                ),
            )
        elif score <= 1:
            risk_category = "Low Risk"
            intervention_risk = "~1%"
            disposition = "May consider early discharge with close follow-up"
            interpretation = Interpretation(
                summary=f"GBS {score}/23: Low Risk - Early discharge possible",
                detail=(
                    "Low risk for needing intervention. "
                    "Consider early discharge with outpatient follow-up."
                ),
                severity=Severity.NORMAL,
                risk_level=RiskLevel.LOW,
                stage="Low Risk",
                stage_description="GBS 1",
                recommendations=(
                    "Consider early discharge with close follow-up",
                    "Outpatient endoscopy within 24-48 hours",
                ),
                next_steps=(
                    "Arrange outpatient follow-up",
                    "Provide return precautions",
                ),
            )
        elif score <= 5:
            risk_category = "Intermediate Risk"
            intervention_risk = "~10-15%"
            disposition = "Admission recommended, endoscopy within 24h"
            interpretation = Interpretation(
                summary=f"GBS {score}/23: Intermediate Risk - Admission recommended",
                detail=(
                    "Intermediate risk for needing intervention. "
                    "Recommend hospital admission. "
                    "Endoscopy should be performed within 24 hours."
                ),
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Intermediate Risk",
                stage_description=f"GBS {score}",
                recommendations=(
                    "Hospital admission recommended",
                    "Endoscopy within 24 hours",
                    "IV PPI therapy",
                    "Resuscitation as needed",
                ),
                warnings=(
                    "Monitor for clinical deterioration",
                    "Reassess if hemodynamically unstable",
                ),
                next_steps=(
                    "Arrange inpatient endoscopy",
                    "Continue IV access and monitoring",
                    "Type and screen blood products",
                ),
            )
        elif score <= 11:
            risk_category = "High Risk"
            intervention_risk = "~25-40%"
            disposition = "Urgent admission, early endoscopy (<12h)"
            interpretation = Interpretation(
                summary=f"GBS {score}/23: High Risk - Early endoscopy indicated",
                detail=(
                    "High risk for needing intervention (transfusion, endoscopy, surgery). "
                    "Urgent hospital admission required. "
                    "Early endoscopy recommended (<12 hours)."
                ),
                severity=Severity.SEVERE,
                risk_level=RiskLevel.HIGH,
                stage="High Risk",
                stage_description=f"GBS {score}",
                recommendations=(
                    "Urgent hospital admission",
                    "Early endoscopy (<12 hours)",
                    "Active resuscitation",
                    "Consider ICU monitoring",
                    "Type and crossmatch blood products",
                ),
                warnings=(
                    "High risk for transfusion requirement",
                    "Monitor for hemodynamic instability",
                    "Surgical consultation may be needed",
                ),
                next_steps=(
                    "Arrange urgent endoscopy",
                    "Transfuse if indicated",
                    "Consider ICU admission",
                ),
            )
        else:
            risk_category = "Very High Risk"
            intervention_risk = ">50%"
            disposition = "ICU admission, emergent endoscopy"
            interpretation = Interpretation(
                summary=f"GBS {score}/23: Very High Risk - Emergent intervention needed",
                detail=(
                    "Very high risk for needing intervention and adverse outcomes. "
                    "Consider ICU admission. "
                    "Emergent endoscopy indicated."
                ),
                severity=Severity.CRITICAL,
                risk_level=RiskLevel.VERY_HIGH,
                stage="Very High Risk",
                stage_description=f"GBS {score}",
                recommendations=(
                    "ICU admission recommended",
                    "Emergent endoscopy",
                    "Massive transfusion protocol if needed",
                    "Surgical and IR standby",
                ),
                warnings=(
                    "High mortality risk",
                    "Prepare for massive transfusion",
                    "Consider surgical intervention",
                ),
                next_steps=(
                    "Emergent endoscopy",
                    "Aggressive resuscitation",
                    "Surgical/IR consultation",
                ),
            )
        
        return ScoreResult(
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs={
                "bun_mg_dl": bun_mg_dl,
                "hemoglobin_g_dl": hemoglobin_g_dl,
                "systolic_bp_mmhg": systolic_bp_mmhg,
                "sex": sex,
                "heart_rate_bpm": heart_rate_bpm,
                "melena": melena,
                "syncope": syncope,
                "hepatic_disease": hepatic_disease,
                "cardiac_failure": cardiac_failure,
            },
            calculation_details={
                "score_name": "Glasgow-Blatchford Score (GBS)",
                "score_range": "0-23",
                "risk_category": risk_category,
                "intervention_risk": intervention_risk,
                "disposition": disposition,
                "components": components,
            },
            formula_used="GBS = sum of BUN + Hemoglobin + SBP + HR + clinical factors",
            notes=[
                "GBS = 0 is the key threshold for identifying very low-risk patients",
                "For GBS ≥1, arrange endoscopy; for GBS = 0, may consider outpatient management"
            ],
        )
