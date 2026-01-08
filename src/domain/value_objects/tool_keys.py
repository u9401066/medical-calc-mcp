"""
Tool Keys Value Objects

Defines Low Level and High Level Keys for Tool Discovery.

- LowLevelKey: For precise tool selection by AI agents
- HighLevelKey: For exploration and discovery based on clinical context
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Specialty(Enum):
    """Medical specialties"""

    # ═══════════════════════════════════════════════════════════════════════════
    # PRIMARY SPECIALTIES - Internal Medicine & Medicine (內科系)
    # ═══════════════════════════════════════════════════════════════════════════
    INTERNAL_MEDICINE = "internal_medicine"  # 內科 (General)
    CARDIOLOGY = "cardiology"  # 心臟內科
    PULMONOLOGY = "pulmonology"  # 胸腔內科
    GASTROENTEROLOGY = "gastroenterology"  # 腸胃內科
    HEPATOLOGY = "hepatology"  # 肝膽內科
    NEPHROLOGY = "nephrology"  # 腎臟內科
    ENDOCRINOLOGY = "endocrinology"  # 內分泌科 / 新陳代謝科
    HEMATOLOGY = "hematology"  # 血液科
    ONCOLOGY = "oncology"  # 腫瘤內科
    INFECTIOUS_DISEASE = "infectious_disease"  # 感染科
    RHEUMATOLOGY = "rheumatology"  # 風濕免疫科
    ALLERGY_IMMUNOLOGY = "allergy_immunology"  # 過敏免疫科
    NEUROLOGY = "neurology"  # 神經內科
    GERIATRICS = "geriatrics"  # 老年醫學科
    PALLIATIVE_CARE = "palliative_care"  # 緩和醫療科 / 安寧醫療

    # ═══════════════════════════════════════════════════════════════════════════
    # PRIMARY SPECIALTIES - Surgery (外科系)
    # ═══════════════════════════════════════════════════════════════════════════
    SURGERY = "surgery"  # 一般外科
    CARDIAC_SURGERY = "cardiac_surgery"  # 心臟外科
    THORACIC_SURGERY = "thoracic_surgery"  # 胸腔外科
    VASCULAR_SURGERY = "vascular_surgery"  # 血管外科
    NEUROSURGERY = "neurosurgery"  # 神經外科
    ORTHOPEDICS = "orthopedics"  # 骨科
    PLASTIC_SURGERY = "plastic_surgery"  # 整形外科
    COLORECTAL_SURGERY = "colorectal_surgery"  # 大腸直腸外科
    UROLOGY = "urology"  # 泌尿外科
    TRANSPLANT_SURGERY = "transplant_surgery"  # 移植外科

    # ═══════════════════════════════════════════════════════════════════════════
    # PRIMARY SPECIALTIES - Other Medical Specialties
    # ═══════════════════════════════════════════════════════════════════════════
    ANESTHESIOLOGY = "anesthesiology"  # 麻醉科
    CRITICAL_CARE = "critical_care"  # 重症醫學科 / ICU
    EMERGENCY_MEDICINE = "emergency_medicine"  # 急診醫學科
    TRAUMA = "trauma"  # 創傷科
    PSYCHIATRY = "psychiatry"  # 精神科
    DERMATOLOGY = "dermatology"  # 皮膚科
    OPHTHALMOLOGY = "ophthalmology"  # 眼科
    ENT = "ent"  # 耳鼻喉科 (Otolaryngology)
    RADIOLOGY = "radiology"  # 放射診斷科
    NUCLEAR_MEDICINE = "nuclear_medicine"  # 核子醫學科
    PATHOLOGY = "pathology"  # 病理科
    TOXICOLOGY = "toxicology"  # 毒物科

    # ═══════════════════════════════════════════════════════════════════════════
    # PRIMARY SPECIALTIES - Women's & Children's Health
    # ═══════════════════════════════════════════════════════════════════════════
    OBSTETRICS = "obstetrics"  # 產科
    GYNECOLOGY = "gynecology"  # 婦科
    OBSTETRICS_GYNECOLOGY = "obstetrics_gynecology"  # 婦產科 (合併)
    PEDIATRICS = "pediatrics"  # 小兒科
    NEONATOLOGY = "neonatology"  # 新生兒科

    # ═══════════════════════════════════════════════════════════════════════════
    # PRIMARY SPECIALTIES - Rehabilitation & Support
    # ═══════════════════════════════════════════════════════════════════════════
    PHYSICAL_MEDICINE = "physical_medicine"  # 復健科 / PM&R
    DENTISTRY = "dentistry"  # 牙科
    ORAL_SURGERY = "oral_surgery"  # 口腔外科
    NURSING = "nursing"  # 護理

    # ═══════════════════════════════════════════════════════════════════════════
    # PRIMARY SPECIALTIES - Preventive & Community Medicine
    # ═══════════════════════════════════════════════════════════════════════════
    PREVENTIVE_MEDICINE = "preventive_medicine"  # 預防醫學科
    OCCUPATIONAL_MEDICINE = "occupational_medicine"  # 職業醫學科
    FAMILY_MEDICINE = "family_medicine"  # 家庭醫學科
    PUBLIC_HEALTH = "public_health"  # 公共衛生

    # ═══════════════════════════════════════════════════════════════════════════
    # SUBSPECIALTIES - Anesthesiology (麻醉次專科)
    # ═══════════════════════════════════════════════════════════════════════════
    CARDIAC_ANESTHESIA = "cardiac_anesthesia"  # 心臟麻醉
    NEUROANESTHESIA = "neuroanesthesia"  # 神經麻醉
    PEDIATRIC_ANESTHESIA = "pediatric_anesthesia"  # 小兒麻醉
    OBSTETRIC_ANESTHESIA = "obstetric_anesthesia"  # 產科麻醉
    REGIONAL_ANESTHESIA = "regional_anesthesia"  # 區域麻醉
    PAIN_MEDICINE = "pain_medicine"  # 疼痛醫學

    # ═══════════════════════════════════════════════════════════════════════════
    # SUBSPECIALTIES - Critical Care (重症次專科)
    # ═══════════════════════════════════════════════════════════════════════════
    PEDIATRIC_CRITICAL_CARE = "pediatric_critical_care"  # 兒童重症
    SURGICAL_CRITICAL_CARE = "surgical_critical_care"  # 外科重症
    CARDIAC_CRITICAL_CARE = "cardiac_critical_care"  # 心臟重症 / CCU
    NEURO_CRITICAL_CARE = "neuro_critical_care"  # 神經重症 / NICU
    BURN_CARE = "burn_care"  # 燒傷照護

    # ═══════════════════════════════════════════════════════════════════════════
    # SUBSPECIALTIES - Cardiology (心臟次專科)
    # ═══════════════════════════════════════════════════════════════════════════
    INTERVENTIONAL_CARDIOLOGY = "interventional_cardiology"  # 心臟介入
    ELECTROPHYSIOLOGY = "electrophysiology"  # 心臟電生理
    HEART_FAILURE = "heart_failure"  # 心衰竭專科
    ECHOCARDIOGRAPHY = "echocardiography"  # 心臟超音波

    # ═══════════════════════════════════════════════════════════════════════════
    # SUBSPECIALTIES - Other Medicine (其他次專科)
    # ═══════════════════════════════════════════════════════════════════════════
    SPORTS_MEDICINE = "sports_medicine"  # 運動醫學
    SLEEP_MEDICINE = "sleep_medicine"  # 睡眠醫學
    NUTRITION_MEDICINE = "nutrition_medicine"  # 營養醫學
    ADDICTION_MEDICINE = "addiction_medicine"  # 成癮醫學
    WOUND_CARE = "wound_care"  # 傷口照護
    INTERVENTIONAL_RADIOLOGY = "interventional_radiology"  # 介入放射科
    PEDIATRIC_SURGERY = "pediatric_surgery"  # 小兒外科
    GYNECOLOGIC_ONCOLOGY = "gynecologic_oncology"  # 婦癌科
    REPRODUCTIVE_MEDICINE = "reproductive_medicine"  # 生殖醫學
    MATERNAL_FETAL_MEDICINE = "maternal_fetal_medicine"  # 母胎醫學

    # ═══════════════════════════════════════════════════════════════════════════
    # OTHER
    # ═══════════════════════════════════════════════════════════════════════════
    OTHER = "other"


class ClinicalContext(Enum):
    """Clinical use contexts for calculators"""

    # ═══════════════════════════════════════════════════════════════════════════
    # GENERAL CLINICAL CONTEXTS (通用臨床情境)
    # ═══════════════════════════════════════════════════════════════════════════
    DIAGNOSIS = "diagnosis"  # 診斷
    DIFFERENTIAL_DIAGNOSIS = "differential_diagnosis"  # 鑑別診斷
    SCREENING = "screening"  # 篩檢
    STAGING = "staging"  # 分期
    GRADING = "grading"  # 分級
    CLASSIFICATION = "classification"  # 分類
    PROGNOSIS = "prognosis"  # 預後
    RISK_STRATIFICATION = "risk_stratification"  # 風險分層
    SEVERITY_ASSESSMENT = "severity_assessment"  # 嚴重度評估
    MONITORING = "monitoring"  # 監測
    FOLLOW_UP = "follow_up"  # 追蹤
    DISPOSITION = "disposition"  # 處置決策 (入院/出院)

    # ═══════════════════════════════════════════════════════════════════════════
    # TREATMENT & DOSING (治療與用藥)
    # ═══════════════════════════════════════════════════════════════════════════
    DRUG_DOSING = "drug_dosing"  # 藥物劑量
    TREATMENT_DECISION = "treatment_decision"  # 治療決策
    TREATMENT_RESPONSE = "treatment_response"  # 治療反應
    TREATMENT_ELIGIBILITY = "treatment_eligibility"  # 治療適應症
    ANTICOAGULATION = "anticoagulation"  # 抗凝血治療
    CHEMOTHERAPY_DOSING = "chemotherapy_dosing"  # 化療劑量
    IMMUNOSUPPRESSION = "immunosuppression"  # 免疫抑制治療

    # ═══════════════════════════════════════════════════════════════════════════
    # ELIGIBILITY & INDICATION (適應症與資格)
    # ═══════════════════════════════════════════════════════════════════════════
    ELIGIBILITY = "eligibility"  # 資格評估 (臨床試驗等)
    SURGICAL_INDICATION = "surgical_indication"  # 手術適應症
    TRANSPLANT_ELIGIBILITY = "transplant_eligibility"  # 移植資格
    THROMBOLYSIS_ELIGIBILITY = "thrombolysis_eligibility"  # 溶栓資格

    # ═══════════════════════════════════════════════════════════════════════════
    # PHYSIOLOGIC & LABORATORY (生理與檢驗)
    # ═══════════════════════════════════════════════════════════════════════════
    PHYSIOLOGIC = "physiologic"  # 生理計算
    LABORATORY = "laboratory"  # 檢驗判讀
    ELECTROLYTE = "electrolyte"  # 電解質
    ACID_BASE = "acid_base"  # 酸鹼平衡
    COAGULATION = "coagulation"  # 凝血功能

    # ═══════════════════════════════════════════════════════════════════════════
    # EMERGENCY & ACUTE CARE (急診與急性照護)
    # ═══════════════════════════════════════════════════════════════════════════
    EMERGENCY = "emergency"  # 急診評估
    TRIAGE = "triage"  # 檢傷分類
    RESUSCITATION = "resuscitation"  # 復甦
    TRAUMA_ASSESSMENT = "trauma_assessment"  # 創傷評估
    HEMORRHAGE_ASSESSMENT = "hemorrhage_assessment"  # 出血評估
    SHOCK_ASSESSMENT = "shock_assessment"  # 休克評估
    BURNS_ASSESSMENT = "burns_assessment"  # 燒傷評估

    # ═══════════════════════════════════════════════════════════════════════════
    # PREOPERATIVE & PERIOPERATIVE (術前與週術期)
    # ═══════════════════════════════════════════════════════════════════════════
    PREOPERATIVE_ASSESSMENT = "preoperative_assessment"  # 術前評估
    SURGICAL_RISK = "surgical_risk"  # 手術風險
    CARDIAC_RISK = "cardiac_risk"  # 心臟風險
    PULMONARY_RISK = "pulmonary_risk"  # 肺部風險
    BLEEDING_RISK = "bleeding_risk"  # 出血風險
    THROMBOSIS_RISK = "thrombosis_risk"  # 血栓風險
    SURGICAL_PLANNING = "surgical_planning"  # 手術規劃

    # ═══════════════════════════════════════════════════════════════════════════
    # AIRWAY & VENTILATION (氣道與呼吸)
    # ═══════════════════════════════════════════════════════════════════════════
    AIRWAY_MANAGEMENT = "airway_management"  # 氣道管理
    DIFFICULT_AIRWAY = "difficult_airway"  # 困難氣道
    VENTILATOR_MANAGEMENT = "ventilator_management"  # 呼吸器管理
    WEANING_ASSESSMENT = "weaning_assessment"  # 脫機評估
    OXYGEN_THERAPY = "oxygen_therapy"  # 氧氣治療
    RESPIRATORY_FAILURE = "respiratory_failure"  # 呼吸衰竭

    # ═══════════════════════════════════════════════════════════════════════════
    # HEMODYNAMIC & FLUID (血流動力學與輸液)
    # ═══════════════════════════════════════════════════════════════════════════
    HEMODYNAMIC_MONITORING = "hemodynamic_monitoring"  # 血流動力學監測
    FLUID_MANAGEMENT = "fluid_management"  # 輸液管理
    FLUID_RESPONSIVENESS = "fluid_responsiveness"  # 輸液反應性
    TRANSFUSION_DECISION = "transfusion_decision"  # 輸血決策
    BLOOD_LOSS_ESTIMATION = "blood_loss_estimation"  # 失血量估計

    # ═══════════════════════════════════════════════════════════════════════════
    # SEDATION & PAIN & DELIRIUM (鎮靜、疼痛與譫妄)
    # ═══════════════════════════════════════════════════════════════════════════
    SEDATION_ASSESSMENT = "sedation_assessment"  # 鎮靜評估
    PAIN_ASSESSMENT = "pain_assessment"  # 疼痛評估
    DELIRIUM_ASSESSMENT = "delirium_assessment"  # 譫妄評估
    WITHDRAWAL_ASSESSMENT = "withdrawal_assessment"  # 戒斷評估

    # ═══════════════════════════════════════════════════════════════════════════
    # NEUROLOGY & CONSCIOUSNESS (神經與意識)
    # ═══════════════════════════════════════════════════════════════════════════
    NEUROLOGICAL_ASSESSMENT = "neurological_assessment"  # 神經評估
    CONSCIOUSNESS_ASSESSMENT = "consciousness_assessment"  # 意識評估
    STROKE_ASSESSMENT = "stroke_assessment"  # 中風評估
    SEIZURE_ASSESSMENT = "seizure_assessment"  # 癲癇評估
    BRAIN_DEATH = "brain_death"  # 腦死判定
    NEUROMUSCULAR_MONITORING = "neuromuscular_monitoring"  # 神經肌肉監測
    VASOSPASM_PREDICTION = "vasospasm_prediction"  # 血管痙攣預測

    # ═══════════════════════════════════════════════════════════════════════════
    # CARDIAC (心臟)
    # ═══════════════════════════════════════════════════════════════════════════
    CARDIAC_ASSESSMENT = "cardiac_assessment"  # 心臟評估
    HEART_FAILURE_ASSESSMENT = "heart_failure_assessment"  # 心衰竭評估
    ARRHYTHMIA_RISK = "arrhythmia_risk"  # 心律不整風險
    ACS_RISK = "acs_risk"  # 急性冠心症風險
    STROKE_RISK = "stroke_risk"  # 中風風險 (如 AF)
    CARDIOVASCULAR_RISK = "cardiovascular_risk"  # 心血管風險

    # ═══════════════════════════════════════════════════════════════════════════
    # RENAL (腎臟)
    # ═══════════════════════════════════════════════════════════════════════════
    RENAL_FUNCTION = "renal_function"  # 腎功能評估
    AKI_ASSESSMENT = "aki_assessment"  # 急性腎損傷
    DIALYSIS_DECISION = "dialysis_decision"  # 透析決策

    # ═══════════════════════════════════════════════════════════════════════════
    # HEPATIC (肝臟)
    # ═══════════════════════════════════════════════════════════════════════════
    LIVER_FUNCTION = "liver_function"  # 肝功能評估
    CIRRHOSIS_ASSESSMENT = "cirrhosis_assessment"  # 肝硬化評估
    HEPATIC_ENCEPHALOPATHY = "hepatic_encephalopathy"  # 肝性腦病

    # ═══════════════════════════════════════════════════════════════════════════
    # INFECTION & SEPSIS (感染與敗血症)
    # ═══════════════════════════════════════════════════════════════════════════
    SEPSIS_EVALUATION = "sepsis_evaluation"  # 敗血症評估
    INFECTION_RISK = "infection_risk"  # 感染風險
    ANTIBIOTIC_SELECTION = "antibiotic_selection"  # 抗生素選擇

    # ═══════════════════════════════════════════════════════════════════════════
    # NUTRITION & METABOLISM (營養與代謝)
    # ═══════════════════════════════════════════════════════════════════════════
    NUTRITION_ASSESSMENT = "nutrition_assessment"  # 營養評估
    MALNUTRITION_RISK = "malnutrition_risk"  # 營養不良風險
    ENERGY_REQUIREMENT = "energy_requirement"  # 能量需求
    METABOLIC_ASSESSMENT = "metabolic_assessment"  # 代謝評估
    GLYCEMIC_CONTROL = "glycemic_control"  # 血糖控制

    # ═══════════════════════════════════════════════════════════════════════════
    # ICU SPECIFIC (ICU 專用)
    # ═══════════════════════════════════════════════════════════════════════════
    ICU_MANAGEMENT = "icu_management"  # ICU 管理
    ICU_ASSESSMENT = "icu_assessment"  # ICU 評估
    ICU_MORTALITY = "icu_mortality"  # ICU 死亡率預測
    ECMO_ASSESSMENT = "ecmo_assessment"  # ECMO 評估

    # ═══════════════════════════════════════════════════════════════════════════
    # ONCOLOGY (腫瘤)
    # ═══════════════════════════════════════════════════════════════════════════
    PERFORMANCE_STATUS = "performance_status"  # 功能狀態
    CANCER_PROGNOSIS = "cancer_prognosis"  # 癌症預後
    CHEMOTHERAPY_TOXICITY = "chemotherapy_toxicity"  # 化療毒性

    # ═══════════════════════════════════════════════════════════════════════════
    # OBSTETRICS (產科)
    # ═══════════════════════════════════════════════════════════════════════════
    FETAL_ASSESSMENT = "fetal_assessment"  # 胎兒評估
    LABOR_ASSESSMENT = "labor_assessment"  # 產程評估
    PREGNANCY_RISK = "pregnancy_risk"  # 妊娠風險

    # ═══════════════════════════════════════════════════════════════════════════
    # PEDIATRIC (小兒)
    # ═══════════════════════════════════════════════════════════════════════════
    PEDIATRIC_ASSESSMENT = "pediatric_assessment"  # 小兒評估
    GROWTH_ASSESSMENT = "growth_assessment"  # 生長評估
    DEVELOPMENTAL_ASSESSMENT = "developmental_assessment"  # 發展評估
    NEONATAL_ASSESSMENT = "neonatal_assessment"  # 新生兒評估

    # ═══════════════════════════════════════════════════════════════════════════
    # FALL & FRACTURE RISK (跌倒與骨折)
    # ═══════════════════════════════════════════════════════════════════════════
    FALL_RISK = "fall_risk"  # 跌倒風險
    FRACTURE_RISK = "fracture_risk"  # 骨折風險
    OSTEOPOROSIS = "osteoporosis"  # 骨質疏鬆

    # ═══════════════════════════════════════════════════════════════════════════
    # QUALITY & SAFETY (品質與安全)
    # ═══════════════════════════════════════════════════════════════════════════
    QUALITY_IMPROVEMENT = "quality_improvement"  # 品質改善
    PATIENT_SAFETY = "patient_safety"  # 病人安全
    PRESSURE_INJURY = "pressure_injury"  # 壓瘡風險
    SKIN_ASSESSMENT = "skin_assessment"  # 皮膚評估


@dataclass(frozen=True)
class LowLevelKey:
    """
    Low Level Key for precise tool identification.

    Used by AI agents for exact tool selection when they know
    which specific calculator they need.

    Attributes:
        tool_id: Unique identifier (e.g., "ckd_epi_2021")
        name: Human-readable name (e.g., "CKD-EPI 2021")
        purpose: What it calculates (e.g., "Calculate estimated GFR")
        input_params: List of required parameters
        output_type: Description of the result
    """

    tool_id: str
    name: str
    purpose: str
    input_params: list[str]
    output_type: str

    def __post_init__(self) -> None:
        if not self.tool_id:
            raise ValueError("tool_id is required")
        if not self.name:
            raise ValueError("name is required")

    def to_dict(self) -> dict[str, Any]:
        return {"tool_id": self.tool_id, "name": self.name, "purpose": self.purpose, "input_params": self.input_params, "output_type": self.output_type}


@dataclass(frozen=True)
class HighLevelKey:
    """
    High Level Key for tool exploration and discovery.

    Used by AI agents to find relevant tools based on:
    - Medical specialty
    - Clinical conditions/diseases
    - Use context (diagnosis, prognosis, etc.)
    - Natural language clinical questions
    - ICD-10 codes
    - Keywords

    This enables intelligent tool discovery when the agent
    doesn't know exactly which calculator to use.
    """

    specialties: tuple[Specialty, ...] = field(default_factory=tuple)
    conditions: tuple[str, ...] = field(default_factory=tuple)
    clinical_contexts: tuple[ClinicalContext, ...] = field(default_factory=tuple)
    clinical_questions: tuple[str, ...] = field(default_factory=tuple)
    icd10_codes: tuple[str, ...] = field(default_factory=tuple)
    keywords: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "specialties": [s.value for s in self.specialties],
            "conditions": list(self.conditions),
            "clinical_contexts": [c.value for c in self.clinical_contexts],
            "clinical_questions": list(self.clinical_questions),
            "icd10_codes": list(self.icd10_codes),
            "keywords": list(self.keywords),
        }

    def matches_specialty(self, specialty: Specialty) -> bool:
        """Check if this tool matches a specialty"""
        return specialty in self.specialties

    def matches_condition(self, condition: str) -> bool:
        """Check if this tool matches a condition (case-insensitive)"""
        condition_lower = condition.lower()
        return any(c.lower() == condition_lower for c in self.conditions)

    def matches_context(self, context: ClinicalContext) -> bool:
        """Check if this tool matches a clinical context"""
        return context in self.clinical_contexts

    def matches_keyword(self, keyword: str) -> bool:
        """Check if this tool matches a keyword (case-insensitive)"""
        keyword_lower = keyword.lower()
        return any(k.lower() == keyword_lower for k in self.keywords)
