"""
CHA₂DS₂-VA Score Calculator (2024 ESC Guidelines)

Updated stroke risk assessment for atrial fibrillation that removes sex 
as a risk modifier, as per the 2024 ESC Guidelines for AF management.

2024 ESC Guideline Reference:
    Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for 
    the management of atrial fibrillation developed in collaboration with 
    EACTS. Eur Heart J. 2024;45(36):3314-3414.
    doi:10.1093/eurheartj/ehae176. PMID: 39217497.

Key Change from CHA₂DS₂-VASc:
    - Removed "Sc" (Sex category - female) as a risk modifier
    - Maximum score reduced from 9 to 8
    - Sex-neutral thresholds for anticoagulation decisions
"""

from ..base import BaseCalculator
from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.units import Unit
from ...value_objects.reference import Reference
from ...value_objects.interpretation import Interpretation, Severity, RiskLevel
from ...value_objects.tool_keys import (
    LowLevelKey,
    HighLevelKey,
    Specialty,
    ClinicalContext,
)


class Chads2VaCalculator(BaseCalculator):
    """
    CHA₂DS₂-VA Score for Atrial Fibrillation Stroke Risk (2024 ESC)
    
    2024 ESC Guidelines removed sex as a risk modifier because:
    - Female sex alone does not increase stroke risk without other factors
    - Avoids gender-based treatment disparities
    - Simplifies clinical decision-making
    
    Scoring criteria:
    - Congestive Heart Failure: +1
    - Hypertension: +1
    - Age ≥75 years: +2
    - Diabetes mellitus: +1
    - Stroke/TIA/TE history: +2
    - Vascular disease (prior MI, PAD, aortic plaque): +1
    - Age 65-74 years: +1
    
    Maximum score: 8
    
    Anticoagulation recommendations (2024 ESC guidelines):
    - Score 0: No anticoagulation (very low risk)
    - Score 1: Anticoagulation should be considered
    - Score ≥2: Anticoagulation is recommended
    
    CHA₂DS₂-VA 計分系統（2024年ESC心房顫動指引）
    
    2024年ESC指引移除性別作為風險修飾因子，原因：
    - 單純女性性別在沒有其他因素下不增加中風風險
    - 避免基於性別的治療差異
    - 簡化臨床決策
    """
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="chads2_va",
                name="CHA₂DS₂-VA Score (2024 ESC)",
                purpose="Estimate stroke risk in AF using 2024 ESC sex-neutral criteria for anticoagulation decisions",
                input_params=[
                    "chf_or_lvef_lte_40",
                    "hypertension",
                    "age_gte_75",
                    "diabetes",
                    "stroke_tia_or_te_history",
                    "vascular_disease",
                    "age_65_to_74",
                ],
                output_type="Score 0-8 with annual stroke risk and anticoagulation recommendation"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CARDIOLOGY,
                    Specialty.NEUROLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.EMERGENCY_MEDICINE,
                ),
                conditions=(
                    "atrial fibrillation",
                    "AF",
                    "Afib",
                    "atrial flutter",
                    "stroke prevention",
                    "thromboembolism",
                ),
                clinical_contexts=(
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.PROGNOSIS,
                ),
                clinical_questions=(
                    "Does this AF patient need anticoagulation per 2024 ESC guidelines?",
                    "What is the stroke risk using the new CHA₂DS₂-VA score?",
                    "Should I prescribe a DOAC for this AF patient (2024 criteria)?",
                    "Is anticoagulation indicated using sex-neutral criteria?",
                    "What is the CHA₂DS₂-VA score without sex modifier?",
                ),
                icd10_codes=(
                    "I48",  # Atrial fibrillation and flutter
                    "I48.0",  # Paroxysmal atrial fibrillation
                    "I48.1",  # Persistent atrial fibrillation
                    "I48.2",  # Chronic atrial fibrillation
                    "I48.91",  # Unspecified atrial fibrillation
                ),
                keywords=(
                    "CHA2DS2-VA",
                    "CHADS-VA",
                    "2024 ESC",
                    "ESC 2024",
                    "sex-neutral",
                    "atrial fibrillation stroke risk",
                    "anticoagulation AF",
                    "stroke prevention AF",
                    "DOAC indication",
                    "新版",
                    "心房顫動",
                    "抗凝血",
                )
            ),
            references=(
                Reference(
                    citation="Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines "
                             "for the management of atrial fibrillation developed in collaboration "
                             "with EACTS. Eur Heart J. 2024;45(36):3314-3414.",
                    doi="10.1093/eurheartj/ehae176",
                    pmid="39217497",
                    year=2024,
                ),
                Reference(
                    citation="Lip GY, Nieuwlaat R, Pisters R, et al. Refining clinical risk "
                             "stratification for predicting stroke and thromboembolism in atrial "
                             "fibrillation using a novel risk factor-based approach: the euro "
                             "heart survey on atrial fibrillation. Chest. 2010;137(2):263-272.",
                    doi="10.1378/chest.09-1584",
                    pmid="19762550",
                    year=2010,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )
    
    def calculate(
        self,
        chf_or_lvef_lte_40: bool,
        hypertension: bool,
        age_gte_75: bool,
        diabetes: bool,
        stroke_tia_or_te_history: bool,
        vascular_disease: bool,
        age_65_to_74: bool,
    ) -> ScoreResult:
        """
        Calculate CHA₂DS₂-VA score (2024 ESC - sex-neutral version).
        計算CHA₂DS₂-VA分數（2024 ESC - 無性別因素版本）
        
        Args:
            chf_or_lvef_lte_40: CHF or LVEF ≤40% / 心衰竭或LVEF≤40%
            hypertension: History of hypertension / 高血壓病史
            age_gte_75: Age ≥75 years (2 points) / 年齡≥75歲（2分）
            diabetes: Diabetes mellitus / 糖尿病
            stroke_tia_or_te_history: Prior stroke, TIA, or thromboembolism (2 points) / 
                                       中風/TIA/血栓栓塞病史（2分）
            vascular_disease: Prior MI, PAD, or aortic plaque / 
                              心肌梗塞、周邊動脈疾病或主動脈斑塊
            age_65_to_74: Age 65-74 years (1 point; mutually exclusive with age ≥75) /
                          年齡65-74歲（1分；與≥75歲互斥）
            
        Returns:
            ScoreResult with score, stroke risk, and anticoagulation recommendation
        """
        # Calculate score (no sex modifier in 2024 version)
        score = 0
        score += 1 if chf_or_lvef_lte_40 else 0
        score += 1 if hypertension else 0
        score += 2 if age_gte_75 else 0
        score += 1 if diabetes else 0
        score += 2 if stroke_tia_or_te_history else 0
        score += 1 if vascular_disease else 0
        score += 1 if age_65_to_74 and not age_gte_75 else 0  # Only if not ≥75
        
        # Determine interpretation
        interpretation = self._interpret_score(score)
        
        # Component details
        components = {
            "C - CHF/LVEF ≤40% (心衰竭)": 1 if chf_or_lvef_lte_40 else 0,
            "H - Hypertension (高血壓)": 1 if hypertension else 0,
            "A₂ - Age ≥75 (年齡≥75歲)": 2 if age_gte_75 else 0,
            "D - Diabetes (糖尿病)": 1 if diabetes else 0,
            "S₂ - Stroke/TIA/TE (中風史)": 2 if stroke_tia_or_te_history else 0,
            "V - Vascular disease (血管疾病)": 1 if vascular_disease else 0,
            "A - Age 65-74 (年齡65-74歲)": 1 if (age_65_to_74 and not age_gte_75) else 0,
        }
        
        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            calculation_details=components,
            references=list(self.references),
        )
    
    def _interpret_score(self, score: int) -> Interpretation:
        """
        Generate interpretation based on CHA₂DS₂-VA score per 2024 ESC guidelines.
        根據2024 ESC指引產生CHA₂DS₂-VA分數解讀
        """
        
        # Annual stroke risk rates (estimated from original CHA₂DS₂-VASc data,
        # adjusted for sex-neutral scoring)
        stroke_rates = {
            0: "0.2%",
            1: "0.6%",
            2: "2.2%",
            3: "3.2%",
            4: "4.8%",
            5: "7.2%",
            6: "9.7%",
            7: "11.2%",
            8: "14.5%",
        }
        
        annual_risk = stroke_rates.get(score, ">14%")
        
        if score == 0:
            # Very low risk - no anticoagulation
            severity = Severity.NORMAL
            risk_level = RiskLevel.VERY_LOW
            summary = f"CHA₂DS₂-VA = {score}: Very low risk ({annual_risk} annual stroke risk)"
            detail = (
                f"Very low stroke risk per 2024 ESC guidelines. "
                f"Annual ischemic stroke rate approximately {annual_risk}. "
                f"No anticoagulation recommended."
            )
            detail_zh = (
                f"根據2024 ESC指引為極低中風風險。"
                f"年中風率約{annual_risk}。不建議抗凝血治療。"
            )
            recommendations = [
                "No anticoagulation recommended (不建議抗凝血)",
                "Address modifiable cardiovascular risk factors",
                "Reassess risk factors periodically",
            ]
            next_steps = [
                "控制高血壓、糖尿病等可改變風險因子",
                "定期重新評估CHA₂DS₂-VA分數",
                "生活型態調整以降低心血管風險",
            ]
            anticoagulation = "Not indicated (不需要)"
            
        elif score == 1:
            # Low risk - consider anticoagulation
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            summary = f"CHA₂DS₂-VA = {score}: Low risk ({annual_risk} annual stroke risk)"
            detail = (
                f"Low stroke risk per 2024 ESC guidelines. "
                f"Annual stroke rate approximately {annual_risk}. "
                f"Anticoagulation should be considered based on individual assessment."
            )
            detail_zh = (
                f"根據2024 ESC指引為低中風風險。"
                f"年中風率約{annual_risk}。應依個別評估考慮抗凝血治療。"
            )
            recommendations = [
                "Anticoagulation should be considered (應考慮抗凝血)",
                "Assess bleeding risk with HAS-BLED score",
                "Shared decision-making with patient",
                "DOACs preferred over VKA if OAC chosen",
            ]
            next_steps = [
                "計算HAS-BLED評估出血風險",
                "與病患共同決策討論利弊",
                "若決定抗凝血，DOAC為首選",
                "處理可改變的出血風險因子",
            ]
            anticoagulation = "Consider (應考慮)"
            
        else:
            # Score ≥2: Anticoagulation recommended
            if score <= 3:
                severity = Severity.MODERATE
                risk_level = RiskLevel.INTERMEDIATE
            elif score <= 5:
                severity = Severity.SEVERE
                risk_level = RiskLevel.HIGH
            else:
                severity = Severity.CRITICAL
                risk_level = RiskLevel.VERY_HIGH
                
            summary = f"CHA₂DS₂-VA = {score}: {risk_level.value.replace('_', ' ').title()} risk ({annual_risk} annual stroke risk)"
            detail = (
                f"{'Significant' if score <= 4 else 'High'} stroke risk per 2024 ESC guidelines. "
                f"Annual stroke rate approximately {annual_risk}. "
                f"Oral anticoagulation is recommended."
            )
            detail_zh = (
                f"根據2024 ESC指引為{'中度' if score <= 3 else '高度'}中風風險。"
                f"年中風率約{annual_risk}。建議口服抗凝血治療。"
            )
            recommendations = [
                "Oral anticoagulation is recommended (建議口服抗凝血)",
                "DOACs preferred over VKA (except mechanical valves, moderate-severe MS)",
                "Aspirin monotherapy is NOT adequate for stroke prevention",
            ]
            next_steps = [
                "評估腎功能以決定DOAC劑量",
                "計算HAS-BLED辨識可改變的出血風險",
                "依病患因素選擇適當DOAC",
                "確保病患衛教理解抗凝血治療",
            ]
            
            if score >= 4:
                recommendations.append("High stroke risk - ensure OAC adherence (高風險-確保服藥順從性)")
            if score >= 6:
                recommendations.append("Very high risk - consider cardiology consultation")
            
            anticoagulation = "Recommended (建議)"
        
        return Interpretation(
            summary=summary,
            severity=severity,
            detail=f"{detail}\n\n{detail_zh}",
            stage=f"CHA₂DS₂-VA = {score}",
            stage_description=f"Annual stroke risk: {annual_risk} | 年中風風險: {annual_risk}",
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
            warnings=(
                "High stroke risk - anticoagulation strongly recommended (高中風風險-強烈建議抗凝血)",
            ) if score >= 4 else tuple(),
        )
