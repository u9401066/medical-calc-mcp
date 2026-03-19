# REST API Reference

> Generated from the FastAPI OpenAPI schema. Do not edit manually.
> Source: [openapi.json](openapi.json) | OpenAPI 3.1.0 | v1.5.0

This API currently publishes **12 operations** across **12 paths**, backed by **6 shared schemas**.

## Base URL

```
http://localhost:8000/api/v1
```

Health and docs remain available at the server root: `/health`, `/docs`, `/redoc`, and `/openapi.json`.

## API Metadata

- Title: Medical Calculator API
- Version: 1.5.0

### Description

## 醫學計算器 REST API

提供 151 個經過驗證的臨床評分工具，涵蓋 31 個主要專科；所有計算器均引用同儕審查研究論文。

### 功能特色
- 智慧工具探索 (依專科、臨床情境搜尋)
- 循證醫學 (所有公式引用原始論文)
- 參數驗證 (範圍檢查、必填檢查)

### 使用流程
1. `GET /api/v1/calculators` - 列出所有計算器
2. `GET /api/v1/calculators/{tool_id}` - 取得計算器詳情
3. `POST /api/v1/calculate/{tool_id}` - 執行計算

### 代表性專科覆蓋
- Critical Care: 18 tools (APACHE II Score, Anion Gap, CAM-ICU (Confusion Assessment Method for ICU), Clinical Pulmonary Infection Score (CPIS))
- Geriatrics: 13 tools (4AT (Rapid Assessment Test for Delirium), Barthel Index (ADL Assessment), CFS (Clinical Frailty Scale), FRAIL Scale)
- Cardiology: 11 tools (ACEF II Score, CHA₂DS₂-VA Score (2024 ESC), CHA₂DS₂-VASc Score, Corrected QT Interval (QTc))
- Emergency Medicine: 9 tools (Centor Score (Modified/McIsaac), Glasgow Coma Scale (GCS), HEART Score, NEWS2 (National Early Warning Score 2))

## Endpoints

### GET /

**Summary:** Root

API root with service information

**Tags:** Info

**Responses**

| Status | Schema | Description |
|--------|--------|-------------|
| 200 | object | Successful Response |

### POST /api/v1/calculate/{tool_id}

**Summary:** Calculate

執行計算

Execute a medical calculation with the given parameters.

Example for CKD-EPI 2021:
```json
{
    "params": {
        "serum_creatinine": 1.2,
        "age": 65,
        "sex": "female"
    }
}
```

**Tags:** Calculate

**Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| tool_id | path | yes | string | - |

**Request Body**

| Content-Type | Schema | Required |
|--------------|--------|----------|
| application/json | CalculatorInput | yes |

**Responses**

| Status | Schema | Description |
|--------|--------|-------------|
| 200 | CalculatorResponse | Successful Response |
| 422 | HTTPValidationError | Validation Error |

### GET /api/v1/calculators

**Summary:** List Calculators

列出所有可用的計算器

List all available calculators with their metadata.

**Tags:** Discovery

**Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| limit | query | no | integer | Maximum results |

**Responses**

| Status | Schema | Description |
|--------|--------|-------------|
| 200 | DiscoveryResponse | Successful Response |
| 422 | HTTPValidationError | Validation Error |

### GET /api/v1/calculators/{tool_id}

**Summary:** Get Calculator Info

取得特定計算器的詳細資訊

Get detailed information about a specific calculator including
parameters, references, and usage examples.

**Tags:** Discovery

**Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| tool_id | path | yes | string | - |

**Responses**

| Status | Schema | Description |
|--------|--------|-------------|
| 200 | object | Successful Response |
| 422 | HTTPValidationError | Validation Error |

### POST /api/v1/ckd-epi

**Summary:** Calculate Ckd Epi

快速計算 CKD-EPI 2021 eGFR

Calculate eGFR using CKD-EPI 2021 equation (race-free).

**Tags:** Quick Calculate

**Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| serum_creatinine | query | yes | number | Serum creatinine (mg/dL) |
| age | query | yes | integer | Age in years |
| sex | query | yes | string | Sex (male/female) |

**Responses**

| Status | Schema | Description |
|--------|--------|-------------|
| 200 | object | Successful Response |
| 422 | HTTPValidationError | Validation Error |

### GET /api/v1/contexts

**Summary:** List Contexts

列出所有臨床情境

List all available clinical contexts.

**Tags:** Discovery

**Responses**

| Status | Schema | Description |
|--------|--------|-------------|
| 200 | object | Successful Response |

### GET /api/v1/search

**Summary:** Search Calculators

依關鍵字搜尋計算器

Search calculators by keyword (name, specialty, condition, etc.)

**Tags:** Discovery

**Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| q | query | yes | string | Search keyword |
| limit | query | no | integer | Maximum results |

**Responses**

| Status | Schema | Description |
|--------|--------|-------------|
| 200 | DiscoveryResponse | Successful Response |
| 422 | HTTPValidationError | Validation Error |

### POST /api/v1/sofa

**Summary:** Calculate Sofa

快速計算 SOFA Score

Calculate Sequential Organ Failure Assessment score.

**Tags:** Quick Calculate

**Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| pao2_fio2_ratio | query | yes | number | PaO2/FiO2 ratio |
| platelets | query | yes | number | Platelets (×10³/µL) |
| bilirubin | query | yes | number | Bilirubin (mg/dL) |
| cardiovascular | query | yes | string | MAP or vasopressor status |
| gcs_score | query | yes | integer | GCS score |
| creatinine | query | yes | number | Creatinine (mg/dL) |

**Responses**

| Status | Schema | Description |
|--------|--------|-------------|
| 200 | object | Successful Response |
| 422 | HTTPValidationError | Validation Error |

### GET /api/v1/specialties

**Summary:** List Specialties

列出所有可用的專科分類

List all available medical specialties.

**Tags:** Discovery

**Responses**

| Status | Schema | Description |
|--------|--------|-------------|
| 200 | object | Successful Response |

### GET /api/v1/specialties/{specialty}

**Summary:** List By Specialty

列出特定專科的所有計算器

List all calculators for a specific medical specialty.

**Tags:** Discovery

**Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| specialty | path | yes | string | - |
| limit | query | no | integer | Maximum results |

**Responses**

| Status | Schema | Description |
|--------|--------|-------------|
| 200 | DiscoveryResponse | Successful Response |
| 422 | HTTPValidationError | Validation Error |

### GET /health

**Summary:** Health Check

Health check endpoint for Docker/K8s

**Tags:** Health

**Responses**

| Status | Schema | Description |
|--------|--------|-------------|
| 200 | HealthResponse | Successful Response |

### GET /ready

**Summary:** Readiness Check

Readiness endpoint for production traffic and deployment gates.

**Tags:** Health

**Responses**

| Status | Schema | Description |
|--------|--------|-------------|
| 200 | object | Successful Response |

## Shared Schemas

| Schema | Description |
|--------|-------------|
| CalculatorInput | Generic calculator input model |
| CalculatorResponse | Calculator response model |
| DiscoveryResponse | Discovery response model |
| HTTPValidationError | - |
| HealthResponse | Health check response |
| ValidationError | - |
