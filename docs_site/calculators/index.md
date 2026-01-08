# Calculator Overview

Medical-Calc-MCP provides **121 validated medical calculators** across 16+ specialties.

## Calculator Categories

### By Specialty

| Specialty | Count | Link |
|-----------|-------|------|
| Critical Care / ICU | 15+ | [View →](critical-care.md) |
| Cardiology | 12+ | [View →](cardiology.md) |
| Nephrology | 8+ | [View →](nephrology.md) |
| Anesthesiology | 10+ | [View →](anesthesiology.md) |
| Pulmonology | 8+ | Coming soon |
| Neurology | 6+ | [View →](neurology.md) |
| Hepatology | 5+ | [View →](hepatology.md) |
| Hematology | 5+ | Coming soon |
| Emergency Medicine | 8+ | Coming soon |
| Psychiatry | 7 | [View →](psychiatry.md) |
| Dermatology | 5 | Coming soon |
| Endocrinology | 5 | Coming soon |
| Urology | 4 | Coming soon |
| OB/GYN | 5 | Coming soon |
| Geriatrics | 6 | [View →](geriatrics.md) |
| Oncology | 3 | Coming soon |

## Calculator Structure

Each calculator provides:

- **Score/Value**: The calculated result
- **Interpretation**: Clinical meaning and severity
- **Recommendations**: Evidence-based next steps
- **References**: Original papers with PMID

## Example Output

```json
{
  "value": 45.2,
  "unit": "mL/min/1.73m²",
  "interpretation": {
    "summary": "CKD Stage 3b",
    "severity": "moderate",
    "recommendations": [
      "Monitor kidney function every 3-6 months",
      "Refer to nephrology"
    ]
  },
  "references": [
    {
      "citation": "Levey AS, et al. N Engl J Med. 2009;361:2279-90",
      "pmid": "19920272"
    }
  ]
}
```

## Using Calculators

### Via MCP (AI Agents)

```
User: Calculate SOFA score for a patient with:
- PaO2/FiO2 = 200, mechanically ventilated
- Platelets = 80
- Bilirubin = 2.5
- MAP = 65 on norepinephrine
- GCS = 13
- Creatinine = 2.0

AI: [Calls calculate("sofa_score", {...})]
→ SOFA Score = 10, indicating severe organ dysfunction
```

### Via REST API

```bash
curl -X POST http://localhost:8000/api/v1/calculate/sofa_score \
  -H "Content-Type: application/json" \
  -d '{
    "pao2_fio2_ratio": 200,
    "is_mechanically_ventilated": true,
    "platelets": 80,
    "bilirubin": 2.5,
    "map_value": 65,
    "vasopressor": "norepinephrine",
    "gcs_score": 13,
    "creatinine": 2.0
  }'
```
