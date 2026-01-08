# 繁體中文文檔

## Medical Calculator MCP Server

🏥 **121 個經驗證的醫學計算器，專為 AI Agent 設計**

---

## 什麼是 Medical-Calc-MCP？

Medical-Calc-MCP 是一個 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 伺服器，提供 **121 個經過驗證的醫學計算器**，供 Claude、GPT 等 AI 代理使用。

!!! warning "臨床免責聲明"
    本工具僅供教育和研究用途。請務必以臨床判斷和機構規範驗證計算結果。

## ✨ 主要特色

- **121 個臨床計算器**：涵蓋 16+ 醫學專科
- **MCP 原生整合**：使用 FastMCP SDK 開發
- **智慧工具發現**：兩層式 Key 系統
- **邊界驗證**：文獻支持的臨床範圍檢查

## 🚀 快速開始

### Claude Desktop 設定

編輯 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "medical-calc": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/medical-calc-mcp", "python", "-m", "src.main"]
    }
  }
}
```

### VS Code Copilot 設定

編輯 `.vscode/mcp.json`：

```json
{
  "servers": {
    "medical-calc": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "${workspaceFolder}", "python", "-m", "src.main"]
    }
  }
}
```

## 📊 專科涵蓋

| 專科 | 計算器數量 | 範例 |
|------|-----------|------|
| 重症加護 | 15+ | SOFA, APACHE II, qSOFA |
| 心臟科 | 12+ | CHA₂DS₂-VASc, HEART |
| 腎臟科 | 8+ | CKD-EPI, KDIGO AKI |
| 麻醉科 | 10+ | ASA-PS, Mallampati |
| 精神科 | 7 | PHQ-9, GAD-7 |
| 老年醫學 | 6 | MMSE, MoCA, Barthel |

## 📖 更多資源

- [英文文檔](../index.md)
- [GitHub 專案](https://github.com/u9401066/medical-calc-mcp)
- [問題回報](https://github.com/u9401066/medical-calc-mcp/issues)

## 📜 授權

Apache 2.0 授權條款
