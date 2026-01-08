# MCP Tools Reference

Medical-Calc-MCP exposes tools via the Model Context Protocol (MCP).

## Discovery Tools

### list_specialties

List all available medical specialties.

```json
{
  "tool": "list_specialties"
}
```

**Returns**: Array of specialty names with calculator counts.

---

### list_contexts

List all clinical contexts.

```json
{
  "tool": "list_contexts"
}
```

---

### list_by_specialty

Get calculators for a specific specialty.

```json
{
  "tool": "list_by_specialty",
  "params": {
    "specialty": "critical_care"
  }
}
```

---

### list_by_context

Get calculators for a clinical context.

```json
{
  "tool": "list_by_context",
  "params": {
    "context": "sepsis_evaluation"
  }
}
```

---

### search_calculators

Search calculators by keyword.

```json
{
  "tool": "search_calculators",
  "params": {
    "keyword": "cardiac risk"
  }
}
```

---

### get_calculator_info

Get detailed info about a calculator.

```json
{
  "tool": "get_calculator_info",
  "params": {
    "tool_id": "sofa_score"
  }
}
```

**Returns**:
- Name, purpose
- Required parameters with descriptions
- References with PMID

---

### get_related_tools

Find calculators related to a given tool.

```json
{
  "tool": "get_related_tools",
  "params": {
    "tool_id": "chads2_vasc"
  }
}
```

---

## Calculation Tool

### calculate

Execute a calculation.

```json
{
  "tool": "calculate",
  "params": {
    "tool_id": "ckd_epi_2021",
    "serum_creatinine": 1.2,
    "age": 65,
    "sex": "male"
  }
}
```

**Returns**:
```json
{
  "success": true,
  "score_name": "CKD-EPI 2021 eGFR",
  "result": 62.5,
  "unit": "mL/min/1.73m²",
  "interpretation": {
    "summary": "CKD Stage 2",
    "severity": "mild",
    "recommendations": [...]
  },
  "references": [...]
}
```

---

## Batch Calculation

### calculate_batch

Execute multiple calculations at once.

```json
{
  "tool": "calculate_batch",
  "params": {
    "calculations": [
      {"tool_id": "qsofa_score", "params": {...}},
      {"tool_id": "sofa_score", "params": {...}}
    ]
  }
}
```

---

## Parameter Matching

The `calculate` tool supports intelligent parameter matching:

| Feature | Example |
|---------|---------|
| Aliases | `cr` → `serum_creatinine` |
| Fuzzy match | `creatnine` → `creatinine` |
| Unit suffix | `creatinine_mg_dl` → `creatinine` |

---

## Boundary Validation

All calculations include clinical boundary validation:

```json
{
  "result": 45.2,
  "_boundary_warnings": [
    {
      "parameter": "creatinine",
      "value": 8.5,
      "message": "Value above typical clinical range (0.5-4.0 mg/dL)",
      "reference": "PMID: 19414839"
    }
  ]
}
```
