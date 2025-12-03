"""
MCP Server Configuration

Configuration for the Medical Calculator MCP Server.
"""

from dataclasses import dataclass


@dataclass
class McpServerConfig:
    """Configuration for MCP server"""
    
    name: str = "Medical Calculator MCP"
    version: str = "1.0.0"
    json_response: bool = True
    
    # Server network settings (for SSE/HTTP transport)
    host: str = "0.0.0.0"  # Bind to all interfaces for remote access
    port: int = 8000
    
    # Instructions shown to AI agents
    instructions: str = """
Medical Calculator MCP Server - 醫學計算工具 MCP 伺服器

A validated medical calculator toolkit for clinical decision support.

## 🔍 RECOMMENDED USAGE PATTERN

### Path A: By Specialty (Hierarchical Navigation)
```
1. list_specialties()              → Get available specialties
2. list_by_specialty("critical_care") → Get tools in that specialty
3. get_calculator_info("sofa_score")  → Get input parameters
4. calculate_sofa(...)                 → Perform calculation
```

### Path B: By Clinical Context
```
1. list_contexts()                    → Get available contexts
2. list_by_context("severity_assessment") → Get relevant tools
3. get_calculator_info("apache_ii")   → Get input parameters
4. calculate_apache_ii(...)           → Perform calculation
```

### Path C: Direct Access (If You Know the Tool)
```
1. get_calculator_info("news2_score") → Get input parameters
2. calculate_news2(...)               → Perform calculation
```

## 📋 PROMPTS (Clinical Workflows)

Use prompts for guided multi-tool workflows:

| Prompt | Description |
|--------|-------------|
| `sepsis_evaluation` | qSOFA → SOFA → RASS → CAM-ICU workflow |
| `preoperative_risk_assessment` | ASA → RCRI → Mallampati workflow |
| `icu_daily_assessment` | RASS → CAM-ICU → GCS → SOFA daily rounds |
| `pediatric_drug_dosing` | Weight-based dosing + MABL + transfusion |
| `acute_kidney_injury_assessment` | CKD-EPI + AKI staging workflow |

## 🏥 CLINICAL WORKFLOW EXAMPLES

### Sepsis Evaluation:
1. `calculate_qsofa` → Quick bedside screen
2. `calculate_sofa` → Full organ dysfunction (if qSOFA≥2)
3. `calculate_rass` → Sedation level (ICU)
4. `calculate_cam_icu` → Delirium screen (requires RASS first)

### Preoperative Assessment:
1. `calculate_asa_physical_status` → Overall health status
2. `calculate_rcri` → Cardiac risk for non-cardiac surgery
3. `calculate_mallampati` → Difficult airway prediction

### Pediatric/Transfusion:
1. `calculate_pediatric_dosing` → Weight-based drug doses
2. `calculate_mabl` → Maximum allowable blood loss
3. `calculate_transfusion` → Blood product volumes

## 📊 AVAILABLE SPECIALTIES

| Specialty | Example Tools |
|-----------|---------------|
| Critical Care | SOFA, APACHE II, qSOFA, NEWS2, GCS, RASS, CAM-ICU |
| Anesthesiology | ASA, RCRI, Mallampati, MABL |
| Emergency Medicine | qSOFA, NEWS2, GCS |
| Nephrology | CKD-EPI 2021 |
| Pediatrics | Pediatric Dosing, Transfusion |

## ⚠️ IMPORTANT NOTES

1. Each response includes `next_step` to guide you to the next action
2. All calculators cite peer-reviewed references
3. Use `get_calculator_info(tool_id)` to see exact input parameters
4. Input validation errors return clear messages about valid ranges

所有計算器均引用同儕審查論文。每個回應都包含下一步指引。
"""


# Default configuration instance
default_config = McpServerConfig()
