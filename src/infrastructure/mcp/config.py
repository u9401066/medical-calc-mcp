"""
MCP Server Configuration

Configuration for the Medical Calculator MCP Server.

Supports SSL/TLS configuration via environment variables or constructor arguments:
    - SSL_ENABLED: Enable SSL/TLS (default: false)
    - SSL_KEYFILE: Path to SSL private key file
    - SSL_CERTFILE: Path to SSL certificate file
    - SSL_CA_CERTS: Path to CA certificates file (optional, for client verification)
    - SSL_CERT_REQUIRED: Require client certificate (default: false)
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SslConfig:
    """SSL/TLS Configuration for secure connections"""

    enabled: bool = False
    keyfile: Optional[str] = None
    certfile: Optional[str] = None
    ca_certs: Optional[str] = None
    cert_required: bool = False

    @classmethod
    def from_env(cls) -> "SslConfig":
        """
        Create SSL configuration from environment variables.

        Environment Variables:
            SSL_ENABLED: Enable SSL/TLS ("true", "1", "yes" to enable)
            SSL_KEYFILE: Path to SSL private key file
            SSL_CERTFILE: Path to SSL certificate file
            SSL_CA_CERTS: Path to CA certificates file (optional)
            SSL_CERT_REQUIRED: Require client certificate ("true", "1", "yes")

        Returns:
            SslConfig instance

        Example:
            SSL_ENABLED=true SSL_KEYFILE=/path/to/key.pem SSL_CERTFILE=/path/to/cert.pem
        """
        enabled_str = os.environ.get("SSL_ENABLED", "false").lower()
        enabled = enabled_str in ("true", "1", "yes", "on")

        cert_required_str = os.environ.get("SSL_CERT_REQUIRED", "false").lower()
        cert_required = cert_required_str in ("true", "1", "yes", "on")

        return cls(
            enabled=enabled,
            keyfile=os.environ.get("SSL_KEYFILE"),
            certfile=os.environ.get("SSL_CERTFILE"),
            ca_certs=os.environ.get("SSL_CA_CERTS"),
            cert_required=cert_required,
        )

    def validate(self) -> None:
        """
        Validate SSL configuration.

        Raises:
            ValueError: If SSL is enabled but keyfile or certfile is missing
        """
        if self.enabled:
            if not self.keyfile:
                raise ValueError("SSL_KEYFILE is required when SSL is enabled")
            if not self.certfile:
                raise ValueError("SSL_CERTFILE is required when SSL is enabled")
            if not os.path.exists(self.keyfile):
                raise ValueError(f"SSL keyfile not found: {self.keyfile}")
            if not os.path.exists(self.certfile):
                raise ValueError(f"SSL certfile not found: {self.certfile}")
            if self.ca_certs and not os.path.exists(self.ca_certs):
                raise ValueError(f"SSL CA certs file not found: {self.ca_certs}")


@dataclass
class McpServerConfig:
    """Configuration for MCP server"""

    name: str = "Medical Calculator MCP"
    version: str = "1.2.0"
    json_response: bool = True

    # Server network settings (for SSE/HTTP transport)
    host: str = "0.0.0.0"  # Bind to all interfaces for remote access
    port: int = 8000

    # SSL/TLS configuration
    ssl: SslConfig = field(default_factory=SslConfig)

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
