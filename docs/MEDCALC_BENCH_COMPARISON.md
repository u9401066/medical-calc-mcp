# MedCalc-Bench 對照分析

> **更新日期**: 2026-02-05
> **MedCalc-Bench**: NeurIPS 2024 Datasets and Benchmark Track Oral (arXiv:2406.12036)
> **目的**: 評估我們的計算器覆蓋率並規劃 Benchmark 整合

---

## 📊 概覽

| 指標 | MedCalc-Bench | 本專案 |
|------|---------------|--------|
| **計算器數量** | 55 | 121 |
| **測試案例** | 1,100 (test) + 10,543 (train) | 1,752 tests |
| **授權** | CC-BY-SA 4.0 | Apache 2.0 |
| **GitHub** | ncbi-nlp/MedCalc-Bench | u9401066/medical-calc-mcp |

---

## 🔄 計算器對照表

### ✅ 我們已實作的 (覆蓋 MedCalc-Bench)

| MedCalc-Bench Calculator | 本專案對應 | 狀態 |
|--------------------------|-----------|------|
| anion_gap | `anion_gap` | ✅ |
| apache_ii | `apache_ii` | ✅ |
| bsa_calculator | `body_surface_area` | ✅ |
| calcium_correction | `corrected_calcium` | ✅ |
| caprini_score | `caprini_vte` | ✅ |
| cardiac_risk_index | `rcri` | ✅ |
| centor_score | `centor_score` | ✅ |
| cha2ds2_vasc_score | `chads2_vasc` | ✅ |
| child_pugh_score | `child_pugh` | ✅ |
| ckd-epi_2021_creatinine | `ckd_epi_2021` | ✅ |
| creatinine_clearance | `cockcroft_gault` | ✅ |
| curb_65 | `curb65` | ✅ |
| delta_ratio | `delta_ratio` | ✅ |
| fibrosis_4 | `fib4_index` | ✅ |
| free_water_deficit | `free_water_deficit` | ✅ |
| glasgow_coma_score | `gcs` | ✅ |
| glasgow_bleeding_score | `glasgow_blatchford` | ✅ |
| has_bled_score | `has_bled` | ✅ |
| heart_score | `heart_score` | ✅ |
| ideal_body_weight | `ideal_body_weight` | ✅ |
| meldna | `meld_score` (包含 MELD-Na) | ✅ |
| psi_score | `psi_port` | ✅ |
| qt_calculator_bazett | `corrected_qt` | ✅ |
| sodium_correction_hyperglycemia | `corrected_sodium` | ✅ |
| sofa | `sofa_score` | ✅ |
| wells_criteria_dvt | `wells_dvt` | ✅ |
| wells_criteria_pe | `wells_pe` | ✅ |

**覆蓋數: 27/55 = 49%**

---

### ⚠️ 我們尚未實作的 (MedCalc-Bench 有)

| MedCalc-Bench Calculator | 說明 | 優先級 |
|--------------------------|------|--------|
| adjusted_body_weight | 調整體重計算 | 🟡 中 |
| albumin_corrected_anion | 白蛋白校正陰離子間隙 | 🟢 低 |
| albumin_corrected_delta_gap | 白蛋白校正 Delta Gap | 🟢 低 |
| albumin_delta_ratio | 白蛋白 Delta Ratio | 🟢 低 |
| bmi_calculator | BMI 計算 | 🟡 中 |
| cci | Charlson Comorbidity Index | 🔴 高 |
| compute_fena | 鈉排泄分數 (FENa) | 🔴 高 |
| delta_gap | Delta Gap | 🟢 低 (我們有 delta_ratio) |
| estimated_conception_date | 預估受孕日 | 🟢 低 |
| estimated_due_date | 預產期 | 🟡 中 |
| estimated_gestational_age | 妊娠週數 | 🟡 中 |
| feverpain | FeverPAIN Score | 🟢 低 |
| framingham_risk_score | Framingham 心血管風險 | 🔴 高 |
| homa_ir | HOMA-IR 胰島素阻抗 | 🟡 中 |
| ldl_calculated | LDL 計算 (Friedewald) | 🟡 中 |
| maintenance_fluid_calc | 維持輸液計算 | 🟡 中 |
| map (mean_arterial_pressure) | 平均動脈壓 | 🟡 中 |
| mdrd_gfr | MDRD GFR | 🟢 低 (CKD-EPI 更新) |
| mme | 嗎啡毫克當量 | 🔴 高 |
| perc_rule | PERC Rule (PE 排除) | 🔴 高 |
| qt_calculator_framingham | QTc Framingham | 🟢 低 |
| qt_calculator_fredericia | QTc Fredericia | 🟡 中 |
| qt_calculator_hodges | QTc Hodges | 🟢 低 |
| qt_calculator_rautaharju | QTc Rautaharju | 🟢 低 |
| sOsm (serum_osmolality) | 血清滲透壓 | 🔴 高 (我們有 osmolar_gap) |
| sirs_criteria | SIRS 標準 | 🔴 高 |
| steroid_conversion | 類固醇換算 | 🟡 中 |
| target_weight | 目標體重 | 🟢 低 |
| age_conversion | 年齡轉換 | 🟢 低 |
| height_conversion | 身高轉換 | 🟢 低 |
| weight_conversion | 體重轉換 | 🟢 低 |
| convert_temperature | 溫度轉換 | 🟢 低 |

**缺少數: 28/55**

---

## 🎯 優先實作建議

### P0 - 高優先級 (臨床常用)

| Calculator | 理由 | 預估時間 |
|------------|------|---------|
| **cci** (Charlson Comorbidity Index) | 共病指數，廣泛使用 | 2h |
| **fena** (FENa) | 急性腎損傷鑑別診斷 | 1h |
| **framingham_risk_score** | CVD 風險評估標準 | 2h |
| **mme** (Morphine Milligram Equivalent) | 鴉片類藥物換算 | 1h |
| **perc_rule** | PE 排除規則 | 1h |
| **sirs_criteria** | 敗血症舊標準，仍常用 | 1h |
| **serum_osmolality** | 滲透壓計算 | 1h |

### P1 - 中優先級

| Calculator | 理由 |
|------------|------|
| bmi | 基礎計算 |
| estimated_due_date | 產科常用 |
| homa_ir | 糖尿病評估 |
| ldl_calculated | 心血管風險 |
| maintenance_fluid | 輸液計算 |
| map | 血壓評估 |
| steroid_conversion | 用藥換算 |

---

## 📋 測試整合計畫

### Phase B1: Dataset Integration

```bash
# 1. 下載 MedCalc-Bench dataset
git clone https://github.com/ncbi-nlp/MedCalc-Bench.git
cd MedCalc-Bench/datasets

# 2. 解壓測試集
unzip test_data.csv.zip

# 3. 篩選我們支援的計算器
# (需要寫 script 對應 calculator_id → tool_id)
```

### Phase B2: Evaluation Framework

```python
# scripts/medcalc_bench_eval.py (規劃中)
"""
MedCalc-Bench Evaluation Script

1. 載入測試資料集
2. 對每個 instance:
   - 解析 Patient Note
   - 提取 Relevant Entities
   - 呼叫對應 calculator
   - 比較 Ground Truth
3. 計算準確率
"""
```

---

## 📈 預期改進

| 指標 | GPT-4 Direct | GPT-4 + Medical-Calc-MCP |
|------|-------------|--------------------------|
| **Overall Accuracy** | ~50% | >95% (預期) |
| **Parameter Extraction** | Variable | 100% (validated) |
| **Calculation Accuracy** | ~60% | 100% (symbolic) |
| **Literature Citation** | 0% | 100% |

---

## 參考資料

- **Paper**: arXiv:2406.12036
- **GitHub**: https://github.com/ncbi-nlp/MedCalc-Bench
- **HuggingFace**: https://huggingface.co/datasets/nsk7153/MedCalc-Bench-Verified
- **License**: CC-BY-SA 4.0

---

*此文件追蹤 MedCalc-Bench 整合進度*
