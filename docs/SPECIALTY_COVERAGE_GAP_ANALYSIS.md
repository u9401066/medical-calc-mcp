# 📊 專科評分工具覆蓋缺口分析

> **最後更新**: 2026-01-08
> **分析依據**: 
>   - Specialty enum (76 個專科) vs 已實作計算器 (91 個)
>   - Cochrane Library 系統性回顧
>   - 各學會臨床指引

---

## 📈 總體覆蓋狀況

### ✅ 覆蓋良好的專科 (有多個評分工具)

| 專科 | 已實作工具數 | 代表工具 |
|------|-------------|---------|
| **Critical Care** | 15+ | SOFA, SOFA-2, qSOFA, APACHE II, NEWS2, RASS, CAM-ICU, ICDSC, NUTRIC |
| **Cardiology** | 12+ | CHA₂DS₂-VASc, CHA₂DS₂-VA, HAS-BLED, HEART, GRACE, EuroSCORE II, HFA-PEFF, SCORE2 |
| **Anesthesiology** | 8+ | ASA, RCRI, Mallampati, STOP-BANG, Apfel, Aldrete, MABL |
| **Neurology** | 7+ | GCS, NIHSS, mRS, ABCD2, Hunt & Hess, Fisher, 4AT |
| **Hepatology** | 6 | Child-Pugh, MELD, MELD-Na, FIB-4, Maddrey DF, Lille Model |
| **Pulmonology** | 6+ | CURB-65, PSI/PORT, ROX Index, P/F Ratio, Murray Score, sPESI |
| **Gastroenterology** | 3 | Rockall, Glasgow-Blatchford, AIMS65 |
| **Emergency Medicine** | 5+ | qSOFA, NEWS2, HEART, Wells DVT/PE |
| **Trauma** | 5+ | GCS, ISS, RTS, TRISS, 燒傷 (Parkland, TBSA) |
| **Pediatrics** | 4+ | PEWS, pSOFA (Phoenix), PIM-3, Pediatric GCS |

### ⚠️ 部分覆蓋的專科 (有 1-2 個工具)

| 專科 | 已實作工具 | 缺口建議 |
|------|-----------|---------|
| **Nephrology** | CKD-EPI 2021, KDIGO AKI | Renal Failure Index, AKIN |
| **Oncology** | ECOG PS, Karnofsky | TNM staging helper? |
| **Nutrition** | NRS-2002, NUTRIC | MUST, SGA |
| **Rheumatology** | DAS28 | CDAI, SDAI, ACR/EULAR criteria |
| **Bone Health** | FRAX | NOGG, Garvan |
| **Geriatrics** | 4AT, Karnofsky | Clinical Frailty Scale, MNA |

### ❌ 覆蓋不足或無覆蓋的專科

| 專科 | 建議優先實作的工具 | Cochrane 支持 | 優先級 |
|------|-------------------|---------------|--------|
| **Psychiatry** | PHQ-9, GAD-7, HAM-D, CAPS | ✅ PMID:33956992 | 🔴 高 |
| **Dermatology** | PASI, SCORAD, DLQI | ✅ PMID:35603936 | 🔴 高 |
| **Endocrinology** | FINDRISC, Thyroid Eye Disease CAS | ✅ PMID:32470201 | 🟡 中 |
| **Urology** | IPSS, AUA-SI, ICIQ-SF | ✅ PMID:37070660 | 🟡 中 |
| **Obstetrics** | Bishop Score, TACO Score, sFlt-1/PlGF | ❌ | 🟡 中 |
| **Ophthalmology** | Visual Acuity scales, IOP criteria | ❌ | 🟢 低 |
| **ENT** | Centor/McIsaac, Epworth Sleepiness Scale | ❌ | 🟢 低 |
| **Orthopedics** | WOMAC, Harris Hip Score | ❌ | 🟢 低 |
| **Infectious Disease** | MASCC, Pitt Bacteremia Score | ❌ | 🟡 中 |

---

## 🎯 按優先級建議實作的評分工具

### Phase 24: 精神科評分工具 (Psychiatry Scores)

| 工具 | 全名 | 用途 | Cochrane 支持 |
|------|------|------|---------------|
| **PHQ-9** | Patient Health Questionnaire-9 | 憂鬱症篩檢/追蹤 | PMID:33956992 |
| **GAD-7** | Generalized Anxiety Disorder-7 | 焦慮症篩檢 | - |
| **HAM-D** | Hamilton Depression Rating Scale | 憂鬱症嚴重度 | PMID:33956992 |
| **HAM-A** | Hamilton Anxiety Rating Scale | 焦慮症嚴重度 | - |
| **MADRS** | Montgomery-Åsberg Depression Rating Scale | 憂鬱症追蹤 | - |
| **CAPS** | Clinician-Administered PTSD Scale | PTSD 評估 | PMID:35234292 |
| **PCL-5** | PTSD Checklist for DSM-5 | PTSD 自評 | PMID:35234292 |

### Phase 25: 皮膚科評分工具 (Dermatology Scores)

| 工具 | 全名 | 用途 | Cochrane 支持 |
|------|------|------|---------------|
| **PASI** | Psoriasis Area and Severity Index | 乾癬嚴重度 | PMID:35603936 |
| **SCORAD** | SCORing Atopic Dermatitis | 異位性皮膚炎 | PMID:36373988 |
| **DLQI** | Dermatology Life Quality Index | 皮膚病生活品質 | 多篇 |
| **SALT** | Severity of Alopecia Tool | 禿頭症嚴重度 | PMID:37870096 |
| **BSA** | Body Surface Area | 皮膚受影響面積 | - |

### Phase 26: 內分泌/代謝評分工具

| 工具 | 全名 | 用途 | Cochrane 支持 |
|------|------|------|---------------|
| **FINDRISC** | Finnish Diabetes Risk Score | 第二型糖尿病風險 | PMID:32470201 |
| **NDS/NSS** | Neuropathy Disability/Symptom Score | 糖尿病神經病變 | PMID:38205823 |
| **Toronto CSS** | Toronto Clinical Scoring System | 糖尿病神經病變 | - |
| **CAS** | Clinical Activity Score | 甲狀腺眼病 | - |
| **Cushingoid Score** | Cushingoid Features Score | 庫欣症候群 | - |

### Phase 27: 泌尿科評分工具

| 工具 | 全名 | 用途 | Cochrane 支持 |
|------|------|------|---------------|
| **IPSS/AUA-SI** | International Prostate Symptom Score | 攝護腺肥大症狀 | - |
| **ICIQ-SF** | ICIQ Short Form | 尿失禁評估 | PMID:37070660 |
| **STONE Score** | - | 輸尿管結石 | - |
| **Bosniak Classification** | - | 腎囊腫分類 | - |

### Phase 28: 婦產科評分工具

| 工具 | 全名 | 用途 | Cochrane 支持 |
|------|------|------|---------------|
| **Bishop Score** | - | 子宮頸成熟度 | - |
| **Apgar Score** | - | 新生兒評估 | 已在小兒科? |
| **Edinburgh Postnatal Depression Scale** | EPDS | 產後憂鬱篩檢 | - |
| **sFlt-1/PlGF Ratio** | - | 子癲前症預測 | - |
| **POP-Q** | Pelvic Organ Prolapse Quantification | 骨盆脫垂分期 | PMID:37493538 |

### Phase 29: 感染科評分工具

| 工具 | 全名 | 用途 | 備註 |
|------|------|------|------|
| **MASCC Score** | - | 發熱性嗜中性球低下風險 | 腫瘤感染 |
| **Pitt Bacteremia Score** | - | 菌血症嚴重度 | - |
| **Pneumonia Severity Index (PSI)** | - | 肺炎嚴重度 | ✅ 已有 |
| **CURB-65** | - | 肺炎嚴重度 | ✅ 已有 |

### Phase 30: 老年醫學評分工具

| 工具 | 全名 | 用途 | 備註 |
|------|------|------|------|
| **Clinical Frailty Scale (CFS)** | - | 衰弱評估 | Rockwood |
| **MNA** | Mini Nutritional Assessment | 營養評估 | 老年人 |
| **MMSE** | Mini-Mental State Examination | 認知功能 | Cochrane 驗證 |
| **MoCA** | Montreal Cognitive Assessment | 認知功能 | - |
| **Timed Up and Go (TUG)** | - | 行動能力 | 跌倒風險 |
| **Barthel Index** | - | 日常生活功能 | - |

---

## 📋 現有 Specialty Enum vs 計算器對應

| Specialty Enum | 已有計算器 | 建議補充 |
|----------------|-----------|---------|
| `PSYCHIATRY` | ❌ 無 | PHQ-9, GAD-7, HAM-D |
| `DERMATOLOGY` | ❌ 無 | PASI, SCORAD, DLQI |
| `ENDOCRINOLOGY` | ❌ 無 | FINDRISC, NDS |
| `UROLOGY` | ❌ 無 | IPSS, ICIQ-SF |
| `OPHTHALMOLOGY` | ❌ 無 | VA, IOP |
| `ENT` | ❌ 無 | Centor, Epworth |
| `ORTHOPEDICS` | ❌ 無 | WOMAC, Harris |
| `OBSTETRICS` | ❌ 無 | Bishop, EPDS |
| `GYNECOLOGY` | ❌ 無 | POP-Q |
| `INFECTIOUS_DISEASE` | ❌ 無 | MASCC, Pitt |
| `RHEUMATOLOGY` | ✅ DAS28 | CDAI, SDAI |
| `HEMATOLOGY` | ❌ 無 | IPSS-R (MDS) |
| `ALLERGY_IMMUNOLOGY` | ❌ 無 | Asthma Control Test |

---

## 📊 覆蓋率統計

### 當前狀態
- **Specialty enum 總數**: 76 個
- **有對應計算器的專科**: ~15 個 (~20%)
- **已實作計算器總數**: 91 個
- **計算器分布**: 主要集中在重症、心臟、麻醉、神經、肝臟

### 目標狀態 (Phase 30 完成後)
- **預計新增計算器**: ~35 個
- **總計算器數**: ~126 個
- **專科覆蓋率**: ~40% (30/76)

---

## 🗓️ 建議開發時程

| Phase | 專科 | 工具數 | 預計時間 |
|-------|------|--------|---------|
| Phase 24 | Psychiatry | 7 | 1 週 |
| Phase 25 | Dermatology | 5 | 3 天 |
| Phase 26 | Endocrinology | 5 | 3 天 |
| Phase 27 | Urology | 4 | 2 天 |
| Phase 28 | Obstetrics/Gynecology | 5 | 3 天 |
| Phase 29 | Infectious Disease | 2 | 1 天 |
| Phase 30 | Geriatrics | 6 | 3 天 |

**總計**: ~34 個新工具，約 2-3 週開發時間

---

## 📚 參考資源

### Cochrane 回顧 (已搜尋)
- PMID: 37987526 - CAM-ICU 診斷準確度
- PMID: 34931303 - RCRI + Biomarkers
- PMID: 34313331 - MMSE 診斷準確度
- PMID: 33956992 - Depression prognosis models
- PMID: 35603936 - Psoriasis treatments (PASI)
- PMID: 32470201 - DM screening (FINDRISC)

### 主要指引
- ESC Guidelines (心臟科)
- SCCM/SSC Guidelines (重症)
- APA Guidelines (精神科)
- AAD Guidelines (皮膚科)
- ADA/EASD Guidelines (內分泌)

---

*此文件將隨新開發進度持續更新*
*Generated by Copilot Analysis*
*Last Update: 2026-01-08*
