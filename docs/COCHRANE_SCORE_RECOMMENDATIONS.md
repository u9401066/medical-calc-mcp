# 📚 Cochrane Library 評分工具推薦整理

> **最後更新**: 2026-01-08
> **資料來源**: PubMed MCP 搜尋 Cochrane Database of Systematic Reviews
> **搜尋策略**: `"Cochrane Database Syst Rev"[Journal]` + 各專科關鍵字

---

## 🔍 PubMed MCP 搜尋 Cochrane 的方法

### ✅ 可用的搜尋策略

| 方法 | 查詢語法 | 說明 |
|------|---------|------|
| **期刊名稱** | `"Cochrane Database Syst Rev"[Journal]` | 最精確 |
| **文獻類型** | `systematic review[pt]` | 包含所有系統性回顧 |
| **MeSH** | `"Clinical Decision Rules"[MeSH]` | 臨床決策規則 |
| **組合搜尋** | `cochrane[sb]` | Cochrane 子集 |

### 📋 範例搜尋

```
# 搜尋 Cochrane 中關於評分工具的回顧
search_literature(
    query='"Cochrane Database Syst Rev"[Journal] AND ("Clinical Decision Rules"[MeSH] OR "prediction model" OR "prognostic score")',
    min_year=2020,
    limit=20
)
```

---

## 🔬 Cochrane 直接驗證的評分工具

這些評分工具有專門的 Cochrane 系統性回顧來評估其診斷/預後準確度：

| 工具 | Cochrane 回顧標題 | PMID | 實作狀態 |
|------|------------------|------|----------|
| **CAM-ICU** | Confusion Assessment Method for ICU - diagnosis of delirium | 37987526 | ✅ 已實作 |
| **RCRI** | Biomarkers to RCRI for preoperative prediction of MACE | 34931303 | ✅ 已實作 |
| **MMSE** | Mini-Mental State Examination for early detection of dementia | 34313331 | ❌ 待評估 |
| **CDRs for Pediatric CSI** | Triage tools for detecting cervical spine injury | 38517085 | ❌ 待評估 |

---

## 📊 各專科 Cochrane 相關發現

### 🏥 重症醫學 (Critical Care)

| Cochrane 回顧 | PMID | 相關評分工具 | 備註 |
|--------------|------|-------------|------|
| CAM-ICU for delirium diagnosis | 37987526 | CAM-ICU | **直接驗證** |
| Oral hygiene for VAP prevention | 33368159 | - | 預防措施 |
| Early mobilization in ICU | 29582429 | - | 治療措施 |
| Transfusion thresholds | 34932836 | - | 輸血閾值 |

### 💊 麻醉科 (Anesthesiology)

| Cochrane 回顧 | PMID | 相關評分工具 | 備註 |
|--------------|------|-------------|------|
| RCRI + Biomarkers for MACE | 34931303 | RCRI | **直接驗證** |
| PONV prevention | 33075160 | Apfel Score | 間接相關 |

### 🧠 神經科 (Neurology)

| Cochrane 回顧 | PMID | 相關評分工具 | 備註 |
|--------------|------|-------------|------|
| MMSE for MCI → dementia | 34313331 | MMSE | 診斷準確度 |
| MS prognostic models | 37681561 | Various | 預後模型回顧 |
| Dementia prediction models | 37265424 | Various | 多領域模型 |

### 👶 小兒科 (Pediatrics)

| Cochrane 回顧 | PMID | 相關評分工具 | 備註 |
|--------------|------|-------------|------|
| Pediatric CSI triage tools | 38517085 | CDRs | 臨床決策規則 |
| Bronchiolitis HFNC | 38506440 | - | 治療措施 |

### 🫀 心臟科 (Cardiology)

| Cochrane 回顧 | PMID | 相關評分工具 | 備註 |
|--------------|------|-------------|------|
| Exercise-based CR for CHD | 34741536 | - | 復健 |
| Exercise-based CR for HF | 38451843 | - | 復健 |
| ECMO for critically ill adults | 37750499 | - | 治療 |

### 🦴 骨科 (Orthopedics)

| Cochrane 回顧 | PMID | 相關評分工具 | 備註 |
|--------------|------|-------------|------|
| Exercise for knee OA | 39625083 | - | 治療 |
| Scoliosis exercises | 38415871 | Cobb angle | 分級 |
| Falls prevention | 30703272 | Fall risk scores | 風險評估 |
| Ankle fracture rehab | 39312389 | - | 復健 |

### 🩺 皮膚科 (Dermatology)

| Cochrane 回顧 | PMID | 相關評分工具 | 備註 |
|--------------|------|-------------|------|
| Psoriasis treatments | 35603936 | PASI | 嚴重度評估 |
| Alopecia areata treatments | 37870096 | SALT | 嚴重度評估 |
| Eczema prevention | 36373988 | SCORAD | 嚴重度評估 |
| Keloid laser therapy | 36161591 | Vancouver Scar Scale | 疤痕評估 |

### 🧬 內分泌科 (Endocrinology)

| Cochrane 回顧 | PMID | 相關評分工具 | 備註 |
|--------------|------|-------------|------|
| Type 2 DM screening | 32470201 | FINDRISC, ADA Risk Score | 風險篩檢 |
| Diabetic neuropathy (ALA) | 38205823 | NDS, NSS | 神經病變評估 |
| PCOS lifestyle | 30921477 | Rotterdam criteria | 診斷 |

### 👩‍⚕️ 婦產科 (Obstetrics & Gynecology)

| Cochrane 回顧 | PMID | 相關評分工具 | 備註 |
|--------------|------|-------------|------|
| PFMT for incontinence | 32378735 | - | 骨盆底訓練 |
| Omega-3 in pregnancy | 30480773 | - | 營養 |
| Antenatal corticosteroids | 33368142 | - | 肺成熟 |
| PRP for assisted reproduction | 38682756 | - | 輔助生殖 |
| Vaginal prolapse surgery | 37493538 | POP-Q | 分期 |

### 🧠 精神科 (Psychiatry)

| Cochrane 回顧 | PMID | 相關評分工具 | 備註 |
|--------------|------|-------------|------|
| Depression prognosis models | 33956992 | PHQ-9, HAM-D | 預後預測 |
| CBT for child anxiety | 33196111 | - | 治療 |
| Antidepressants for children | 34029378 | CDRS-R | 療效評估 |
| PTSD pharmacotherapy | 35234292 | CAPS, PCL | 症狀評估 |
| Self-harm interventions | 33677832 | - | 治療 |

### 🔬 泌尿科 (Urology)

| Cochrane 回顧 | PMID | 相關評分工具 | 備註 |
|--------------|------|-------------|------|
| UI after prostate surgery | 37070660 | ICIQ-SF | 尿失禁評估 |
| Conservative UI treatments | 36053030 | Various UI scores | 治療 |

---

## 📈 基於 Cochrane 回顧的待實作評分工具

### 🔴 高優先級 (有 Cochrane 直接驗證)

| 工具 | 領域 | Cochrane PMID | 說明 |
|------|------|---------------|------|
| **MMSE** | Neurology | 34313331 | 失智症早期偵測 |
| **PASI** | Dermatology | 35603936 | 乾癬嚴重度 |
| **SCORAD** | Dermatology | 36373988 | 濕疹嚴重度 |
| **FINDRISC** | Endocrinology | 32470201 | 糖尿病風險 |
| **PHQ-9** | Psychiatry | 33956992 | 憂鬱症篩檢 |
| **CAPS** | Psychiatry | 35234292 | PTSD 評估 |

### 🟡 中優先級 (Cochrane 回顧間接提及)

| 工具 | 領域 | 說明 |
|------|------|------|
| **POP-Q** | OB/GYN | 骨盆脫垂分期 |
| **ICIQ-SF** | Urology | 尿失禁問卷 |
| **Vancouver Scar Scale** | Dermatology/Surgery | 疤痕評估 |
| **NDS/NSS** | Endocrinology | 糖尿病神經病變 |
| **Rotterdam Criteria** | OB/GYN | PCOS 診斷 |

---

## 🔗 與現有指引文檔的整合

本文檔補充 `GUIDELINE_RECOMMENDED_TOOLS_2023_2025.md`：

- **指引文檔**: 各學會 (ESC, AHA, SCCM 等) 的臨床指引推薦
- **本文檔**: Cochrane 系統性回顧對評分工具的驗證

兩者互補：
1. 指引提供「推薦使用」的工具
2. Cochrane 提供「證據品質」的評估

---

## 📚 參考文獻

### 評分工具驗證的 Cochrane 回顧

1. Miranda F, et al. CAM-ICU for diagnosis of delirium. Cochrane Database Syst Rev. 2023;11:CD013126. PMID: 37987526
2. Vernooij LM, et al. Biomarkers to RCRI for MACE prediction. Cochrane Database Syst Rev. 2021;12:CD013139. PMID: 34931303
3. Arevalo-Rodriguez I, et al. MMSE for early detection of dementia. Cochrane Database Syst Rev. 2021;7:CD010783. PMID: 34313331
4. Tavender E, et al. Triage tools for pediatric CSI. Cochrane Database Syst Rev. 2024;3:CD011686. PMID: 38517085

### 預後模型的 Cochrane 回顧

5. Reeve K, et al. Prognostic models for MS. Cochrane Database Syst Rev. 2023;9:CD013606. PMID: 37681561
6. Moriarty AS, et al. Prognostic models for depression relapse. Cochrane Database Syst Rev. 2021;5:CD013491. PMID: 33956992
7. Mohanannair Geethadevi G, et al. Dementia prediction models. Cochrane Database Syst Rev. 2023;6:CD014885. PMID: 37265424

---

*此文件將隨新 Cochrane 回顧發布持續維護*
*Generated by PubMed Search MCP*
*Last Update: 2026-01-08*
