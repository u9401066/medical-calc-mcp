"""
MCP Server Configuration

Configuration for the Medical Calculator MCP Server.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class McpServerConfig:
    """Configuration for MCP server"""
    
    name: str = "Medical Calculator MCP"
    version: str = "1.0.0"
    json_response: bool = True
    
    # Instructions shown to AI agents
    instructions: str = """
Medical Calculator MCP Server - 醫學計算工具 MCP 伺服器

This server provides validated medical calculators with intelligent tool discovery.

## Discovery Tools (探索工具)

Use these tools to find the right calculator:

| Tool | Purpose | 用途 |
|------|---------|------|
| `discover_tools(query)` | Free text search | 自由文字搜尋 |
| `list_by_specialty(specialty)` | Filter by specialty | 依專科篩選 |
| `list_by_context(context)` | Filter by clinical context | 依情境篩選 |
| `list_calculators()` | List all tools | 列出所有工具 |
| `get_calculator_info(tool_id)` | Get tool details | 取得工具詳情 |
| `list_specialties()` | Available specialties | 可用專科清單 |
| `list_contexts()` | Available contexts | 可用情境清單 |

## Usage Flow (使用流程)

1. **Discover**: Use discovery tools to find appropriate calculators
2. **Info**: Get input parameters with `get_calculator_info(tool_id)`
3. **Calculate**: Call the specific calculator (e.g., `calculate_sofa(...)`)

## Specialties Available (可用專科)

- Critical Care / ICU (重症加護)
- Anesthesiology (麻醉科)
- Emergency Medicine (急診)
- Nephrology (腎臟科)
- Cardiology (心臟科)
- And more...

All calculators cite peer-reviewed references.
所有計算器均引用同儕審查論文。
"""


# Default configuration instance
default_config = McpServerConfig()
