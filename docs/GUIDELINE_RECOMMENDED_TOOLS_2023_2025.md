# 📋 2020-2025 臨床指引推薦評分工具總整理

> **最後更新**: 2026-01-08 (Phase 20-23 完成)
> **資料來源**: PubMed 系統性搜尋 + ESC/SCCM/AHA/ACC 官方指引
> **搜尋方法**: PubMed Search MCP 多主題搜尋 (2020-2025)
> **驗證狀態**: ✅ 已使用 PubMed MCP 2026-01-08 再次驗證

本文件整理 2020-2025 年間主要臨床指引中提及的評分工具，並與本系統現有工具進行比對，
以識別缺口並規劃未來開發優先順序。

---

## 📊 整體對照摘要

| 領域 | 指引推薦工具 | 已實作 | 待實作 |
|------|-------------|--------|--------|
| 敗血症/重症 | SOFA, SOFA-2, qSOFA, NEWS2, APACHE II, RASS, CAM-ICU, **ICDSC**, **NUTRIC** | ✅ **9/9** | - |
| 心血管 | CHA₂DS₂-VASc, CHA₂DS₂-VA, HAS-BLED, HEART, GRACE, TIMI, EuroSCORE II, **HFA-PEFF**, **SCORE2** | ✅ **9/9** | - |
| 消化道出血 | Rockall, Glasgow-Blatchford, AIMS65 | ✅ **3/3** | - |
| 肝臟疾病 | Child-Pugh, MELD, MELD-Na, FIB-4, Maddrey DF, Lille Model | ✅ **6/6** | - |
| 腎臟疾病 | KDIGO AKI, CKD-EPI 2021 | ✅ 2/2 | - |
| 肺炎/呼吸 | CURB-65, PSI/PORT, ROX Index, P/F Ratio, **Murray Score** | ✅ **5/5** | - |
| 血栓栓塞 | Wells DVT, Wells PE, Caprini VTE, sPESI | ✅ **4/4** | - |
| 神經科 | GCS, NIHSS, mRS, ABCD2, Hunt & Hess, Fisher, **4AT** | ✅ **7/7** | - |
| 麻醉科 | ASA, RCRI, Mallampati, STOP-BANG, Apfel, Aldrete | ✅ 6/6 | - |
| 創傷 | GCS, ISS, RTS, TRISS | ✅ **4/4** | - |
| 燒傷 | Parkland, TBSA | ✅ **2/2** | - |
| 小兒科 | PEWS, pSOFA (Phoenix 2024) | ✅ **2/2** | - |
| 腫瘤科 | **ECOG PS**, **Karnofsky** | ✅ **2/2** | - |
| 營養科 | **NRS-2002**, NUTRIC | ✅ **2/2** | - |
| 風濕科 | **DAS28** | ✅ **1/1** | - |
| 骨質疏鬆 | **FRAX** | ✅ **1/1** | - |

**總計**: **91 已實作** / 所有主要指引工具完成

---

## ✅ 2026-01-08 實作狀態確認

### 已完成實作的工具 (先前標記為待實作)

| 工具 | 領域 | 狀態 | 原始文獻 PMID |
|------|------|------|---------------|
| **Glasgow-Blatchford (GBS)** | GI | ✅ 已實作 | 11073021 |
| **AIMS65** | GI | ✅ 已實作 | 21907980 |
| **ISS** | Trauma | ✅ 已實作 | 4814394 |
| **Parkland Formula** | Burns | ✅ 已實作 | 4973463 |
| **TBSA (Rule of Nines)** | Burns | ✅ 已實作 | 14805109 |
| **PEWS** | Pediatrics | ✅ 已實作 | 19678924 |
| **pSOFA (Phoenix)** | Pediatrics | ✅ 已實作 | 38245889 |
| **sPESI** | Pulmonology | ✅ 已實作 | 20696966 |
| **Hunt & Hess** | Neurology | ✅ 已實作 | - |
| **Fisher Grade** | Neurology | ✅ 已實作 | - |

---

## 🆕 2026-01-08 PubMed 搜尋新發現

### 新增重要指引 (已整合至系統)

| 指引 | 年份 | PMID | 關鍵推薦 |
|------|------|------|----------|
| **2024 AHA/ACC Perioperative CV Guideline** | 2024 | 39316661 | RCRI, 術前心臟評估流程 |
| **2023 ACC/AHA AF Guideline** | 2024 | 38033089 | CHA₂DS₂-VASc, HAS-BLED |
| **2024 Pediatric Sepsis Consensus** | 2024 | 38245889 | Phoenix Sepsis Score (新!) |
| **2020 HFA-PEFF Algorithm** | 2020 | 32133741 | HFpEF 診斷評分 |
| **2021 ACG UGIB Guideline** | 2021 | 33929377 | **GBS 強烈推薦** |
| **2021 ESGE NVUGIH Guideline** | 2021 | 33567467 | **GBS ≤1 可門診** |
| **2024 ACG ALD Guideline** | 2024 | 38174913 | Maddrey DF, Lille Model |
| **2020 ED-PEWS Validation** | 2020 | 32710839 | ED-PEWS (Lancet) |
| **2022 PODIUM MOD Consensus** | 2022 | 34970683 | Pediatric MOD Scoring |

---

## 🫀 心血管領域 (Cardiology)

### 2024 ESC 心房顫動指引 (AF Guidelines) - 重大更新

> **PMID**: 39217497 | Eur Heart J. 2024;45(36):3314-3414
> Van Gelder IC, et al.

| 評分工具 | 用途 | 狀態 | 指引建議 |
|---------|------|------|----------|
| **CHA₂DS₂-VA** (新版) | 中風風險評估 (性別中性) | ✅ 已實作 | **2024 ESC 推薦** |
| **CHA₂DS₂-VASc** | 中風風險評估 (傳統版) | ✅ 已實作 | 仍可使用 |
| **HAS-BLED** | 出血風險評估 | ✅ 已實作 | **ESC 強烈推薦** |
| DOAC Score | DOAC出血風險 | ❌ 待評估 | 🟢 低 |
| ABC-bleeding | 生物標記出血風險 | ❌ 待評估 | 🟢 低 |

**關鍵更新**:
- 2024 ESC 指引移除性別作為中風風險修飾因子
- 新評分系統 CHA₂DS₂-VA 最高分從 9 分降為 8 分
- 推薦同時使用 CHA₂DS₂-VA + HAS-BLED 平衡中風/出血風險

### 🆕 2023 ACC/AHA/ACCP/HRS AF Guideline (美國版)

> **PMID**: 38033089 | Circulation. 2024;149:e1-e156

與 ESC 指引互補的美國版本，推薦工具相同。

### 🆕 2024 AHA/ACC Perioperative CV Guideline

> **PMID**: 39316661 | Circulation. 2024;150:e351-e442

| 評分工具 | 用途 | 狀態 | 指引建議 |
|---------|------|------|----------|
| **RCRI** | 非心臟手術心臟風險 | ✅ 已實作 | **Class I 推薦** |
| **Functional Capacity (METs)** | 功能狀態評估 | ⚠️ 部分 | 核心流程 |

### 🆕 HFA-PEFF Algorithm for HFpEF (2020)

> **PMID**: 32133741 | Eur J Heart Fail. 2020;22:391-412

| 工具 | 用途 | 狀態 | 優先級 |
|------|------|------|--------|
| **HFA-PEFF Score** | HFpEF 診斷 | ❌ **待實作** | 🟡 中 |

**說明**: 4 步驟診斷流程，含 echocardiographic 和 biomarker 評分

### 急性冠心症 (ACS)

| 工具 | 用途 | 狀態 | 指引推薦 |
|------|------|------|----------|
| **HEART Score** | 急診胸痛風險分層 | ✅ 已實作 | ACEP 推薦 |
| **TIMI STEMI** | STEMI 30天死亡率 | ✅ 已實作 | AHA/ACC |
| **GRACE Score** | ACS 死亡率預測 | ✅ 已實作 | ESC ACS指引 |

### 心臟手術風險

| 工具 | 用途 | 狀態 | 優先級 |
|------|------|------|--------|
| **ACEF II** | 心臟手術死亡率 | ✅ 已實作 | - |
| **EuroSCORE II** | 心臟手術死亡率 | ✅ **已實作** | ✅ 完成 |
| **STS Score** | 心臟手術風險 | ❌ 待評估 | 🟢 低 |
| **TRI-SCORE** | 三尖瓣手術 (新2022) | ❌ 待評估 | 🟢 低 |

**EuroSCORE II 原始文獻**:
- Nashef SAM, et al. Eur J Cardiothorac Surg. 2012;41(4):734-745. **PMID: 22378855**

**近期文獻**:
- PMID: 34586392 - TRI-SCORE (Eur Heart J 2022)
- PMID: 35141860 - EuroSCORE II 八旬老人驗證

### VTE 風險評估

| 評分工具 | 用途 | 狀態 | 指引推薦 |
|---------|------|------|----------|
| **Wells DVT** | DVT 機率評估 | ✅ 已實作 | ASH 推薦 |
| **Wells PE** | PE 機率評估 | ✅ 已實作 | ESC PE 指引 |
| **Caprini VTE** | 手術VTE風險 | ✅ 已實作 | ACCP 推薦 |
| PESI/sPESI | PE 預後 | ❌ 待評估 | 🟡 中 |

---

## 🏥 重症醫學 (Critical Care)

### Surviving Sepsis Campaign 2021 Guidelines

> **PMID**: 34605781 | Crit Care Med. 2021;49(11):e1063-e1143
> Evans L, et al.

| 評分工具 | 用途 | 狀態 | 指引建議強度 |
|---------|------|------|-------------|
| **SOFA** | 器官衰竭評估/Sepsis診斷 | ✅ 已實作 | **強推薦** |
| **qSOFA** | 床邊快速篩檢 | ✅ 已實作 | 有條件推薦 |
| **NEWS2** | 臨床惡化預警 | ✅ 已實作 | 指引提及 |
| **APACHE II** | ICU 死亡率 | ✅ 已實作 | 經典工具 |

**2024 專家共識 (Intensive Care Med 2024)** - PMID: 39531053:
- SOFA 仍為 Sepsis-3 核心診斷標準
- qSOFA 敏感度較低 (37%)，不應單獨作為篩檢工具
- NEWS/MEWS 表現與 SIRS/qSOFA 相當或更好

### SOFA-2 Score (2025 JAMA 新發表)

> **PMID**: 41159833 | JAMA 2025

| 工具 | 用途 | 狀態 | 備註 |
|------|------|------|------|
| **SOFA-2** | 器官衰竭評估 (2025新版) | ✅ 已實作 | **最新版本** |

**SOFA-2 更新要點**:
- 基於 **3.3M 患者數據** 重新校正
- 更新閾值以反映現代 ICU 實踐
- 包含 ECMO 和進階呼吸支持的考量

### ICU 鎮靜與譫妄 (PADIS Guidelines)

| 工具 | 用途 | 狀態 | 指引建議 |
|------|------|------|----------|
| **RASS** | 鎮靜深度評估 | ✅ 已實作 | **強推薦** |
| **CAM-ICU** | ICU 譫妄篩檢 | ✅ 已實作 | **強推薦** |
| **ICDSC** | ICU 譫妄評估 (替代) | ❌ 待實作 | 可接受替代 |

**相關文獻**:
- PMID: 36122204 - SAMDS-ICU 國際調查 (Ann Intensive Care 2022)
- PMID: 32035691 - 鎮靜對譫妄識別的影響 (Aust Crit Care 2020)

---

## 🫁 呼吸/肺臟領域 (Pulmonology)

### 社區型肺炎 (CAP)

| 工具 | 用途 | 狀態 | 指引推薦 |
|------|------|------|----------|
| **CURB-65** | CAP 嚴重度/住院決策 | ✅ 已實作 | BTS/IDSA 推薦 |
| **PSI/PORT** | CAP 死亡率預測 | ✅ 已實作 | IDSA/ATS 推薦 |

### ARDS 相關

| 工具 | 用途 | 狀態 | 參考 |
|------|------|------|------|
| **P/F Ratio** | ARDS 嚴重度 (Berlin) | ✅ 已實作 | Berlin 定義核心 |
| **IBW/TV** | 潮氣量計算 | ✅ 已實作 | ARDSNet 標準 |
| **Murray Score** | 肺損傷嚴重度 | ❌ 待實作 | 🟡 中 |

**重要文獻**:
- PMID: 32870298 - 低潮氣量通氣 RCT (JAMA 2020)

### 高流量氧療 (HFNC)

#### ROX Index - 2020-2025 大量驗證研究

| 工具 | 用途 | 狀態 | 驗證情況 |
|------|------|------|----------|
| **ROX Index** | HFNC 失敗預測 | ✅ 已實作 | **20+ 驗證研究** |

**Meta-Analysis 支持**:
- PMID: 35365110 - ROX Index 系統性回顧 (BMC Pulm Med 2022)
- PMID: 35177091 - ROX Index Meta-analysis (Respir Res 2022)
- PMID: 37605238 - COVID-19 中 ROX 表現 (Crit Care 2023)

---

## 🩸 消化道出血 (GI Bleeding) - ✅ 完成實作

### 🆕 2021 ESGE NVUGIH Guideline (最重要!)

> **PMID**: 33567467 | Endoscopy. 2021;53(3):300-332
> Gralnek IM, et al. European Society of Gastrointestinal Endoscopy

| 工具 | 用途 | 狀態 | **指引建議強度** |
|------|------|------|-----------------|
| **Glasgow-Blatchford (GBS)** | 預內視鏡風險分層 | ✅ **已實作** | 🔴 **強烈推薦** |
| **AIMS65** | UGIB 死亡率 | ✅ **已實作** | 🔴 **推薦** |
| **Rockall Score** | UGIB 死亡率/再出血 | ✅ 已實作 | 內視鏡後評估 |

**ESGE 關鍵建議**:
- **GBS ≤1 分可安全門診追蹤**，不需住院或急診內視鏡
- GBS 為預內視鏡評估首選工具
- Rockall 需內視鏡資訊，適合後續評估

### 🆕 2021 ACG UGIB Guideline

> **PMID**: 33929377 | Am J Gastroenterol. 2021;116(5):899-917
> Laine L, et al. American College of Gastroenterology

**ACG 推薦**:
- 建議使用風險分層工具 (GBS, AIMS65)
- 與 ESGE 一致，支持低風險患者門診管理

### 🆕 2021 ESGE LGIB Guideline (下消化道出血)

> **PMID**: 34062566 | Endoscopy. 2021;53(8):850-868

**LGIB 管理**:
- 無特定評分工具強烈推薦
- 重點在血流動力學穩定性和臨床判斷

### 實作狀態確認 ✅

| 工具 | 原始文獻 | PMID | 指引驗證 |
|------|----------|------|----------|
| Glasgow-Blatchford | Blatchford O, Lancet 2000 | **11073021** | ESGE 2021 |
| AIMS65 | Saltzman JR, GIE 2011 | **21907980** | ACG 2021 |
| Rockall Score | Rockall TA, Gut 1996 | **8855351** | ESGE 2021 |

**關鍵文獻**:
- PMID: 33567467 - **2021 ESGE NVUGIH Guideline** (核心指引)
- PMID: 33929377 - **2021 ACG UGIB Guideline**
- PMID: 39400553 - Rockall vs GBS Meta-analysis (2025)
- PMID: 36542335 - 瑞士多中心驗證 (Eur J Emerg Med 2023)
- PMID: 37629235 - 預內視鏡風險分層回顧 (J Clin Med 2023)

---

## 🧠 神經科 (Neurology)

### 腦外傷 (TBI)

#### 2024 NINDS TBI Classification Recommendations

> **PMID**: 40393504 | J Neurotrauma 2025

| 工具 | 用途 | 狀態 | 指引狀態 |
|------|------|------|----------|
| **GCS** | 意識程度/TBI 嚴重度 | ✅ 已實作 | **核心標準** |
| **GCS-Pupils (GCS-P)** | GCS + 瞳孔反應 | ❌ 待評估 | 新提議 |

**關鍵更新** (2024 NINDS):
- GCS 仍為 TBI 分類核心標準
- 輕度 (13-15), 中度 (9-12), 重度 (≤8)
- 建議結合其他評估 (瞳孔反應、影像學)

### 中風 (Stroke)

| 工具 | 用途 | 狀態 | 指引推薦 |
|------|------|------|----------|
| **NIHSS** | 中風嚴重度量化 | ✅ 已實作 | **AHA/ASA 強推薦** |
| **mRS** | 中風後失能評估 | ✅ 已實作 | 主要預後指標 |
| **ABCD2** | TIA 後中風風險 | ✅ 已實作 | 指引推薦 |

### 蛛網膜下腔出血 (SAH) - Gap

| 工具 | 用途 | 狀態 | 優先級 |
|------|------|------|--------|
| **Hunt & Hess Grade** | SAH 臨床嚴重度 | ❌ 待實作 | 🟡 中 |
| **Fisher Grade** | SAH CT 分級 | ❌ 待實作 | 🟡 中 |
| **WFNS Grade** | SAH 分級 | ❌ 待評估 | 🟢 低 |

---

## 💉 麻醉科 (Anesthesiology)

### 術前評估

| 工具 | 用途 | 狀態 | 指引推薦 |
|------|------|------|----------|
| **ASA Physical Status** | 術前風險分級 | ✅ 已實作 | **核心標準** |
| **RCRI** | 非心臟手術心臟風險 | ✅ 已實作 | AHA/ACC 推薦 |
| **Mallampati** | 困難氣道預測 | ✅ 已實作 | 廣泛使用 |
| **STOP-BANG** | OSA 篩檢 | ✅ 已實作 | AASM 推薦 |

**相關文獻**:
- PMID: 38278596 - 術前心臟檢查更新 (Anesth Clin 2024)
- PMID: 39956581 - RCRI 性別差異研究 (Circ J 2025)

### 困難氣道

| 工具 | 用途 | 狀態 | 參考 |
|------|------|------|------|
| **Mallampati** | 視覺化評估 | ✅ 已實作 | - |
| El-Ganzouri Risk Index | 多因子困難氣道 | ❌ 待評估 | 🟢 低 |
| LEMON | 急診困難氣道 | ❌ 待評估 | 🟢 低 |

### 術後恢復

| 工具 | 用途 | 狀態 | 參考 |
|------|------|------|------|
| **Aldrete Score** | PACU 出院標準 | ✅ 已實作 | 標準工具 |
| **Apfel Score** | PONV 風險 | ✅ 已實作 | PONV 預防指引 |

---

## 🩺 肝臟疾病 (Hepatology)

### 肝硬化相關

| 工具 | 用途 | 狀態 | 指引推薦 |
|------|------|------|----------|
| **Child-Pugh** | 肝硬化嚴重度 | ✅ 已實作 | AASLD 推薦 |
| **MELD** | 肝移植優先順序 | ✅ 已實作 | UNOS 標準 |
| **MELD-Na** | MELD + 鈉 | ✅ 已實作 | 2016 UNOS 採用 |
| **FIB-4** | 非侵入性纖維化 | ✅ 已實作 | AASLD/EASL 推薦 |

### 酒精性肝炎 - ✅ 完成實作

| 工具 | 用途 | 狀態 | 原始文獻 PMID |
|------|------|------|---------------|
| **Maddrey DF** | 酒精性肝炎嚴重度 | ✅ **已實作** | **352788** |
| **Lille Model** | 類固醇反應預測 | ✅ **已實作** | **17518367** |

**原始文獻**:
- Maddrey WC, et al. Gastroenterology. 1978;75(2):193-199. **PMID: 352788**
- Louvet A, et al. Hepatology. 2007;45(6):1348-1354. **PMID: 17518367**

---

## 🫘 腎臟疾病 (Nephrology)

| 工具 | 用途 | 狀態 | 指引推薦 |
|------|------|------|----------|
| **CKD-EPI 2021** | eGFR 計算 (無種族) | ✅ 已實作 | **KDIGO 2021** |
| **KDIGO AKI** | 急性腎損傷分期 | ✅ 已實作 | **KDIGO AKI** |

---

## 👶 小兒科 (Pediatrics) - ✅ 完成實作

### 🆕 2024 國際小兒敗血症共識 (Pediatric Sepsis Consensus)

> **PMID**: 38245889 | JAMA. 2024;331(8):665-674
> Schlapbach LJ, et al. Society of Critical Care Medicine Pediatric Sepsis Definition Task Force

| 工具 | 用途 | 狀態 | 說明 |
|------|------|------|------|
| **Phoenix Sepsis Score (pSOFA)** | 小兒敗血症診斷 | ✅ **已實作** | **2024 新標準** |
| Phoenix-8 Score | 簡化版器官衰竭 | ⚠️ 含於pSOFA | 資源有限環境 |

**Phoenix Criteria 要點**:
- 取代傳統 SIRS 為基礎的小兒敗血症定義
- 包含 4 個器官系統評分 (呼吸、心血管、凝血、神經)
- Phoenix Sepsis Score ≥2 + 感染 = 小兒敗血症

**實作文獻**:
- Schlapbach LJ, et al. JAMA. 2024. **PMID: 38245889** (Phoenix 共識)
- Sanchez-Pinto LN, et al. JAMA. 2024. **PMID: 38245897** (Phoenix 驗證)
- Matics TJ, et al. JAMA Pediatr. 2017. **PMID: 28783810** (pSOFA)

### 🆕 2022 PODIUM MOD Consensus (小兒多重器官衰竭)

> **PMID**: 34970683 | Pediatr Crit Care Med. 2022;23(1):S1-S7

**PODIUM 器官衰竭定義**:
- 標準化小兒多重器官衰竭 (MOD) 標準
- 與 Phoenix Criteria 互補

### 🆕 2020 ED-PEWS 驗證研究 (Lancet)

> **PMID**: 32710839 | Lancet. 2020;395(10232):1274-1284

| 工具 | 用途 | 狀態 | 驗證情況 |
|------|------|------|----------|
| **PEWS (Brighton)** | 小兒惡化預警 | ✅ **已實作** | **Lancet 驗證** |
| Bedside PEWS | 小兒惡化預警 | ⚠️ 類似實作 | 多國驗證 |
| Cardiff PEWS | 小兒惡化預警 | ⚠️ 待評估 | 英國使用 |

**關鍵發現 (Lancet 2020)**:
- 多中心驗證研究確認 PEWS 有效性
- Brighton PEWS 為最廣泛採用版本
- 可有效預測小兒臨床惡化

### 小兒科實作狀態確認 ✅

| 工具 | 原始文獻 | PMID | 指引驗證 |
|------|----------|------|----------|
| **PEWS** | Parshuram CS, Crit Care 2009 | **19678924** | Lancet 2020 |
| **pSOFA (Phoenix)** | Matics TJ, JAMA Pediatr 2017 | **28783810** | Phoenix 2024 |
| Pediatric GCS | Simpson D, Lancet 1982 | - | - |
| PIM-3 | Straney L, PCC 2013 | **23392369** | - |

**關鍵文獻**:
- PMID: 38245889 - **2024 Pediatric Sepsis Consensus** (JAMA)
- PMID: 34970683 - **2022 PODIUM MOD Consensus**
- PMID: 32710839 - **2020 Lancet PEWS Validation**
- PMID: 32710839 - **2020 Lancet PEWS Validation**

---

## 🔥 創傷與燒傷 (Trauma & Burns) - ✅ 主要工具已實作

### 創傷評分 - ✅ 完成實作

| 工具 | 用途 | 狀態 | 原始文獻 PMID |
|------|------|------|---------------|
| **GCS** | TBI 評估 | ✅ 已實作 | 4136544 |
| **ISS** | 創傷嚴重度 | ✅ **已實作** | **4814394** |
| **RTS** | 生理創傷評分 | ✅ **已實作** | **2657085** |
| **TRISS** | 創傷存活預測 | ✅ **已實作** | **3106646** |

**原始文獻**:
- Baker SP, et al. J Trauma. 1974;14(3):187-196. **PMID: 4814394** (ISS)
- Champion HR, et al. J Trauma. 1989;29(5):623-629. **PMID: 2657085** (RTS)
- Boyd CR, et al. J Trauma. 1987;27(4):370-378. **PMID: 3106646** (TRISS)

### 燒傷評估 - ✅ 完成實作

| 工具 | 用途 | 狀態 | 原始文獻 PMID |
|------|------|------|---------------|
| **Parkland Formula** | 燒傷輸液計算 | ✅ **已實作** | **4973463** |
| **TBSA (Rule of 9s)** | 燒傷面積 | ✅ **已實作** | **14805109** |

**燒傷工具原始文獻**:
- Baxter CR. Ann NY Acad Sci. 1968;150(3):874-894. **PMID: 4973463**
- Wallace AB. Lancet. 1951;1(6653):501-504. **PMID: 14805109**

---

## 📈 缺口分析與開發優先順序

### ✅ Phase 19 已完成 (2026-01-08)

| 工具 | 領域 | 原始文獻 PMID | 指引驗證 |
|------|------|---------------|----------|
| Glasgow-Blatchford | GI | 11073021 | ESGE 2021 |
| AIMS65 | GI | 21907980 | ACG 2021 |
| Phoenix/pSOFA | Pediatrics | 38245889 | JAMA 2024 |
| PEWS | Pediatrics | 19678924 | Lancet 2020 |
| ISS | Trauma | 4814394 | ACS |
| Parkland Formula | Burns | 4973463 | ISBI 2016 |
| TBSA | Burns | 14805109 | ABA |
| sPESI | Pulmonology | 20696966 | ESC 2019 |
| Hunt & Hess | Neurology | - | AHA/ASA |
| Fisher Grade | Neurology | - | AHA/ASA |
| **RTS** | Trauma | 2657085 | ATLS |
| **TRISS** | Trauma | 3106646 | ACS |
| **Maddrey DF** | Hepatology | 352788 | 2024 ACG |
| **Lille Model** | Hepatology | 17518367 | 2024 ACG |
| **EuroSCORE II** | Cardiology | 22378855 | ESC/EACTS |

### ✅ Phase 20-23 已完成 (2026-01-08)

| 工具 | 領域 | 原始文獻 PMID | 指引驗證 |
|------|------|---------------|----------|
| **ICDSC** | Critical Care | 11430542 | PADIS Guidelines |
| **Murray Score** | Pulmonology | 3202424 | ELSO/ARDS |
| **HFA-PEFF** | Cardiology | 31504452 | ESC HFA 2020 |
| **ECOG PS** | Oncology | 7165009 | ASCO/ESMO |
| **Karnofsky** | Oncology | 6704925 | WHO/Palliative |
| **4AT** | Geriatrics | 24590568 | NICE Delirium |
| **NRS-2002** | Nutrition | 12765673 | ESPEN 2017 |
| **DAS28** | Rheumatology | 7818570 | ACR/EULAR |
| **NUTRIC** | Critical Care | 22085763 | ASPEN/SCCM |
| **SCORE2** | Cardiology | 34120177 | ESC 2021 |
| **FRAX** | Bone Health | 18292978 | AACE/NOF |

### 🟢 低優先級/待評估

| 工具 | 領域 | 備註 |
|------|------|------|
| APACHE IV | Critical Care | APACHE II 更新版 |
| SAPS 3 | Critical Care | 歐洲常用 |
| STS Score | Cardiac Surgery | 美國常用 |
| GCS-Pupils | Neurology | 新提議 |
| DOAC Score | Cardiology | 新興工具 |

---

## 🆕 未來開發方向：疾病-評分工具知識圖譜

### 問題背景

同一疾病在不同學會/地區可能有不同的評分工具選擇：

| 疾病 | 美國指引 | 歐洲指引 | 其他地區 |
|------|---------|---------|---------|
| **心房顫動中風風險** | CHA₂DS₂-VASc | CHA₂DS₂-VA (2024 新版) | 台灣用 VASc |
| **心臟手術風險** | STS Score | EuroSCORE II | 兩者皆用 |
| **ICU 死亡率** | APACHE II/IV | SAPS 3 | 各有偏好 |
| **敗血症篩檢** | qSOFA | NEWS2 (英國) | 各有偏好 |
| **PE 預後** | PESI | sPESI | 簡化版更常用 |

### 建議實作：Disease-Score Knowledge Graph

```
疾病節點 (Condition)
    │
    ├── 關聯評分工具 (Score Tools)
    │   ├── 工具 A (地區: 美國, 指引: AHA 2024)
    │   ├── 工具 B (地區: 歐洲, 指引: ESC 2024)
    │   └── 工具 C (地區: 國際, 指引: WHO)
    │
    └── 臨床決策點 (Decision Points)
        ├── 診斷
        ├── 風險分層
        ├── 治療選擇
        └── 預後評估
```

### 預期效益

1. **臨床痛點解決**: 醫師可根據地區/學會偏好選擇適當工具
2. **研究價值**: 可比較不同評分系統在同一疾病的表現
3. **教育意義**: 了解為何同一疾病有多種評分方式

### 實作建議 (Phase 24+)

- 擴展 `HighLevelKey` 加入 `guideline_source` 和 `region_preference`
- 建立 `ConditionGraph` 類別管理疾病-工具關係
- 使用 PubMed MCP 搜尋各學會指引推薦

---

## 📚 重要參考文獻

### 主要指引

| 指引 | 年份 | PMID | 推薦工具 |
|------|------|------|----------|
| Surviving Sepsis Campaign | 2021 | 34605781 | SOFA, qSOFA |
| ESC AF Guidelines | 2024 | 39217497 | CHA₂DS₂-VA, HAS-BLED |
| SOFA-2 Development | 2025 | 41159833 | SOFA-2 |
| NINDS TBI Classification | 2025 | 40393504 | GCS |
| ROX Index Meta-Analysis | 2022 | 35365110 | ROX Index |
| UGIB Scoring Meta-Analysis | 2025 | 39400553 | GBS, Rockall, AIMS65 |

### 其他重要文獻

1. Martin-Loeches I, et al. Intensive Care Med. 2024;50(12):2043-2049. PMID: 39531053
2. Chua WL, et al. J Clin Nurs. 2024;33(6):2005-2018. PMID: 38379353
3. Karalapillai D, et al. JAMA. 2020;324:848-858. PMID: 32870298
4. Blatchford O, et al. Lancet. 2000;356(9238):1318-1321. PMID: 11073021 (GBS 原始)
5. Saltzman JR, et al. Gastrointest Endosc. 2011;74(6):1215-1224. PMID: 21907980 (AIMS65 原始)
6. Schlapbach LJ, et al. JAMA. 2024;331(8):665-674. PMID: 38245889 (Phoenix 共識)

---

---

## 🔗 相關文檔

| 文檔 | 說明 |
|------|------|
| [COCHRANE_SCORE_RECOMMENDATIONS.md](./COCHRANE_SCORE_RECOMMENDATIONS.md) | Cochrane 系統性回顧對評分工具的驗證 |
| [SPECIALTY_COVERAGE_GAP_ANALYSIS.md](./SPECIALTY_COVERAGE_GAP_ANALYSIS.md) | 專科覆蓋缺口分析與開發優先順序 |
| [DISEASE_SCORE_KNOWLEDGE_GRAPH.md](./DISEASE_SCORE_KNOWLEDGE_GRAPH.md) | 疾病-評分工具知識圖譜設計 |

---

## 📊 專科覆蓋快速總覽

### ✅ 覆蓋良好 (5+ 工具)
- Critical Care, Cardiology, Anesthesiology, Neurology, Hepatology, Pulmonology

### ⚠️ 部分覆蓋 (1-4 工具)
- Nephrology, Oncology, Nutrition, Rheumatology, Bone Health, Geriatrics, Pediatrics

### ❌ 待開發專科
- **Psychiatry** (PHQ-9, GAD-7, HAM-D) - Cochrane 支持
- **Dermatology** (PASI, SCORAD, DLQI) - Cochrane 支持
- **Endocrinology** (FINDRISC, NDS) - Cochrane 支持
- **Urology** (IPSS, ICIQ-SF) - Cochrane 支持
- **Obstetrics/Gynecology** (Bishop Score, POP-Q)
- **Infectious Disease** (MASCC, Pitt Bacteremia)
- **Orthopedics** (WOMAC, Harris Hip)

詳細分析請參閱 [SPECIALTY_COVERAGE_GAP_ANALYSIS.md](./SPECIALTY_COVERAGE_GAP_ANALYSIS.md)

---

*此文件將隨新指引發布持續維護*
*Generated by PubMed Search MCP + Manual Curation*
*Last Update: 2026-01-08*
