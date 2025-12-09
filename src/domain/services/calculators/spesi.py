"""
Simplified Pulmonary Embolism Severity Index (sPESI) Calculator

簡化版肺栓塞嚴重度指數，用於評估急性肺栓塞30天死亡風險。
比原始 PESI 更簡單，僅需6個臨床變數。

References:
- Jiménez D, et al. Arch Intern Med. 2010;170(15):1383-1389. PMID: 20696966
- ESC 2019 Guidelines on PE. Eur Heart J. 2020;41(4):543-603. PMID: 31504429
"""

from typing import Optional
from ..base import BaseCalculator
from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity, RiskLevel
from ...value_objects.reference import Reference
from ...value_objects.units import Unit
from ...value_objects.tool_keys import LowLevelKey, HighLevelKey, Specialty, ClinicalContext


class SimplifiedPESICalculator(BaseCalculator):
    """
    Simplified Pulmonary Embolism Severity Index (sPESI) Calculator
    
    Stratifies PE patients into low-risk vs high-risk categories
    for 30-day mortality prediction.
    
    6 criteria (each = 1 point):
    - Age >80 years
    - Cancer history
    - Chronic cardiopulmonary disease
    - Heart rate ≥110 bpm
    - SBP <100 mmHg
    - SpO₂ <90%
    
    Score 0 = Low risk (30-day mortality ~1%)
    Score ≥1 = High risk (30-day mortality ~10.9%)
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="spesi",
                name="Simplified Pulmonary Embolism Severity Index (sPESI)",
                purpose="Risk stratify acute PE patients for 30-day mortality",
                input_params=(
                    "age", "cancer", "chronic_cardiopulmonary_disease",
                    "heart_rate", "systolic_bp", "spo2"
                ),
                output_type="sPESI (0 or ≥1) with risk classification"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.PULMONOLOGY,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.CARDIOLOGY,
                ),
                conditions=(
                    "Pulmonary Embolism", "PE", "VTE",
                    "Venous Thromboembolism"
                ),
                clinical_contexts=(
                    ClinicalContext.EMERGENCY,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.DISPOSITION,
                ),
                clinical_questions=(
                    "Can this PE patient be treated as outpatient?",
                    "What is the 30-day mortality risk for this PE?",
                    "Is this a low-risk or high-risk PE?",
                    "Does this PE patient need ICU admission?",
                ),
                icd10_codes=("I26.9", "I26.0"),
                keywords=(
                    "sPESI", "PESI", "pulmonary embolism severity",
                    "PE risk stratification", "PE prognosis",
                    "outpatient PE treatment", "PE mortality"
                )
            ),
            references=(
                Reference(
                    citation="Jiménez D, Aujesky D, Moores L, et al. Simplification of the pulmonary embolism severity index for prognostication in patients with acute symptomatic pulmonary embolism. Arch Intern Med. 2010;170(15):1383-1389.",
                    pmid="20696966",
                    year=2010
                ),
                Reference(
                    citation="Konstantinides SV, Meyer G, Becattini C, et al. 2019 ESC Guidelines for the diagnosis and management of acute pulmonary embolism. Eur Heart J. 2020;41(4):543-603.",
                    pmid="31504429",
                    year=2020
                ),
            ),
            version="1.0.0",
            validation_status="validated"
        )
    
    def calculate(
        self,
        age: int,
        cancer: bool = False,
        chronic_cardiopulmonary_disease: bool = False,
        heart_rate: Optional[int] = None,
        systolic_bp: Optional[int] = None,
        spo2: Optional[float] = None,
        # Alternative parameter names
        heart_rate_gte_110: Optional[bool] = None,
        sbp_lt_100: Optional[bool] = None,
        spo2_lt_90: Optional[bool] = None,
    ) -> ScoreResult:
        """
        Calculate Simplified PESI Score
        
        Args:
            age: Patient age in years
            cancer: Active cancer or cancer within past year
            chronic_cardiopulmonary_disease: Chronic heart failure or chronic lung disease
            heart_rate: Heart rate in bpm (optional if heart_rate_gte_110 provided)
            systolic_bp: Systolic BP in mmHg (optional if sbp_lt_100 provided)
            spo2: Oxygen saturation % (optional if spo2_lt_90 provided)
            
        Alternative (direct criteria):
            heart_rate_gte_110: Heart rate ≥110 bpm
            sbp_lt_100: Systolic BP <100 mmHg
            spo2_lt_90: SpO₂ <90%
            
        Returns:
            ScoreResult with risk classification
        """
        # Validate age
        if not 18 <= age <= 120:
            raise ValueError("Age must be between 18-120 years")
        
        # Calculate criteria
        score = 0
        components = []
        
        # 1. Age >80 years
        age_criteria = age > 80
        if age_criteria:
            score += 1
            components.append(f"Age >80: Yes ({age} years) +1")
        else:
            components.append(f"Age >80: No ({age} years) +0")
        
        # 2. Cancer
        if cancer:
            score += 1
            components.append("Cancer history: Yes +1")
        else:
            components.append("Cancer history: No +0")
        
        # 3. Chronic cardiopulmonary disease
        if chronic_cardiopulmonary_disease:
            score += 1
            components.append("Chronic cardiopulmonary disease: Yes +1")
        else:
            components.append("Chronic cardiopulmonary disease: No +0")
        
        # 4. Heart rate ≥110 bpm
        if heart_rate_gte_110 is not None:
            hr_criteria = heart_rate_gte_110
        elif heart_rate is not None:
            if not 30 <= heart_rate <= 250:
                raise ValueError("Heart rate must be between 30-250 bpm")
            hr_criteria = heart_rate >= 110
        else:
            hr_criteria = False  # Assume normal if not provided
            
        if hr_criteria:
            score += 1
            hr_text = f" ({heart_rate} bpm)" if heart_rate else ""
            components.append(f"Heart rate ≥110: Yes{hr_text} +1")
        else:
            hr_text = f" ({heart_rate} bpm)" if heart_rate else ""
            components.append(f"Heart rate ≥110: No{hr_text} +0")
        
        # 5. Systolic BP <100 mmHg
        if sbp_lt_100 is not None:
            sbp_criteria = sbp_lt_100
        elif systolic_bp is not None:
            if not 50 <= systolic_bp <= 250:
                raise ValueError("Systolic BP must be between 50-250 mmHg")
            sbp_criteria = systolic_bp < 100
        else:
            sbp_criteria = False  # Assume normal if not provided
            
        if sbp_criteria:
            score += 1
            sbp_text = f" ({systolic_bp} mmHg)" if systolic_bp else ""
            components.append(f"SBP <100: Yes{sbp_text} +1")
        else:
            sbp_text = f" ({systolic_bp} mmHg)" if systolic_bp else ""
            components.append(f"SBP <100: No{sbp_text} +0")
        
        # 6. SpO₂ <90%
        if spo2_lt_90 is not None:
            spo2_criteria = spo2_lt_90
        elif spo2 is not None:
            if not 50 <= spo2 <= 100:
                raise ValueError("SpO2 must be between 50-100%")
            spo2_criteria = spo2 < 90
        else:
            spo2_criteria = False  # Assume normal if not provided
            
        if spo2_criteria:
            score += 1
            spo2_text = f" ({spo2}%)" if spo2 else ""
            components.append(f"SpO₂ <90%: Yes{spo2_text} +1")
        else:
            spo2_text = f" ({spo2}%)" if spo2 else ""
            components.append(f"SpO₂ <90%: No{spo2_text} +0")
        
        components.append(f"Total sPESI Score: {score}")
        
        # Risk stratification
        if score == 0:
            risk_category = "Low Risk"
            mortality_30d = "1.0-1.5%"
            outpatient_candidate = True
            interpretation = Interpretation(
                summary=f"sPESI {score}: Low Risk PE - Outpatient treatment possible",
                detail=(
                    f"sPESI = 0: Low risk for 30-day mortality (~1%). "
                    "May be candidate for outpatient treatment if other criteria met."
                ),
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="Low Risk PE",
                stage_description="sPESI = 0",
                recommendations=(
                    "Consider outpatient treatment if appropriate",
                    "No need for supplemental O₂",
                    "Pain adequately controlled",
                    "Low bleeding risk",
                    "Good social support/compliance",
                    "Follow-up available within 48-72h",
                ),
                next_steps=(
                    "Assess outpatient eligibility",
                    "Start anticoagulation",
                    "Arrange close follow-up",
                ),
            )
        else:
            risk_category = "High Risk"
            mortality_30d = "10.9% (8.5-13.2%)"
            outpatient_candidate = False
            
            if score == 1:
                interpretation = Interpretation(
                    summary=f"sPESI {score}: Not Low Risk PE - Hospital admission",
                    detail=(
                        f"sPESI = {score}: Not low risk, hospital admission recommended. "
                        "Perform echo and troponin for further risk stratification."
                    ),
                    severity=Severity.MODERATE,
                    risk_level=RiskLevel.INTERMEDIATE,
                    stage="Intermediate Risk PE",
                    stage_description=f"sPESI = {score}",
                    recommendations=(
                        "Hospital admission recommended",
                        "Echo and cardiac biomarkers for risk stratification",
                        "Start anticoagulation",
                        "Monitor for deterioration",
                    ),
                    warnings=(
                        "Not suitable for outpatient management",
                        "Assess for RV dysfunction",
                    ),
                    next_steps=(
                        "Obtain echocardiogram",
                        "Check troponin",
                        "Reassess risk category",
                    ),
                )
            elif score == 2:
                interpretation = Interpretation(
                    summary=f"sPESI {score}: Intermediate-High Risk PE",
                    detail=(
                        f"sPESI = {score}: Intermediate-high risk, hospital admission required. "
                        "Assess RV dysfunction and troponin for complete stratification."
                    ),
                    severity=Severity.SEVERE,
                    risk_level=RiskLevel.HIGH,
                    stage="Intermediate-High Risk PE",
                    stage_description=f"sPESI = {score}",
                    recommendations=(
                        "Hospital admission required",
                        "RV assessment (echo/CT)",
                        "Troponin monitoring",
                        "Close monitoring for hemodynamic deterioration",
                    ),
                    warnings=(
                        "Significant mortality risk",
                        "Monitor for hemodynamic instability",
                    ),
                    next_steps=(
                        "Urgent echocardiogram",
                        "Serial troponins",
                        "ICU if RV dysfunction + positive troponin",
                    ),
                )
            else:
                interpretation = Interpretation(
                    summary=f"sPESI {score}: High Risk PE - ICU consideration",
                    detail=(
                        f"sPESI = {score}: High mortality risk, ICU consideration. "
                        "If hemodynamically unstable, consider reperfusion therapy."
                    ),
                    severity=Severity.CRITICAL,
                    risk_level=RiskLevel.VERY_HIGH,
                    stage="High Risk PE",
                    stage_description=f"sPESI = {score}",
                    recommendations=(
                        "Hospital admission required, consider ICU",
                        "Aggressive monitoring",
                        "If shock/hypotension: consider reperfusion",
                        "Multidisciplinary PE response team if available",
                    ),
                    warnings=(
                        "High mortality risk",
                        "Prepare for potential reperfusion therapy",
                        "Watch for hemodynamic collapse",
                    ),
                    next_steps=(
                        "ICU admission if hemodynamically unstable",
                        "Consider thrombolysis or thrombectomy if indicated",
                        "Echocardiogram urgently",
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
                "age": age,
                "cancer": cancer,
                "chronic_cardiopulmonary_disease": chronic_cardiopulmonary_disease,
                "heart_rate": heart_rate,
                "systolic_bp": systolic_bp,
                "spo2": spo2,
            },
            calculation_details={
                "score_name": "Simplified Pulmonary Embolism Severity Index (sPESI)",
                "score_range": "0-6",
                "spesi_score": score,
                "risk_category": risk_category,
                "mortality_30d": mortality_30d,
                "outpatient_candidate": outpatient_candidate,
                "criteria_met": {
                    "age_gt_80": age_criteria,
                    "cancer": cancer,
                    "chronic_cardiopulmonary": chronic_cardiopulmonary_disease,
                    "hr_gte_110": hr_criteria,
                    "sbp_lt_100": sbp_criteria,
                    "spo2_lt_90": spo2_criteria,
                },
                "components": components,
            },
            formula_used="sPESI = sum of 6 binary criteria",
            notes=[
                "Score 0 = low risk; Score ≥1 = not low risk (requires further stratification)",
                "Consider echo + troponin for intermediate risk stratification if sPESI ≥1",
                "ESC 2019 Guidelines on Pulmonary Embolism"
            ],
        )
