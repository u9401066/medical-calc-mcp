# MCP 測試範例 | MCP Test Examples

這份文件提供實際可在 VS Code Copilot Chat 中測試的範例指令。

This document provides practical examples to test in VS Code Copilot Chat.

---

## 🔍 工具探索 | Tool Discovery (High Level)

### 1. 列出所有專科 | List All Specialties
```
@medical-calc-mcp 列出所有可用的醫學專科
```

```
@medical-calc-mcp list all available medical specialties
```

### 2. 列出所有臨床情境 | List All Clinical Contexts
```
@medical-calc-mcp 列出所有臨床使用情境
```

```
@medical-calc-mcp what clinical contexts are available?
```

### 3. 依專科查詢工具 | List Tools by Specialty
```
@medical-calc-mcp 列出重症加護科的所有計算工具
```

```
@medical-calc-mcp 列出心臟科可用的評分工具
```

```
@medical-calc-mcp show me all anesthesiology calculators
```

### 4. 依臨床情境查詢 | List Tools by Context
```
@medical-calc-mcp 術前評估可以用哪些工具？
```

```
@medical-calc-mcp 有哪些工具可用於嚴重度評估？
```

```
@medical-calc-mcp what tools can help with prognosis assessment?
```

### 5. 關鍵字搜尋 | Keyword Search
```
@medical-calc-mcp 搜尋 sepsis 相關工具
```

```
@medical-calc-mcp 搜尋腎功能相關的計算器
```

```
@medical-calc-mcp search for stroke risk calculators
```

### 6. 取得工具詳細資訊 | Get Calculator Info
```
@medical-calc-mcp 告訴我 SOFA score 的詳細資訊和所需參數
```

```
@medical-calc-mcp CHA2DS2-VASc 需要哪些輸入參數？
```

```
@medical-calc-mcp explain the HEART score and its inputs
```

---

## 🧮 計算器使用 | Calculator Usage

### Critical Care | 重症加護

#### SOFA Score (Sepsis-3)
```
@medical-calc-mcp 計算 SOFA score:
- PaO2/FiO2 = 200
- Platelets = 80
- Bilirubin = 2.5 mg/dL
- GCS = 13
- Creatinine = 2.0 mg/dL
- 使用 dopamine 5 mcg/kg/min
```

#### qSOFA (Quick Sepsis)
```
@medical-calc-mcp 計算 qSOFA:
病人呼吸 24 次/分、血壓 90/60、意識混亂
```

#### GCS (Glasgow Coma Scale)
```
@medical-calc-mcp 計算 GCS:
眼睛對聲音有反應(3)、言語混亂(4)、可定位疼痛(5)
```

#### NEWS2
```
@medical-calc-mcp 計算 NEWS2:
RR=22, SpO2=94% on room air, Temp=38.5°C, SBP=100, HR=95, Alert
```

### Cardiology | 心臟科

#### CHA₂DS₂-VASc (AF Stroke Risk)
```
@medical-calc-mcp 計算心房顫動中風風險:
75歲女性，有高血壓和糖尿病，無中風病史
```

#### CHA₂DS₂-VA (2024 ESC 新版)
```
@medical-calc-mcp 用 2024 ESC 新版 CHA2DS2-VA 計算:
68歲男性，心衰竭 EF 35%，高血壓，曾經 TIA
```

#### HEART Score (Chest Pain)
```
@medical-calc-mcp 評估急診胸痛病人 MACE 風險:
- 病史高度可疑
- ECG 有 ST 壓低
- 55歲
- 有 3 個以上危險因子
- Troponin 輕微升高 (1-3x ULN)
```

### Emergency Medicine | 急診醫學

#### Wells PE Score
```
@medical-calc-mcp 評估肺栓塞風險:
病人有 DVT 症狀、心跳 105、近期手術、無咳血
```

#### Wells DVT Score
```
@medical-calc-mcp 評估深層靜脈栓塞風險:
小腿腫脹 >3cm、有壓痛、有凹陷性水腫、無其他更可能診斷
```

### Pulmonology | 胸腔科

#### CURB-65 (Pneumonia)
```
@medical-calc-mcp 評估社區型肺炎嚴重度:
70歲、意識清楚、BUN 25 mg/dL、血壓 85/50、呼吸 32 次/分
```

#### PSI/PORT Score
```
@medical-calc-mcp 計算肺炎嚴重度指數:
65歲男性、護理之家住民、有心衰竭、意識正常、呼吸 28 次/分、血壓正常
```

### Preoperative | 術前評估

#### RCRI (Cardiac Risk)
```
@medical-calc-mcp 評估非心臟手術的心臟風險:
要做腹部大手術、有缺血性心臟病、用胰島素控制糖尿病
```

#### ASA Physical Status
```
@medical-calc-mcp 病人有控制良好的高血壓和第二型糖尿病，ASA 分級是多少？
```

#### Caprini VTE Score
```
@medical-calc-mcp 計算術後 VTE 風險:
65歲、BMI 32、要做膝關節置換、有靜脈曲張
```

### Nephrology | 腎臟科

#### CKD-EPI 2021
```
@medical-calc-mcp 計算 eGFR:
65歲女性、肌酸酐 1.5 mg/dL
```

### Hepatology | 肝膽科

#### MELD Score
```
@medical-calc-mcp 計算 MELD 分數:
Bilirubin 4.5 mg/dL、INR 1.8、Creatinine 1.5 mg/dL、Sodium 132 mEq/L
```

---

## 🔄 臨床工作流程 | Clinical Workflows

### Sepsis Workup (Sepsis-3 流程)
```
@medical-calc-mcp 幫我完整評估一位疑似敗血症的 ICU 病人:
- 生命徵象: RR 24, BP 90/60, 意識混亂
- Lab: PaO2/FiO2 250, Plt 100, Bili 1.8, Cr 2.2
- 使用 norepinephrine 0.1 mcg/kg/min
- GCS E3V4M5

請依序計算 qSOFA、SOFA，並評估是否符合 Sepsis-3 診斷標準
```

### Preoperative Assessment (術前評估流程)
```
@medical-calc-mcp 完整術前風險評估:
72歲男性，要做髖關節置換手術
病史: 冠心病(放過支架)、第二型糖尿病(用胰島素)、高血壓
Cr 1.8 mg/dL

請評估 ASA 分級、RCRI 心臟風險、Caprini VTE 風險
```

### AF Anticoagulation Decision (心房顫動抗凝決策)
```
@medical-calc-mcp 協助心房顫動抗凝決策:
78歲女性，新診斷 AF，有高血壓控制中，曾經小中風

請計算 CHA2DS2-VASc 並給予抗凝建議
```

### Chest Pain Workup (胸痛評估)
```
@medical-calc-mcp 急診胸痛病人風險分層:
52歲男性，典型心絞痛症狀
ECG: ST 輕微壓低
Risk factors: 抽菸、高血壓、糖尿病、家族史
Troponin: 2x ULN

請計算 HEART score 並建議處置
```

---

## 📚 進階查詢 | Advanced Queries

### 比較不同工具
```
@medical-calc-mcp CURB-65 和 PSI/PORT 有什麼差別？何時用哪個？
```

### 查詢文獻來源
```
@medical-calc-mcp SOFA score 的原始文獻出處是什麼？
```

### 工具參數說明
```
@medical-calc-mcp 解釋 APACHE II 的 A-a gradient 參數怎麼計算
```

### 臨床指引整合
```
@medical-calc-mcp 根據 Sepsis-3 指引，qSOFA 和 SOFA 的關係是什麼？
```

---

## 💡 Tips | 使用技巧

1. **使用中文或英文都可以** - MCP 工具支援雙語
2. **提供完整數值** - 計算時提供所有必要參數會得到更準確結果
3. **可以問工具探索問題** - 不確定用哪個工具時，先問「有哪些工具可以...」
4. **支援工作流程** - 可以一次問多個計算器的組合評估
5. **參考文獻** - 每個計算結果都會附上原始論文引用

---

## 📊 可用工具統計 | Available Tools

| Category | Count | Examples |
|----------|-------|----------|
| Discovery Tools | 7 | list_specialties, search_calculators, get_calculator_info |
| Critical Care | 7 | SOFA, qSOFA, NEWS2, GCS, RASS, CAM-ICU, APACHE II |
| Cardiology | 3 | CHA₂DS₂-VASc, CHA₂DS₂-VA, HEART |
| Emergency | 2 | Wells PE, Wells DVT |
| Pulmonology | 2 | CURB-65, PSI/PORT |
| Anesthesia | 6 | ASA, RCRI, Mallampati, MABL, Transfusion, Caprini |
| Nephrology | 1 | CKD-EPI 2021 |
| Hepatology | 1 | MELD |
| Pediatrics | 1 | Pediatric Dosing |

**Total: 30 MCP Tools (7 Discovery + 23 Calculators)**
