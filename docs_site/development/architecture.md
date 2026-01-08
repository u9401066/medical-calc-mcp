# Architecture

Medical-Calc-MCP follows **Domain-Driven Design (DDD)** with an **Onion Architecture**.

## Design Principles

1. **Domain at the Center**: Business logic is isolated from infrastructure
2. **Dependency Inversion**: Inner layers don't depend on outer layers
3. **Single Responsibility**: Each calculator is a focused domain service

## Layer Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │   MCP Server  │  │   REST API    │  │    Docker     │       │
│  │   (FastMCP)   │  │  (Starlette)  │  │               │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
├─────────────────────────────────────────────────────────────────┤
│                       APPLICATION                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Use Cases                               │  │
│  │  • CalculateUseCase (calculate with validation)           │  │
│  │  • DiscoveryUseCase (find tools by context)               │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                         DOMAIN                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │    Entities     │  │    Services     │  │  Value Objects  │  │
│  │  • ScoreResult  │  │  • Calculators  │  │  • Unit         │  │
│  │  • ToolMetadata │  │  • ParamMatcher │  │  • Severity     │  │
│  │                 │  │  • Boundary     │  │  • Reference    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
src/
├── domain/                    # Core business logic
│   ├── entities/              # Domain entities
│   │   ├── score_result.py    # Calculation result
│   │   └── tool_metadata.py   # Calculator metadata
│   ├── services/              # Domain services
│   │   ├── calculators/       # 121 calculator implementations
│   │   ├── base.py            # BaseCalculator abstract class
│   │   └── param_matcher.py   # Intelligent parameter matching
│   ├── value_objects/         # Immutable value types
│   │   ├── tool_keys.py       # Specialty, ClinicalContext enums
│   │   ├── units.py           # Medical units
│   │   └── interpretation.py  # Result interpretation
│   └── validation/            # Domain validation
│       └── boundaries.py      # Clinical boundary validation
│
├── application/               # Application services
│   └── use_cases/
│       ├── calculate_use_case.py
│       └── discovery_use_case.py
│
├── infrastructure/            # External interfaces
│   ├── mcp/                   # MCP protocol
│   │   ├── server.py          # FastMCP server
│   │   └── handlers/          # Tool handlers
│   └── rest/                  # REST API
│       └── server.py          # Starlette server
│
└── main.py                    # Entry point
```

## Calculator Pattern

Each calculator follows the `BaseCalculator` pattern:

```python
class SofaCalculator(BaseCalculator):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="sofa_score",
                name="SOFA Score",
                purpose="...",
                input_params=[...],
            ),
            high_level=HighLevelKey(
                specialties=(Specialty.CRITICAL_CARE,),
                conditions=("Sepsis", "Organ Dysfunction"),
                clinical_contexts=(ClinicalContext.SEVERITY_ASSESSMENT,),
            ),
            references=(Reference(citation="...", pmid="..."),),
        )

    def calculate(self, **params) -> ScoreResult:
        # Validated calculation logic
        return ScoreResult(
            value=score,
            unit=Unit.SCORE,
            interpretation=Interpretation(...),
        )
```

## Two-Level Key System

### Low-Level Key (Direct Access)
- `tool_id`: Unique identifier
- `name`: Display name
- `input_params`: Required parameters

### High-Level Key (Discovery)
- `specialties`: Medical specialties
- `conditions`: Clinical conditions
- `clinical_contexts`: Use contexts
- `keywords`: Search terms

This enables both:
1. Direct tool invocation: `calculate("sofa_score", ...)`
2. Discovery: "Find tools for sepsis evaluation"
