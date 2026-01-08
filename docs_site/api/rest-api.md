# REST API Reference

Medical-Calc-MCP also provides a REST API for non-MCP integrations.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

When `SECURITY_API_KEY` is configured:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/...
```

---

## Endpoints

### Health Check

```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "1.5.0",
  "calculators": 121
}
```

---

### List All Calculators

```http
GET /api/v1/calculators
```

**Response**:
```json
{
  "calculators": [
    {
      "tool_id": "sofa_score",
      "name": "SOFA Score",
      "specialty": "critical_care"
    },
    ...
  ],
  "total": 121
}
```

---

### Get Calculator Details

```http
GET /api/v1/calculators/{tool_id}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/calculators/ckd_epi_2021
```

**Response**:
```json
{
  "tool_id": "ckd_epi_2021",
  "name": "CKD-EPI 2021 eGFR",
  "purpose": "Estimate glomerular filtration rate",
  "parameters": [
    {
      "name": "serum_creatinine",
      "type": "number",
      "required": true,
      "description": "Serum creatinine in mg/dL"
    },
    ...
  ],
  "references": [...]
}
```

---

### Calculate

```http
POST /api/v1/calculate/{tool_id}
```

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/calculate/ckd_epi_2021 \
  -H "Content-Type: application/json" \
  -d '{
    "serum_creatinine": 1.2,
    "age": 65,
    "sex": "male"
  }'
```

**Response**:
```json
{
  "success": true,
  "score_name": "CKD-EPI 2021 eGFR",
  "result": 62.5,
  "unit": "mL/min/1.73m²",
  "interpretation": {
    "summary": "CKD Stage 2 (Mildly decreased)",
    "severity": "mild",
    "stage": "G2",
    "recommendations": [
      "Monitor kidney function annually",
      "Optimize cardiovascular risk factors"
    ]
  },
  "references": [
    {
      "citation": "Inker LA, et al. N Engl J Med. 2021;385(19):1737-1749",
      "pmid": "34554658"
    }
  ]
}
```

---

### Batch Calculate

```http
POST /api/v1/calculate/batch
```

**Request**:
```json
{
  "calculations": [
    {
      "tool_id": "qsofa_score",
      "params": {
        "respiratory_rate": 24,
        "systolic_bp": 95,
        "altered_mentation": true
      }
    },
    {
      "tool_id": "sofa_score",
      "params": {...}
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "error": "validation_error",
  "message": "Missing required parameter: serum_creatinine",
  "details": {
    "missing_params": ["serum_creatinine"]
  }
}
```

### 404 Not Found

```json
{
  "error": "not_found",
  "message": "Calculator 'invalid_tool' not found"
}
```

### 429 Too Many Requests

```json
{
  "error": "rate_limited",
  "message": "Rate limit exceeded. Try again in 60 seconds."
}
```

---

## OpenAPI Documentation

When running the server, access interactive API docs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
