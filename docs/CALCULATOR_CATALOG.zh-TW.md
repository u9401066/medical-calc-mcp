# 計算器目錄

> 由目前 registry 自動產生，請勿手動編輯。
> 重新產生指令：`uv run python scripts/generate_tool_catalog_docs.py` (v1.6.0)。

此快照包含 **151 個計算器**，涵蓋 **31 個主要專科**。

## 專科摘要

| 專科 | 工具數 | 範例 tool ID |
|------|------:|--------------|
| 麻醉科 | 8 | `aldrete_score`, `apfel_ponv`, `asa_physical_status` |
| 心臟科 | 11 | `acef_ii`, `chads2_va`, `chads2_vasc` |
| 重症醫學科 | 18 | `anion_gap`, `apache_ii`, `cam_icu` |
| 皮膚科 | 5 | `bsa_dermatology`, `dlqi`, `pasi` |
| 急診醫學科 | 9 | `centor_score`, `glasgow_coma_scale`, `heart_score` |
| 內分泌科 | 6 | `cas_graves`, `cushingoid_score`, `findrisc` |
| 家庭醫學科 | 4 | `audit`, `audit_c`, `cage` |
| 腸胃科 | 3 | `aims65`, `glasgow_blatchford`, `rockall_score` |
| 老年醫學科 | 13 | `barthel_index`, `cfs`, `four_at` |
| 婦科 | 3 | `epds`, `pop_q`, `sflt_plgf_ratio` |
| 血液科 | 1 | `4ts_hit` |
| 肝膽科 | 5 | `child_pugh`, `fib4_index`, `lille_model` |
| 感染科 | 1 | `pitt_bacteremia` |
| 內科 | 2 | `charlson_comorbidity_index`, `corrected_calcium` |
| 新生兒科 | 1 | `ballard_score` |
| 腎臟科 | 6 | `ckd_epi_2021`, `cockcroft_gault`, `fena` |
| 神經科 | 7 | `abcd2`, `fisher_grade`, `four_score` |
| nursing | 1 | `braden_scale` |
| nutrition medicine | 3 | `conut`, `gnri`, `mst` |
| 產科 | 1 | `bishop_score` |
| 腫瘤科 | 4 | `body_surface_area`, `ecog_performance_status`, `karnofsky_performance_scale` |
| 疼痛醫學 | 1 | `mme_calculator` |
| palliative care | 2 | `palliative_performance_scale`, `palliative_prognostic_index` |
| 小兒科 | 6 | `apgar_score`, `pediatric_dosing`, `pediatric_gcs` |
| 精神科 | 9 | `caps5`, `gad7`, `hama` |
| 胸腔科 | 4 | `aa_gradient`, `curb65`, `psi_port` |
| 風濕免疫科 | 1 | `das28` |
| sleep medicine | 5 | `athens_insomnia_scale`, `berlin_questionnaire`, `epworth_sleepiness_scale` |
| 外科 | 6 | `caprini_vte`, `iss`, `parkland_formula` |
| 毒理科 | 1 | `osmolar_gap` |
| 泌尿科 | 4 | `bosniak`, `iciq_sf`, `ipss` |

## 完整工具清單

| Tool ID | 名稱 | 主要專科 | 用途 | 文獻數 |
|--------|------|----------|------|------:|
| `aldrete_score` | Aldrete Score | 麻醉科 | Assess post-anesthesia recovery and PACU discharge readiness | 2 |
| `apfel_ponv` | Apfel Score for PONV | 麻醉科 | Predict postoperative nausea and vomiting risk | 2 |
| `asa_physical_status` | ASA Physical Status Classification | 麻醉科 | Assess preoperative patient fitness and anesthetic risk | 2 |
| `mabl` | Maximum Allowable Blood Loss (MABL) | 麻醉科 | Calculate maximum blood loss before transfusion required | 4 |
| `mallampati_score` | Mallampati Score (Modified) | 麻醉科 | Predict difficult intubation based on oropharyngeal visualization | 2 |
| `rcri` | Revised Cardiac Risk Index (Lee Index) | 麻醉科 | Estimate risk of major cardiac complications after non-cardiac surgery | 2 |
| `stop_bang` | STOP-BANG Questionnaire | 麻醉科 | Screen for obstructive sleep apnea risk in surgical patients | 2 |
| `transfusion_calc` | Transfusion Volume Calculator | 麻醉科 | Calculate blood product volume needed for target Hct/Hgb/Plt | 4 |
| `acef_ii` | ACEF II Score | 心臟科 | Predict cardiac surgery mortality risk | 2 |
| `chads2_va` | CHA₂DS₂-VA Score (2024 ESC) | 心臟科 | Estimate stroke risk in AF using 2024 ESC sex-neutral criteria for anticoagulation decisions | 2 |
| `chads2_vasc` | CHA₂DS₂-VASc Score | 心臟科 | Estimate annual stroke risk in atrial fibrillation for anticoagulation decisions | 2 |
| `corrected_qt` | Corrected QT Interval (QTc) | 心臟科 | Calculate heart-rate corrected QT interval for arrhythmia risk | 3 |
| `euroscore_ii` | EuroSCORE II (Cardiac Surgery Risk) | 心臟科 | Predict mortality risk for cardiac surgery | 2 |
| `framingham_risk_score` | Framingham Risk Score | 心臟科 | Estimate 10-year risk of coronary heart disease | 3 |
| `grace_score` | GRACE Score | 心臟科 | Stratify mortality risk in acute coronary syndrome | 2 |
| `has_bled` | HAS-BLED Score | 心臟科 | Assess 1-year major bleeding risk in AF patients on anticoagulation | 3 |
| `hfa_peff` | HFA-PEFF Score (Heart Failure with Preserved Ejection Fraction) | 心臟科 | Diagnose HFpEF using echocardiographic and biomarker criteria | 2 |
| `score2` | SCORE2 (Systematic Coronary Risk Evaluation 2) | 心臟科 | Estimate 10-year cardiovascular risk in apparently healthy individuals | 2 |
| `timi_stemi` | TIMI Risk Score for STEMI | 心臟科 | Predict 30-day mortality in STEMI patients | 1 |
| `anion_gap` | Anion Gap | 重症醫學科 | Calculate serum anion gap for metabolic acidosis differential diagnosis | 2 |
| `apache_ii` | APACHE II Score | 重症醫學科 | Estimate ICU mortality risk based on acute physiology and chronic health | 1 |
| `cam_icu` | CAM-ICU (Confusion Assessment Method for ICU) | 重症醫學科 | Screen for delirium in ICU patients | 3 |
| `corrected_sodium` | Corrected Sodium for Hyperglycemia | 重症醫學科 | Calculate true sodium level corrected for hyperglycemic dilution | 2 |
| `cpis` | Clinical Pulmonary Infection Score (CPIS) | 重症醫學科 | Assist in VAP diagnosis and guide antibiotic therapy decisions | 3 |
| `delta_ratio` | Delta Ratio (Delta Gap) | 重症醫學科 | Identify mixed acid-base disorders in high anion gap metabolic acidosis | 2 |
| `icdsc` | ICDSC (Intensive Care Delirium Screening Checklist) | 重症醫學科 | Screen for delirium in ICU patients over 8-24 hour observation period | 3 |
| `ideal_body_weight` | Ideal Body Weight (IBW) | 重症醫學科 | Calculate ideal body weight for ventilator settings and drug dosing | 3 |
| `murray_lung_injury_score` | Murray Lung Injury Score (LIS) | 重症醫學科 | Quantify severity of acute lung injury and guide ECMO consideration | 2 |
| `nrs_2002` | NRS-2002 (Nutritional Risk Screening 2002) | 重症醫學科 | Screen hospitalized patients for nutritional risk | 2 |
| `nutric_score` | NUTRIC Score (Nutrition Risk in Critically Ill) | 重症醫學科 | Identify ICU patients who benefit most from nutritional therapy | 2 |
| `pf_ratio` | P/F Ratio (PaO2/FiO2) | 重症醫學科 | Calculate P/F ratio for ARDS severity classification | 1 |
| `rass` | Richmond Agitation-Sedation Scale (RASS) | 重症醫學科 | Assess level of agitation or sedation in ICU patients | 2 |
| `rox_index` | ROX Index | 重症醫學科 | Predict high-flow nasal cannula failure and need for intubation | 2 |
| `sirs_criteria` | SIRS Criteria (Systemic Inflammatory Response Syndrome) | 重症醫學科 | Identify systemic inflammatory response syndrome | 2 |
| `sofa2_score` | SOFA-2 Score (2025 Update) | 重症醫學科 | Assess organ dysfunction with updated 2025 thresholds based on 3.3M patients | 2 |
| `sofa_score` | SOFA Score (Sequential Organ Failure Assessment) | 重症醫學科 | Assess organ dysfunction and predict ICU mortality in sepsis | 3 |
| `winters_formula` | Winter's Formula | 重症醫學科 | Predict expected PaCO₂ in metabolic acidosis | 2 |
| `bsa_dermatology` | BSA for Dermatology (Body Surface Area) | 皮膚科 | Estimate body surface area affected by skin disease | 2 |
| `dlqi` | DLQI (Dermatology Life Quality Index) | 皮膚科 | Assess quality of life impact of skin disease | 2 |
| `pasi` | PASI (Psoriasis Area and Severity Index) | 皮膚科 | Assess psoriasis severity for treatment decisions | 2 |
| `salt_score` | SALT (Severity of Alopecia Tool) | 皮膚科 | Quantify hair loss severity in alopecia | 2 |
| `scorad` | SCORAD (SCORing Atopic Dermatitis) | 皮膚科 | Assess atopic dermatitis severity | 2 |
| `centor_score` | Centor Score (Modified/McIsaac) | 急診醫學科 | Estimate probability of GAS pharyngitis and guide testing/treatment decisions | 3 |
| `glasgow_coma_scale` | Glasgow Coma Scale (GCS) | 急診醫學科 | Assess level of consciousness and brain injury severity | 2 |
| `heart_score` | HEART Score | 急診醫學科 | Stratify risk of major adverse cardiac events in ED chest pain patients | 2 |
| `news2_score` | NEWS2 (National Early Warning Score 2) | 急診醫學科 | Detect clinical deterioration and trigger appropriate clinical response | 2 |
| `perc_rule` | PERC Rule (Pulmonary Embolism Rule-out Criteria) | 急診醫學科 | Rule out pulmonary embolism in low-risk patients | 2 |
| `qsofa_score` | qSOFA Score (Quick SOFA) | 急診醫學科 | Bedside screening for patients at risk of poor outcomes from sepsis | 3 |
| `shock_index` | Shock Index (SI) | 急診醫學科 | Calculate HR/SBP ratio for rapid hemodynamic assessment | 3 |
| `wells_dvt` | Wells Score for DVT | 急診醫學科 | Estimate pretest probability of DVT to guide diagnostic workup | 2 |
| `wells_pe` | Wells Score for PE | 急診醫學科 | Estimate pretest probability of pulmonary embolism to guide diagnostic workup | 2 |
| `cas_graves` | CAS (Clinical Activity Score for Graves' Ophthalmopathy) | 內分泌科 | Assess inflammatory activity in thyroid eye disease | 2 |
| `cushingoid_score` | Cushingoid Score (Clinical Features of Cushing's Syndrome) | 內分泌科 | Assess clinical likelihood of Cushing's syndrome | 2 |
| `findrisc` | FINDRISC (Finnish Diabetes Risk Score) | 內分泌科 | Estimate 10-year risk of type 2 diabetes | 2 |
| `frax` | FRAX (Fracture Risk Assessment Tool) | 內分泌科 | Calculate 10-year fracture risk probability | 2 |
| `nds` | NDS (Neuropathy Disability Score) | 內分泌科 | Assess severity of diabetic peripheral neuropathy | 2 |
| `toronto_css` | Toronto CSS (Toronto Clinical Scoring System) | 內分泌科 | Diagnose and stage diabetic polyneuropathy | 2 |
| `audit` | AUDIT (Alcohol Use Disorders Identification Test) | 家庭醫學科 | Assess hazardous drinking and possible alcohol use disorder severity | 2 |
| `audit_c` | AUDIT-C (Alcohol Use Disorders Identification Test - Consumption) | 家庭醫學科 | Screen for risky alcohol consumption with a three-item score | 2 |
| `cage` | CAGE Questionnaire | 家庭醫學科 | Identify possible problematic alcohol use with a four-question screen | 2 |
| `scoff` | SCOFF Questionnaire | 家庭醫學科 | Screen for possible eating disorder with a five-question instrument | 2 |
| `aims65` | AIMS65 Score | 腸胃科 | Predict in-hospital mortality for upper GI bleeding | 1 |
| `glasgow_blatchford` | Glasgow-Blatchford Score (GBS) | 腸胃科 | Stratify upper GI bleeding risk and predict need for intervention | 2 |
| `rockall_score` | Rockall Score | 腸胃科 | Predict mortality and rebleeding in upper GI bleeding | 1 |
| `barthel_index` | Barthel Index (ADL Assessment) | 老年醫學科 | Assess functional independence in activities of daily living | 2 |
| `cfs` | CFS (Clinical Frailty Scale) | 老年醫學科 | Assess frailty in older adults | 2 |
| `four_at` | 4AT (Rapid Assessment Test for Delirium) | 老年醫學科 | Rapid delirium screening in hospital settings | 2 |
| `frail_scale` | FRAIL Scale | 老年醫學科 | Screen for frailty with a five-domain yes/no questionnaire | 2 |
| `gds_15` | GDS-15 (Geriatric Depression Scale - 15 item) | 老年醫學科 | Screen for depression in older adults with a geriatric-focused questionnaire | 2 |
| `katz_adl` | Katz ADL Index | 老年醫學科 | Assess independence in basic activities of daily living | 2 |
| `lawton_iadl` | Lawton IADL (Instrumental Activities of Daily Living) | 老年醫學科 | Assess higher-order community living independence in older adults | 2 |
| `mini_cog` | Mini-Cog | 老年醫學科 | Briefly screen for cognitive impairment using recall and clock drawing | 2 |
| `mmse` | MMSE (Mini-Mental State Examination) | 老年醫學科 | Screen for cognitive impairment | 2 |
| `mna` | MNA (Mini Nutritional Assessment) | 老年醫學科 | Screen for malnutrition risk in elderly patients | 2 |
| `moca` | MoCA (Montreal Cognitive Assessment) | 老年醫學科 | Screen for mild cognitive impairment | 2 |
| `sarc_f` | SARC-F | 老年醫學科 | Screen for sarcopenia risk with a brief symptom-based score | 2 |
| `tug` | TUG (Timed Up and Go Test) | 老年醫學科 | Assess mobility, balance, and fall risk | 2 |
| `epds` | EPDS (Edinburgh Postnatal Depression Scale) | 婦科 | Screen for postnatal and perinatal depression | 2 |
| `pop_q` | POP-Q (Pelvic Organ Prolapse Quantification) | 婦科 | Stage pelvic organ prolapse severity | 2 |
| `sflt_plgf_ratio` | sFlt-1/PlGF Ratio (Preeclampsia Biomarker) | 婦科 | Predict and diagnose preeclampsia | 2 |
| `4ts_hit` | 4Ts Score for HIT | 血液科 | Assess pretest probability of heparin-induced thrombocytopenia | 2 |
| `child_pugh` | Child-Pugh Score | 肝膽科 | Assess severity of chronic liver disease (cirrhosis) for prognosis | 3 |
| `fib4_index` | FIB-4 Index | 肝膽科 | Non-invasive assessment of liver fibrosis | 2 |
| `lille_model` | Lille Model (Alcoholic Hepatitis Steroid Response) | 肝膽科 | Assess response to corticosteroid therapy in alcoholic hepatitis | 2 |
| `maddrey_df` | Maddrey Discriminant Function (mDF) | 肝膽科 | Assess severity and prognosis in alcoholic hepatitis | 3 |
| `meld_score` | MELD Score | 肝膽科 | Predict 90-day mortality in end-stage liver disease for transplant prioritization | 3 |
| `pitt_bacteremia` | Pitt Bacteremia Score | 感染科 | Predict mortality in gram-negative bacteremia patients | 2 |
| `charlson_comorbidity_index` | Charlson Comorbidity Index (CCI) | 內科 | Predict 10-year mortality based on comorbid conditions | 3 |
| `corrected_calcium` | Albumin-Corrected Calcium | 內科 | Correct total calcium for hypoalbuminemia | 3 |
| `ballard_score` | New Ballard Score | 新生兒科 | Estimate gestational age of newborns from physical and neuromuscular maturity | 2 |
| `ckd_epi_2021` | CKD-EPI 2021 (Creatinine, without race) | 腎臟科 | Calculate estimated glomerular filtration rate (eGFR) | 1 |
| `cockcroft_gault` | Cockcroft-Gault Creatinine Clearance | 腎臟科 | Calculate creatinine clearance for drug dosing adjustments | 3 |
| `fena` | Fractional Excretion of Sodium (FENa) | 腎臟科 | Differentiate prerenal azotemia from acute tubular necrosis | 2 |
| `free_water_deficit` | Free Water Deficit | 腎臟科 | Calculate free water deficit for hypernatremia treatment | 3 |
| `kdigo_aki` | KDIGO AKI Staging | 腎臟科 | Classify acute kidney injury severity by KDIGO criteria | 3 |
| `serum_osmolality` | Serum Osmolality (Calculated) | 腎臟科 | Calculate serum osmolality from sodium, glucose, and BUN | 2 |
| `abcd2` | ABCD2 Score | 神經科 | Predict stroke risk after TIA at 2, 7, and 90 days | 2 |
| `fisher_grade` | Fisher Grade (Modified Fisher Scale) | 神經科 | Predict vasospasm risk in subarachnoid hemorrhage based on CT findings | 2 |
| `four_score` | FOUR Score (Full Outline of UnResponsiveness) | 神經科 | Assess coma severity with detailed brainstem and respiratory evaluation | 1 |
| `hunt_hess` | Hunt and Hess Scale | 神經科 | Grade subarachnoid hemorrhage severity and predict surgical risk | 1 |
| `ich_score` | ICH Score (Intracerebral Hemorrhage Score) | 神經科 | Predict 30-day mortality in spontaneous intracerebral hemorrhage | 1 |
| `modified_rankin_scale` | Modified Rankin Scale (mRS) | 神經科 | Assess disability and dependence after stroke | 2 |
| `nihss` | NIH Stroke Scale (NIHSS) | 神經科 | Quantify stroke severity and track neurological changes | 2 |
| `braden_scale` | Braden Scale | nursing | Estimate pressure injury risk using six nursing assessment domains | 2 |
| `conut` | CONUT Score | nutrition medicine | Screen hospital nutrition status using albumin, lymphocytes, and cholesterol | 2 |
| `gnri` | GNRI (Geriatric Nutritional Risk Index) | nutrition medicine | Estimate nutrition-related risk in older or medically complex adults | 2 |
| `mst` | MST (Malnutrition Screening Tool) | nutrition medicine | Rapidly identify patients at risk of malnutrition with a short screening score | 2 |
| `bishop_score` | Bishop Score | 產科 | Assess cervical favorability for labor induction | 2 |
| `body_surface_area` | Body Surface Area (BSA) | 腫瘤科 | Calculate BSA for chemotherapy dosing, cardiac indexing, and burn assessment | 3 |
| `ecog_performance_status` | ECOG Performance Status | 腫瘤科 | Assess functional status and prognosis in cancer patients | 2 |
| `karnofsky_performance_scale` | Karnofsky Performance Scale (KPS) | 腫瘤科 | Quantify functional status and prognosis in cancer and other diseases | 2 |
| `mascc_score` | MASCC Risk Index | 腫瘤科 | Identify low-risk febrile neutropenia patients for potential outpatient management | 2 |
| `mme_calculator` | MME Calculator (Morphine Milligram Equivalent) | 疼痛醫學 | Calculate total opioid dose in morphine equivalents | 2 |
| `palliative_performance_scale` | Palliative Performance Scale (PPS) | palliative care | Assess functional status and prognosis in palliative care | 2 |
| `palliative_prognostic_index` | Palliative Prognostic Index (PPI) | palliative care | Estimate short-term prognosis in palliative care using PPS and bedside symptoms | 2 |
| `apgar_score` | APGAR Score | 小兒科 | Newborn assessment at 1 and 5 minutes after birth | 2 |
| `pediatric_dosing` | Pediatric Drug Dosing Calculator | 小兒科 | Calculate weight-based drug doses for pediatric patients | 3 |
| `pediatric_gcs` | Pediatric Glasgow Coma Scale | 小兒科 | Age-adapted consciousness assessment for children | 2 |
| `pediatric_sofa` | Pediatric SOFA (pSOFA) Score | 小兒科 | Age-adapted organ dysfunction assessment for pediatric patients | 2 |
| `pews` | Pediatric Early Warning Score (PEWS) | 小兒科 | Identify hospitalized children at risk of clinical deterioration | 2 |
| `pim3` | Pediatric Index of Mortality 3 (PIM3) | 小兒科 | Predict PICU mortality for quality benchmarking | 2 |
| `caps5` | CAPS-5 (Clinician-Administered PTSD Scale for DSM-5) | 精神科 | Gold standard diagnostic assessment for PTSD | 2 |
| `gad7` | GAD-7 (Generalized Anxiety Disorder 7-item) | 精神科 | Screen for anxiety and assess severity | 2 |
| `hama` | HAM-A (Hamilton Anxiety Rating Scale) | 精神科 | Assess anxiety severity (clinician-rated) | 2 |
| `hamd` | HAM-D17 (Hamilton Depression Rating Scale) | 精神科 | Assess depression severity (clinician-rated) | 2 |
| `madrs` | MADRS (Montgomery-Åsberg Depression Rating Scale) | 精神科 | Assess depression severity with focus on treatment response | 2 |
| `pc_ptsd_5` | PC-PTSD-5 (Primary Care PTSD Screen for DSM-5) | 精神科 | Rapidly screen for probable PTSD in primary care and general medical settings | 2 |
| `pcl5` | PCL-5 (PTSD Checklist for DSM-5) | 精神科 | Self-report screening and monitoring for PTSD | 2 |
| `phq2` | PHQ-2 (Patient Health Questionnaire-2) | 精神科 | Rapidly screen for depressive symptoms in primary and specialty care | 2 |
| `phq9` | PHQ-9 (Patient Health Questionnaire-9) | 精神科 | Screen for depression and assess severity | 2 |
| `aa_gradient` | Alveolar-arterial (A-a) Oxygen Gradient | 胸腔科 | Calculate A-a gradient to evaluate hypoxemia etiology | 3 |
| `curb65` | CURB-65 Score | 胸腔科 | Predict 30-day mortality in community-acquired pneumonia for disposition decisions | 2 |
| `psi_port` | PSI/PORT Score for Pneumonia | 胸腔科 | Stratify CAP patients by mortality risk to guide disposition | 2 |
| `spesi` | Simplified Pulmonary Embolism Severity Index (sPESI) | 胸腔科 | Risk stratify acute PE patients for 30-day mortality | 2 |
| `das28` | DAS28 (Disease Activity Score 28) | 風濕免疫科 | Measure disease activity in rheumatoid arthritis | 2 |
| `athens_insomnia_scale` | Athens Insomnia Scale (AIS) | sleep medicine | Screen for insomnia using an ICD-based eight-item symptom scale | 2 |
| `berlin_questionnaire` | Berlin Questionnaire | sleep medicine | Estimate obstructive sleep apnea risk using category-based screening | 2 |
| `epworth_sleepiness_scale` | Epworth Sleepiness Scale (ESS) | sleep medicine | Screen for excessive daytime sleepiness and quantify symptom burden | 2 |
| `insomnia_severity_index` | ISI (Insomnia Severity Index) | sleep medicine | Quantify insomnia symptom severity and treatment-response monitoring | 2 |
| `no_sas_score` | NoSAS Score | sleep medicine | Screen for obstructive sleep apnea risk with a simple weighted score | 2 |
| `caprini_vte` | Caprini VTE Risk Assessment Score | 外科 | Stratify VTE risk in surgical patients to guide prophylaxis | 3 |
| `iss` | Injury Severity Score (ISS) | 外科 | Calculate anatomic injury severity for trauma patients | 2 |
| `parkland_formula` | Parkland Formula (Burn Resuscitation) | 外科 | Calculate crystalloid fluid requirements for burn resuscitation | 3 |
| `rts` | Revised Trauma Score (RTS) | 外科 | Physiologic trauma severity scoring for triage and prognosis | 1 |
| `tbsa` | TBSA Calculator (Rule of Nines) | 外科 | Calculate total body surface area burned using Rule of Nines | 2 |
| `triss` | TRISS (Trauma and Injury Severity Score) | 外科 | Calculate trauma survival probability combining RTS and ISS | 2 |
| `osmolar_gap` | Osmolar Gap (Osmolal Gap) | 毒理科 | Calculate difference between measured and calculated osmolality | 3 |
| `bosniak` | Bosniak Classification (Renal Cyst Classification v2019) | 泌尿科 | Classify renal cysts and predict malignancy risk | 2 |
| `iciq_sf` | ICIQ-SF (International Consultation on Incontinence Questionnaire) | 泌尿科 | Assess urinary incontinence severity and impact | 2 |
| `ipss` | IPSS (International Prostate Symptom Score) | 泌尿科 | Assess severity of lower urinary tract symptoms in BPH | 2 |
| `stone_score` | STONE Score (Prediction of Ureteral Stone) | 泌尿科 | Predict probability of ureteral stone in flank pain | 2 |

## 依專科分組

### 麻醉科 (8)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `aldrete_score` | Aldrete Score | Assess post-anesthesia recovery and PACU discharge readiness |
| `apfel_ponv` | Apfel Score for PONV | Predict postoperative nausea and vomiting risk |
| `asa_physical_status` | ASA Physical Status Classification | Assess preoperative patient fitness and anesthetic risk |
| `mabl` | Maximum Allowable Blood Loss (MABL) | Calculate maximum blood loss before transfusion required |
| `mallampati_score` | Mallampati Score (Modified) | Predict difficult intubation based on oropharyngeal visualization |
| `rcri` | Revised Cardiac Risk Index (Lee Index) | Estimate risk of major cardiac complications after non-cardiac surgery |
| `stop_bang` | STOP-BANG Questionnaire | Screen for obstructive sleep apnea risk in surgical patients |
| `transfusion_calc` | Transfusion Volume Calculator | Calculate blood product volume needed for target Hct/Hgb/Plt |

### 心臟科 (11)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `acef_ii` | ACEF II Score | Predict cardiac surgery mortality risk |
| `chads2_va` | CHA₂DS₂-VA Score (2024 ESC) | Estimate stroke risk in AF using 2024 ESC sex-neutral criteria for anticoagulation decisions |
| `chads2_vasc` | CHA₂DS₂-VASc Score | Estimate annual stroke risk in atrial fibrillation for anticoagulation decisions |
| `corrected_qt` | Corrected QT Interval (QTc) | Calculate heart-rate corrected QT interval for arrhythmia risk |
| `euroscore_ii` | EuroSCORE II (Cardiac Surgery Risk) | Predict mortality risk for cardiac surgery |
| `framingham_risk_score` | Framingham Risk Score | Estimate 10-year risk of coronary heart disease |
| `grace_score` | GRACE Score | Stratify mortality risk in acute coronary syndrome |
| `has_bled` | HAS-BLED Score | Assess 1-year major bleeding risk in AF patients on anticoagulation |
| `hfa_peff` | HFA-PEFF Score (Heart Failure with Preserved Ejection Fraction) | Diagnose HFpEF using echocardiographic and biomarker criteria |
| `score2` | SCORE2 (Systematic Coronary Risk Evaluation 2) | Estimate 10-year cardiovascular risk in apparently healthy individuals |
| `timi_stemi` | TIMI Risk Score for STEMI | Predict 30-day mortality in STEMI patients |

### 重症醫學科 (18)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `anion_gap` | Anion Gap | Calculate serum anion gap for metabolic acidosis differential diagnosis |
| `apache_ii` | APACHE II Score | Estimate ICU mortality risk based on acute physiology and chronic health |
| `cam_icu` | CAM-ICU (Confusion Assessment Method for ICU) | Screen for delirium in ICU patients |
| `corrected_sodium` | Corrected Sodium for Hyperglycemia | Calculate true sodium level corrected for hyperglycemic dilution |
| `cpis` | Clinical Pulmonary Infection Score (CPIS) | Assist in VAP diagnosis and guide antibiotic therapy decisions |
| `delta_ratio` | Delta Ratio (Delta Gap) | Identify mixed acid-base disorders in high anion gap metabolic acidosis |
| `icdsc` | ICDSC (Intensive Care Delirium Screening Checklist) | Screen for delirium in ICU patients over 8-24 hour observation period |
| `ideal_body_weight` | Ideal Body Weight (IBW) | Calculate ideal body weight for ventilator settings and drug dosing |
| `murray_lung_injury_score` | Murray Lung Injury Score (LIS) | Quantify severity of acute lung injury and guide ECMO consideration |
| `nrs_2002` | NRS-2002 (Nutritional Risk Screening 2002) | Screen hospitalized patients for nutritional risk |
| `nutric_score` | NUTRIC Score (Nutrition Risk in Critically Ill) | Identify ICU patients who benefit most from nutritional therapy |
| `pf_ratio` | P/F Ratio (PaO2/FiO2) | Calculate P/F ratio for ARDS severity classification |
| `rass` | Richmond Agitation-Sedation Scale (RASS) | Assess level of agitation or sedation in ICU patients |
| `rox_index` | ROX Index | Predict high-flow nasal cannula failure and need for intubation |
| `sirs_criteria` | SIRS Criteria (Systemic Inflammatory Response Syndrome) | Identify systemic inflammatory response syndrome |
| `sofa2_score` | SOFA-2 Score (2025 Update) | Assess organ dysfunction with updated 2025 thresholds based on 3.3M patients |
| `sofa_score` | SOFA Score (Sequential Organ Failure Assessment) | Assess organ dysfunction and predict ICU mortality in sepsis |
| `winters_formula` | Winter's Formula | Predict expected PaCO₂ in metabolic acidosis |

### 皮膚科 (5)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `bsa_dermatology` | BSA for Dermatology (Body Surface Area) | Estimate body surface area affected by skin disease |
| `dlqi` | DLQI (Dermatology Life Quality Index) | Assess quality of life impact of skin disease |
| `pasi` | PASI (Psoriasis Area and Severity Index) | Assess psoriasis severity for treatment decisions |
| `salt_score` | SALT (Severity of Alopecia Tool) | Quantify hair loss severity in alopecia |
| `scorad` | SCORAD (SCORing Atopic Dermatitis) | Assess atopic dermatitis severity |

### 急診醫學科 (9)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `centor_score` | Centor Score (Modified/McIsaac) | Estimate probability of GAS pharyngitis and guide testing/treatment decisions |
| `glasgow_coma_scale` | Glasgow Coma Scale (GCS) | Assess level of consciousness and brain injury severity |
| `heart_score` | HEART Score | Stratify risk of major adverse cardiac events in ED chest pain patients |
| `news2_score` | NEWS2 (National Early Warning Score 2) | Detect clinical deterioration and trigger appropriate clinical response |
| `perc_rule` | PERC Rule (Pulmonary Embolism Rule-out Criteria) | Rule out pulmonary embolism in low-risk patients |
| `qsofa_score` | qSOFA Score (Quick SOFA) | Bedside screening for patients at risk of poor outcomes from sepsis |
| `shock_index` | Shock Index (SI) | Calculate HR/SBP ratio for rapid hemodynamic assessment |
| `wells_dvt` | Wells Score for DVT | Estimate pretest probability of DVT to guide diagnostic workup |
| `wells_pe` | Wells Score for PE | Estimate pretest probability of pulmonary embolism to guide diagnostic workup |

### 內分泌科 (6)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `cas_graves` | CAS (Clinical Activity Score for Graves' Ophthalmopathy) | Assess inflammatory activity in thyroid eye disease |
| `cushingoid_score` | Cushingoid Score (Clinical Features of Cushing's Syndrome) | Assess clinical likelihood of Cushing's syndrome |
| `findrisc` | FINDRISC (Finnish Diabetes Risk Score) | Estimate 10-year risk of type 2 diabetes |
| `frax` | FRAX (Fracture Risk Assessment Tool) | Calculate 10-year fracture risk probability |
| `nds` | NDS (Neuropathy Disability Score) | Assess severity of diabetic peripheral neuropathy |
| `toronto_css` | Toronto CSS (Toronto Clinical Scoring System) | Diagnose and stage diabetic polyneuropathy |

### 家庭醫學科 (4)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `audit` | AUDIT (Alcohol Use Disorders Identification Test) | Assess hazardous drinking and possible alcohol use disorder severity |
| `audit_c` | AUDIT-C (Alcohol Use Disorders Identification Test - Consumption) | Screen for risky alcohol consumption with a three-item score |
| `cage` | CAGE Questionnaire | Identify possible problematic alcohol use with a four-question screen |
| `scoff` | SCOFF Questionnaire | Screen for possible eating disorder with a five-question instrument |

### 腸胃科 (3)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `aims65` | AIMS65 Score | Predict in-hospital mortality for upper GI bleeding |
| `glasgow_blatchford` | Glasgow-Blatchford Score (GBS) | Stratify upper GI bleeding risk and predict need for intervention |
| `rockall_score` | Rockall Score | Predict mortality and rebleeding in upper GI bleeding |

### 老年醫學科 (13)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `barthel_index` | Barthel Index (ADL Assessment) | Assess functional independence in activities of daily living |
| `cfs` | CFS (Clinical Frailty Scale) | Assess frailty in older adults |
| `four_at` | 4AT (Rapid Assessment Test for Delirium) | Rapid delirium screening in hospital settings |
| `frail_scale` | FRAIL Scale | Screen for frailty with a five-domain yes/no questionnaire |
| `gds_15` | GDS-15 (Geriatric Depression Scale - 15 item) | Screen for depression in older adults with a geriatric-focused questionnaire |
| `katz_adl` | Katz ADL Index | Assess independence in basic activities of daily living |
| `lawton_iadl` | Lawton IADL (Instrumental Activities of Daily Living) | Assess higher-order community living independence in older adults |
| `mini_cog` | Mini-Cog | Briefly screen for cognitive impairment using recall and clock drawing |
| `mmse` | MMSE (Mini-Mental State Examination) | Screen for cognitive impairment |
| `mna` | MNA (Mini Nutritional Assessment) | Screen for malnutrition risk in elderly patients |
| `moca` | MoCA (Montreal Cognitive Assessment) | Screen for mild cognitive impairment |
| `sarc_f` | SARC-F | Screen for sarcopenia risk with a brief symptom-based score |
| `tug` | TUG (Timed Up and Go Test) | Assess mobility, balance, and fall risk |

### 婦科 (3)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `epds` | EPDS (Edinburgh Postnatal Depression Scale) | Screen for postnatal and perinatal depression |
| `pop_q` | POP-Q (Pelvic Organ Prolapse Quantification) | Stage pelvic organ prolapse severity |
| `sflt_plgf_ratio` | sFlt-1/PlGF Ratio (Preeclampsia Biomarker) | Predict and diagnose preeclampsia |

### 血液科 (1)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `4ts_hit` | 4Ts Score for HIT | Assess pretest probability of heparin-induced thrombocytopenia |

### 肝膽科 (5)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `child_pugh` | Child-Pugh Score | Assess severity of chronic liver disease (cirrhosis) for prognosis |
| `fib4_index` | FIB-4 Index | Non-invasive assessment of liver fibrosis |
| `lille_model` | Lille Model (Alcoholic Hepatitis Steroid Response) | Assess response to corticosteroid therapy in alcoholic hepatitis |
| `maddrey_df` | Maddrey Discriminant Function (mDF) | Assess severity and prognosis in alcoholic hepatitis |
| `meld_score` | MELD Score | Predict 90-day mortality in end-stage liver disease for transplant prioritization |

### 感染科 (1)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `pitt_bacteremia` | Pitt Bacteremia Score | Predict mortality in gram-negative bacteremia patients |

### 內科 (2)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `charlson_comorbidity_index` | Charlson Comorbidity Index (CCI) | Predict 10-year mortality based on comorbid conditions |
| `corrected_calcium` | Albumin-Corrected Calcium | Correct total calcium for hypoalbuminemia |

### 新生兒科 (1)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `ballard_score` | New Ballard Score | Estimate gestational age of newborns from physical and neuromuscular maturity |

### 腎臟科 (6)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `ckd_epi_2021` | CKD-EPI 2021 (Creatinine, without race) | Calculate estimated glomerular filtration rate (eGFR) |
| `cockcroft_gault` | Cockcroft-Gault Creatinine Clearance | Calculate creatinine clearance for drug dosing adjustments |
| `fena` | Fractional Excretion of Sodium (FENa) | Differentiate prerenal azotemia from acute tubular necrosis |
| `free_water_deficit` | Free Water Deficit | Calculate free water deficit for hypernatremia treatment |
| `kdigo_aki` | KDIGO AKI Staging | Classify acute kidney injury severity by KDIGO criteria |
| `serum_osmolality` | Serum Osmolality (Calculated) | Calculate serum osmolality from sodium, glucose, and BUN |

### 神經科 (7)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `abcd2` | ABCD2 Score | Predict stroke risk after TIA at 2, 7, and 90 days |
| `fisher_grade` | Fisher Grade (Modified Fisher Scale) | Predict vasospasm risk in subarachnoid hemorrhage based on CT findings |
| `four_score` | FOUR Score (Full Outline of UnResponsiveness) | Assess coma severity with detailed brainstem and respiratory evaluation |
| `hunt_hess` | Hunt and Hess Scale | Grade subarachnoid hemorrhage severity and predict surgical risk |
| `ich_score` | ICH Score (Intracerebral Hemorrhage Score) | Predict 30-day mortality in spontaneous intracerebral hemorrhage |
| `modified_rankin_scale` | Modified Rankin Scale (mRS) | Assess disability and dependence after stroke |
| `nihss` | NIH Stroke Scale (NIHSS) | Quantify stroke severity and track neurological changes |

### nursing (1)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `braden_scale` | Braden Scale | Estimate pressure injury risk using six nursing assessment domains |

### nutrition medicine (3)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `conut` | CONUT Score | Screen hospital nutrition status using albumin, lymphocytes, and cholesterol |
| `gnri` | GNRI (Geriatric Nutritional Risk Index) | Estimate nutrition-related risk in older or medically complex adults |
| `mst` | MST (Malnutrition Screening Tool) | Rapidly identify patients at risk of malnutrition with a short screening score |

### 產科 (1)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `bishop_score` | Bishop Score | Assess cervical favorability for labor induction |

### 腫瘤科 (4)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `body_surface_area` | Body Surface Area (BSA) | Calculate BSA for chemotherapy dosing, cardiac indexing, and burn assessment |
| `ecog_performance_status` | ECOG Performance Status | Assess functional status and prognosis in cancer patients |
| `karnofsky_performance_scale` | Karnofsky Performance Scale (KPS) | Quantify functional status and prognosis in cancer and other diseases |
| `mascc_score` | MASCC Risk Index | Identify low-risk febrile neutropenia patients for potential outpatient management |

### 疼痛醫學 (1)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `mme_calculator` | MME Calculator (Morphine Milligram Equivalent) | Calculate total opioid dose in morphine equivalents |

### palliative care (2)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `palliative_performance_scale` | Palliative Performance Scale (PPS) | Assess functional status and prognosis in palliative care |
| `palliative_prognostic_index` | Palliative Prognostic Index (PPI) | Estimate short-term prognosis in palliative care using PPS and bedside symptoms |

### 小兒科 (6)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `apgar_score` | APGAR Score | Newborn assessment at 1 and 5 minutes after birth |
| `pediatric_dosing` | Pediatric Drug Dosing Calculator | Calculate weight-based drug doses for pediatric patients |
| `pediatric_gcs` | Pediatric Glasgow Coma Scale | Age-adapted consciousness assessment for children |
| `pediatric_sofa` | Pediatric SOFA (pSOFA) Score | Age-adapted organ dysfunction assessment for pediatric patients |
| `pews` | Pediatric Early Warning Score (PEWS) | Identify hospitalized children at risk of clinical deterioration |
| `pim3` | Pediatric Index of Mortality 3 (PIM3) | Predict PICU mortality for quality benchmarking |

### 精神科 (9)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `caps5` | CAPS-5 (Clinician-Administered PTSD Scale for DSM-5) | Gold standard diagnostic assessment for PTSD |
| `gad7` | GAD-7 (Generalized Anxiety Disorder 7-item) | Screen for anxiety and assess severity |
| `hama` | HAM-A (Hamilton Anxiety Rating Scale) | Assess anxiety severity (clinician-rated) |
| `hamd` | HAM-D17 (Hamilton Depression Rating Scale) | Assess depression severity (clinician-rated) |
| `madrs` | MADRS (Montgomery-Åsberg Depression Rating Scale) | Assess depression severity with focus on treatment response |
| `pc_ptsd_5` | PC-PTSD-5 (Primary Care PTSD Screen for DSM-5) | Rapidly screen for probable PTSD in primary care and general medical settings |
| `pcl5` | PCL-5 (PTSD Checklist for DSM-5) | Self-report screening and monitoring for PTSD |
| `phq2` | PHQ-2 (Patient Health Questionnaire-2) | Rapidly screen for depressive symptoms in primary and specialty care |
| `phq9` | PHQ-9 (Patient Health Questionnaire-9) | Screen for depression and assess severity |

### 胸腔科 (4)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `aa_gradient` | Alveolar-arterial (A-a) Oxygen Gradient | Calculate A-a gradient to evaluate hypoxemia etiology |
| `curb65` | CURB-65 Score | Predict 30-day mortality in community-acquired pneumonia for disposition decisions |
| `psi_port` | PSI/PORT Score for Pneumonia | Stratify CAP patients by mortality risk to guide disposition |
| `spesi` | Simplified Pulmonary Embolism Severity Index (sPESI) | Risk stratify acute PE patients for 30-day mortality |

### 風濕免疫科 (1)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `das28` | DAS28 (Disease Activity Score 28) | Measure disease activity in rheumatoid arthritis |

### sleep medicine (5)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `athens_insomnia_scale` | Athens Insomnia Scale (AIS) | Screen for insomnia using an ICD-based eight-item symptom scale |
| `berlin_questionnaire` | Berlin Questionnaire | Estimate obstructive sleep apnea risk using category-based screening |
| `epworth_sleepiness_scale` | Epworth Sleepiness Scale (ESS) | Screen for excessive daytime sleepiness and quantify symptom burden |
| `insomnia_severity_index` | ISI (Insomnia Severity Index) | Quantify insomnia symptom severity and treatment-response monitoring |
| `no_sas_score` | NoSAS Score | Screen for obstructive sleep apnea risk with a simple weighted score |

### 外科 (6)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `caprini_vte` | Caprini VTE Risk Assessment Score | Stratify VTE risk in surgical patients to guide prophylaxis |
| `iss` | Injury Severity Score (ISS) | Calculate anatomic injury severity for trauma patients |
| `parkland_formula` | Parkland Formula (Burn Resuscitation) | Calculate crystalloid fluid requirements for burn resuscitation |
| `rts` | Revised Trauma Score (RTS) | Physiologic trauma severity scoring for triage and prognosis |
| `tbsa` | TBSA Calculator (Rule of Nines) | Calculate total body surface area burned using Rule of Nines |
| `triss` | TRISS (Trauma and Injury Severity Score) | Calculate trauma survival probability combining RTS and ISS |

### 毒理科 (1)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `osmolar_gap` | Osmolar Gap (Osmolal Gap) | Calculate difference between measured and calculated osmolality |

### 泌尿科 (4)

| Tool ID | 名稱 | 用途 |
|--------|------|------|
| `bosniak` | Bosniak Classification (Renal Cyst Classification v2019) | Classify renal cysts and predict malignancy risk |
| `iciq_sf` | ICIQ-SF (International Consultation on Incontinence Questionnaire) | Assess urinary incontinence severity and impact |
| `ipss` | IPSS (International Prostate Symptom Score) | Assess severity of lower urinary tract symptoms in BPH |
| `stone_score` | STONE Score (Prediction of Ureteral Stone) | Predict probability of ureteral stone in flank pain |
