# Progress (Updated: 2025-12-01)

## Done

- 完成安全審查 (Security Audit 2025-06)
- 修復 CORS 設定 - 改為環境變數控制
- 升級 pip 25.3 和 setuptools 80.9.0 修復 CVE
- 修復 API Quick Calculate endpoints (model_dump -> dict)
- 更新 README 新增 Security 章節
- 新增 API 測試 (tests/test_api.py) - 25 個測試
- 建立 DEPLOYMENT.md 部署指南

## Doing

- Git commit 並 push 安全更新

## Next

- 考慮新增 rate limiting middleware
- 考慮新增 API key 認證選項
