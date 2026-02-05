# Progress (Updated: 2026-02-05)

## Done

- uv 套件管理遷移完成
- mypy --strict 100% 類型覆蓋
- ruff 程式碼清理
- 測試套件通過 (1752+ passed)
- 文件更新 (README, CHANGELOG, ROADMAP, CONTRIBUTING)
- Dockerfile 更新為 uv 多階段建構
- Git 推送 (commit 47c1f3e)
- MCP stdio logging 修正 (重導向至 stderr)
- .vscode/mcp.json 配置修正
- CI 流程遷移至 uv 並通過驗證 (Python 3.11, 3.12, 3.13)
- 計算器數量達到 121 個 (涵蓋 24 個專科)
- SSL/TLS 憑證路徑配置功能
  - 新增 SslConfig dataclass (config.py)
  - 支援 CLI 參數: --ssl-keyfile, --ssl-certfile, --ssl-ca-certs
  - 支援環境變數: SSL_ENABLED, SSL_KEYFILE, SSL_CERTFILE, SSL_CA_CERTS, SSL_DIR
  - 更新部署文件 (DEPLOYMENT.md, README.md, README.zh-TW.md)
- mypy --strict src 全部通過 (195 files)
- ruff check 全部通過
- SSL 測試套件 (29 tests in test_ssl_config.py)
  - SslConfig dataclass 單元測試
  - from_env() 環境變數測試
  - validate() 驗證測試
  - 整合測試 (create_server, main CLI)
- 文獻引用統計 script (scripts/count_references.py)
  - 229 unique PMIDs
  - 190 unique DOIs
  - 100% calculators have citations
  - Average 2.14 refs per calculator

## Doing

- 監控 Copilot MCP 整合狀態

## Next

- 驗證 VS Code MCP 伺服器運作正常
- 新增更多醫學計算器
- 效能優化
