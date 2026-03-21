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

from ...shared.project_metadata import get_project_version


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
    version: str = field(default_factory=get_project_version)
    json_response: bool = True

    # Server network settings (for SSE/HTTP transport)
    host: str = "0.0.0.0"  # nosec B104 - MCP SSE/HTTP mode supports remote/container access by design
    port: int = 8000

    # SSL/TLS configuration
    ssl: SslConfig = field(default_factory=SslConfig)

    # Instructions shown to AI agents
    instructions: str = """
Medical Calculator MCP Server - 醫學計算工具 MCP 伺服器

A validated medical calculator toolkit for clinical decision support.

## SYSTEM RULES FOR AGENTS

Follow this exact sequence unless the user already gave a verified canonical tool_id and complete params.

1. Start with `discover(...)` to find the right tool category or tool_id.
2. Always call `get_tool_schema(tool_id)` before `calculate(tool_id, params)`.
3. Never invent parameter names, enums, units, or boolean meanings.
4. If a tool call returns `guidance`, `suggestions`, `resolved_value`, or `component_scores.param_template`, use them for the next retry.
5. If unsure between multiple tools, prefer `discover(by="keyword", value="...")` or `get_related_tools(tool_id)` before calculating.

## DEFAULT WORKFLOW FOR SMALL / WEAKER MODELS

```python
# SAFE PATH: use this unless you are certain
1. discover(by="keyword", value="clinical problem")
2. get_tool_schema("tool_id_from_discover")
3. calculate("tool_id_from_schema", {"exact_param_name": value})
```

## WHEN INPUTS ARE IMPERFECT

- Tool ids may be fuzzy-resolved, but still prefer canonical ids returned by `discover()` or `get_tool_schema()`.
- Empty or invalid params should trigger a retry using the returned `guidance` and `param_template`.
- Do not skip schema inspection just because a tool name looks obvious.

## 📋 PROMPTS (Clinical Workflows)

Use prompts for guided multi-tool workflows:

| Prompt | Description |
|--------|-------------|
| `tool_usage_playbook` | Strong operating rules for smaller models before any calculation |
| `sepsis_evaluation` | qSOFA → SOFA → RASS → CAM-ICU workflow |
| `preoperative_risk_assessment` | ASA → RCRI → Mallampati workflow |
| `icu_daily_assessment` | RASS → CAM-ICU → GCS → SOFA daily rounds |
| `pediatric_drug_dosing` | Weight-based dosing + MABL + transfusion |
| `acute_kidney_injury_assessment` | CKD-EPI + AKI staging workflow |

## 🏥 CLINICAL WORKFLOW EXAMPLES

### Sepsis Evaluation:
1. `qsofa_score` via `get_tool_schema('qsofa_score')` → `calculate('qsofa_score', params)`
2. `sofa_score` via `get_tool_schema('sofa_score')` → `calculate('sofa_score', params)`
3. `rass` via `get_tool_schema('rass')` → `calculate('rass', params)`
4. `cam_icu` via `get_tool_schema('cam_icu')` → `calculate('cam_icu', params)`

### Preoperative Assessment:
1. `asa_physical_status` via `get_tool_schema('asa_physical_status')` → `calculate('asa_physical_status', params)`
2. `rcri` via `get_tool_schema('rcri')` → `calculate('rcri', params)`
3. `mallampati_score` via `get_tool_schema('mallampati_score')` → `calculate('mallampati_score', params)`

### Pediatric/Transfusion:
1. `pediatric_dosing` via `get_tool_schema('pediatric_dosing')` → `calculate('pediatric_dosing', params)`
2. `mabl` via `get_tool_schema('mabl')` → `calculate('mabl', params)`
3. `transfusion_calc` via `get_tool_schema('transfusion_calc')` → `calculate('transfusion_calc', params)`

## 📊 AVAILABLE SPECIALTIES

| Specialty | Example Tools |
|-----------|---------------|
| Critical Care | SOFA, APACHE II, qSOFA, NEWS2, GCS, RASS, CAM-ICU |
| Anesthesiology | ASA, RCRI, Mallampati, MABL |
| Emergency Medicine | qSOFA, NEWS2, GCS |
| Nephrology | CKD-EPI 2021 |
| Pediatrics | Pediatric Dosing, Transfusion |

## ⚠️ IMPORTANT NOTES

1. Each response may include `next_step`, `guidance`, `suggestions`, and `resolved_value` to guide your next action
2. All calculators cite peer-reviewed references
3. Use `get_tool_schema(tool_id)` to see exact input parameters
4. Input validation errors return clear messages about valid ranges

所有計算器均引用同儕審查論文。每個回應都包含下一步指引。
"""


# Default configuration instance
default_config = McpServerConfig()
