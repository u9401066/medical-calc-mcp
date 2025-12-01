# Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-01 | CORS 設定改為環境變數控制，生產環境需設定 CORS_ORIGINS | 預設 allow_origins=['*'] 過於寬鬆，生產環境需要限制來源以防止 CSRF 攻擊 |
