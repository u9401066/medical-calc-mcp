"""
EuroSCORE II Calculator

歐洲心臟手術風險評估系統 II 版。
用於預測心臟手術的院內死亡率。

References:
- Nashef SAM, et al. Eur J Cardiothorac Surg. 2012;41(4):734-745. PMID: 22378855
- Online calculator: http://euroscore.org/calc.html
"""

import math

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class EuroSCOREIICalculator(BaseCalculator):
    """
    EuroSCORE II (European System for Cardiac Operative Risk Evaluation II)

    計算心臟手術的預測死亡率。
    基於患者因素、心臟狀態和手術因素的 Logistic 回歸模型。
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="euroscore_ii",
                name="EuroSCORE II (Cardiac Surgery Risk)",
                purpose="Predict mortality risk for cardiac surgery",
                input_params=[
                    "age",
                    "gender",
                    "creatinine_clearance",
                    "extracardiac_arteriopathy",
                    "poor_mobility",
                    "previous_cardiac_surgery",
                    "chronic_lung_disease",
                    "active_endocarditis",
                    "critical_preop_state",
                    "diabetes_on_insulin",
                    "nyha_class",
                    "ccs_class_4_angina",
                    "lvef",
                    "recent_mi",
                    "pulmonary_hypertension",
                    "urgency",
                    "weight_of_intervention",
                    "surgery_on_thoracic_aorta",
                ],
                output_type="Predicted mortality (%)",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CARDIOLOGY,
                    Specialty.SURGERY,
                    Specialty.CARDIAC_ANESTHESIA,
                    Specialty.ANESTHESIOLOGY,
                    Specialty.CRITICAL_CARE,
                ),
                conditions=("Cardiac Surgery", "CABG", "Valve Surgery", "Aortic Surgery", "Heart Surgery"),
                clinical_contexts=(
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.SURGICAL_PLANNING,
                ),
                clinical_questions=(
                    "What is the surgical mortality risk for this patient?",
                    "Should we proceed with cardiac surgery?",
                    "What is the EuroSCORE II for this patient?",
                    "Is this patient high risk for cardiac surgery?",
                ),
                icd10_codes=("Z95.1", "I25.10", "I35.0", "I34.0"),
                keywords=(
                    "EuroSCORE",
                    "cardiac surgery risk",
                    "CABG risk",
                    "valve surgery risk",
                    "operative mortality",
                    "surgical risk score",
                    "heart surgery",
                ),
            ),
            references=(
                Reference(
                    citation="Nashef SAM, Roques F, Sharples LD, et al. EuroSCORE II. Eur J Cardiothorac Surg. 2012;41(4):734-745.",
                    pmid="22378855",
                    doi="10.1093/ejcts/ezs043",
                    year=2012,
                ),
                Reference(
                    citation="Roques F, Michel P, Goldstone AR, Nashef SAM. The logistic EuroSCORE. Eur Heart J. 2003;24(9):882-883.",
                    pmid="12727160",
                    year=2003,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        age: int,
        gender: str,
        creatinine_clearance: float,
        lvef: str,
        nyha_class: int,
        urgency: str,
        weight_of_intervention: str,
        extracardiac_arteriopathy: bool = False,
        poor_mobility: bool = False,
        previous_cardiac_surgery: bool = False,
        chronic_lung_disease: bool = False,
        active_endocarditis: bool = False,
        critical_preop_state: bool = False,
        diabetes_on_insulin: bool = False,
        ccs_class_4_angina: bool = False,
        recent_mi: bool = False,
        pulmonary_hypertension: str = "none",
        surgery_on_thoracic_aorta: bool = False,
    ) -> ScoreResult:
        """
        Calculate EuroSCORE II.

        Args:
            age: Patient age in years
            gender: "male" or "female"
            creatinine_clearance: CrCl in mL/min (Cockcroft-Gault)
            lvef: Left ventricular ejection fraction category
                  "good" (>50%), "moderate" (31-50%), "poor" (21-30%), "very_poor" (≤20%)
            nyha_class: NYHA functional class (1, 2, 3, or 4)
            urgency: "elective", "urgent", "emergency", or "salvage"
            weight_of_intervention: "isolated_cabg", "single_non_cabg",
                                   "two_procedures", "three_or_more"
            extracardiac_arteriopathy: Claudication, carotid stenosis >50%,
                                       previous/planned vascular surgery
            poor_mobility: Severe impairment of mobility secondary to
                          musculoskeletal or neurological dysfunction
            previous_cardiac_surgery: Previous cardiac surgery with pericardiotomy
            chronic_lung_disease: Long-term use of bronchodilators or steroids for lung
            active_endocarditis: Currently receiving antibiotics for endocarditis
            critical_preop_state: VT/VF/aborted SCD, preop CPR, preop ventilation,
                                 preop inotropes, IABP, preop renal failure
            diabetes_on_insulin: Diabetes requiring insulin therapy
            ccs_class_4_angina: CCS Class 4 angina (rest angina)
            recent_mi: MI within 90 days
            pulmonary_hypertension: "none", "moderate" (31-55 mmHg), "severe" (>55 mmHg)
            surgery_on_thoracic_aorta: Surgery involving the thoracic aorta

        Returns:
            ScoreResult with predicted mortality percentage
        """
        # Validate inputs
        if age < 0:
            raise ValueError("Age cannot be negative")
        if gender.lower() not in ["male", "female"]:
            raise ValueError("Gender must be 'male' or 'female'")
        if creatinine_clearance <= 0:
            raise ValueError("Creatinine clearance must be positive")
        if lvef.lower() not in ["good", "moderate", "poor", "very_poor"]:
            raise ValueError("LVEF must be 'good', 'moderate', 'poor', or 'very_poor'")
        if nyha_class not in [1, 2, 3, 4]:
            raise ValueError("NYHA class must be 1, 2, 3, or 4")
        if urgency.lower() not in ["elective", "urgent", "emergency", "salvage"]:
            raise ValueError("Urgency must be 'elective', 'urgent', 'emergency', or 'salvage'")
        if weight_of_intervention.lower() not in ["isolated_cabg", "single_non_cabg", "two_procedures", "three_or_more"]:
            raise ValueError("Weight of intervention must be 'isolated_cabg', 'single_non_cabg', 'two_procedures', or 'three_or_more'")
        if pulmonary_hypertension.lower() not in ["none", "moderate", "severe"]:
            raise ValueError("Pulmonary hypertension must be 'none', 'moderate', or 'severe'")

        # EuroSCORE II Coefficients (β values)
        beta_0 = -5.324537  # Intercept

        score_components: dict[str, float] = {}

        # Age (continuous, squared term)
        # Age coefficient uses a specific formula
        if age < 60:
            age_term: float = 0.0
        else:
            age_term = math.exp(0.0285181 * (age - 60))
        score_components["age"] = age_term

        # Gender (female = reference)
        female = 1 if gender.lower() == "female" else 0
        score_components["female"] = female * 0.2196434

        # Renal function (CrCl categories)
        if creatinine_clearance > 85:
            renal_term: float = 0.0  # Reference
        elif creatinine_clearance > 50:
            renal_term = 0.303553  # Moderate
        elif creatinine_clearance > 0:  # On dialysis would need separate handling
            renal_term = 0.8592256  # Severe
        else:
            renal_term = 0.6421508  # On dialysis
        score_components["renal"] = renal_term

        # Binary risk factors
        binary_coefficients = {
            "extracardiac_arteriopathy": (extracardiac_arteriopathy, 0.5360268),
            "poor_mobility": (poor_mobility, 0.2407181),
            "previous_cardiac_surgery": (previous_cardiac_surgery, 1.118599),
            "chronic_lung_disease": (chronic_lung_disease, 0.1886564),
            "active_endocarditis": (active_endocarditis, 0.6194522),
            "critical_preop_state": (critical_preop_state, 1.086517),
            "diabetes_on_insulin": (diabetes_on_insulin, 0.3542749),
            "ccs_class_4_angina": (ccs_class_4_angina, 0.2226147),
            "recent_mi": (recent_mi, 0.1253526),
        }

        for factor, (present, coef) in binary_coefficients.items():
            score_components[factor] = coef if present else 0

        # NYHA class
        nyha_coefficients = {1: 0, 2: 0.1070545, 3: 0.2958358, 4: 0.5597929}
        score_components["nyha"] = nyha_coefficients[nyha_class]

        # LVEF
        lvef_coefficients = {
            "good": 0,
            "moderate": 0.3150652,
            "poor": 0.8084096,
            "very_poor": 0.9346919,
        }
        score_components["lvef"] = lvef_coefficients[lvef.lower()]

        # Pulmonary hypertension
        ph_coefficients = {"none": 0, "moderate": 0.1788899, "severe": 0.3491475}
        score_components["pulmonary_hypertension"] = ph_coefficients[pulmonary_hypertension.lower()]

        # Urgency
        urgency_coefficients = {
            "elective": 0,
            "urgent": 0.3174673,
            "emergency": 0.7039121,
            "salvage": 1.362947,
        }
        score_components["urgency"] = urgency_coefficients[urgency.lower()]

        # Weight of intervention
        weight_coefficients = {
            "isolated_cabg": 0,
            "single_non_cabg": 0.0062118,
            "two_procedures": 0.5521478,
            "three_or_more": 0.9724533,
        }
        score_components["weight_of_intervention"] = weight_coefficients[weight_of_intervention.lower()]

        # Surgery on thoracic aorta
        score_components["thoracic_aorta"] = 0.6527205 if surgery_on_thoracic_aorta else 0

        # Calculate linear predictor (sum of all terms)
        linear_predictor = beta_0 + sum(score_components.values())

        # Calculate predicted mortality using logistic function
        predicted_mortality = math.exp(linear_predictor) / (1 + math.exp(linear_predictor))
        mortality_percent = predicted_mortality * 100

        # Risk stratification
        if mortality_percent < 1:
            risk_level = RiskLevel.VERY_LOW
            severity = Severity.NORMAL
            risk_category = "Low risk"
        elif mortality_percent < 3:
            risk_level = RiskLevel.LOW
            severity = Severity.MILD
            risk_category = "Low-moderate risk"
        elif mortality_percent < 5:
            risk_level = RiskLevel.INTERMEDIATE
            severity = Severity.MODERATE
            risk_category = "Moderate risk"
        elif mortality_percent < 10:
            risk_level = RiskLevel.HIGH
            severity = Severity.SEVERE
            risk_category = "High risk"
        else:
            risk_level = RiskLevel.VERY_HIGH
            severity = Severity.CRITICAL
            risk_category = "Very high risk"

        # Format component breakdown
        component_details = [f"{k}: {v:.4f}" for k, v in score_components.items() if v != 0]

        # Build recommendations list
        recommendations_list = [
            "Discuss risk with patient and family",
            "Consider multidisciplinary heart team discussion",
        ]
        if mortality_percent >= 5:
            recommendations_list.append("Optimize modifiable risk factors preoperatively")
        else:
            recommendations_list.append("Standard preoperative optimization")
        if mortality_percent >= 10:
            recommendations_list.append("Consider alternative therapies (TAVI, PCI) if very high risk")

        interpretation = Interpretation(
            summary=f"EuroSCORE II = {mortality_percent:.2f}%: {risk_category}",
            detail=(
                f"Predicted in-hospital/30-day mortality of {mortality_percent:.2f}%. "
                f"Based on patient factors, cardiac status, and surgical complexity. "
                f"This is a {risk_category.lower()} for cardiac surgery."
            ),
            severity=severity,
            risk_level=risk_level,
            stage=risk_category,
            stage_description=f"Predicted mortality {mortality_percent:.1f}%",
            recommendations=tuple(recommendations_list),
            next_steps=(
                "Complete preoperative workup",
                "Document informed consent with risk discussion",
            ),
        )

        return ScoreResult(
            value=round(mortality_percent, 2),
            unit=Unit.PERCENT,
            interpretation=interpretation,
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs={
                "age": age,
                "gender": gender,
                "creatinine_clearance": creatinine_clearance,
                "lvef": lvef,
                "nyha_class": nyha_class,
                "urgency": urgency,
                "weight_of_intervention": weight_of_intervention,
                "extracardiac_arteriopathy": extracardiac_arteriopathy,
                "poor_mobility": poor_mobility,
                "previous_cardiac_surgery": previous_cardiac_surgery,
                "chronic_lung_disease": chronic_lung_disease,
                "active_endocarditis": active_endocarditis,
                "critical_preop_state": critical_preop_state,
                "diabetes_on_insulin": diabetes_on_insulin,
                "ccs_class_4_angina": ccs_class_4_angina,
                "recent_mi": recent_mi,
                "pulmonary_hypertension": pulmonary_hypertension,
                "surgery_on_thoracic_aorta": surgery_on_thoracic_aorta,
            },
            calculation_details={
                "score_name": "EuroSCORE II",
                "predicted_mortality_percent": round(mortality_percent, 2),
                "predicted_mortality_decimal": round(predicted_mortality, 4),
                "linear_predictor": round(linear_predictor, 4),
                "beta_0_intercept": beta_0,
                "risk_category": risk_category,
                "contributing_factors": component_details,
                "score_components": {k: round(v, 4) for k, v in score_components.items() if v != 0},
            },
            formula_used="Predicted mortality = e^L / (1 + e^L), where L = β₀ + Σ(βᵢ × riskᵢ)",
            notes=[
                "EuroSCORE II validated on 22,381 patients from 154 hospitals",
                "Calibrated for contemporary cardiac surgical outcomes",
                "Consider model limitations in very high-risk populations",
                "Compare with STS score for comprehensive risk assessment",
            ],
        )
