# Contributing

We welcome contributions to Medical-Calc-MCP!

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/medical-calc-mcp.git
   cd medical-calc-mcp
   ```
3. Install dependencies:
   ```bash
   uv sync --all-extras
   uv run pre-commit install
   ```

## Development Workflow

### Running Tests

```bash
# All tests
uv run pytest tests/

# With coverage
uv run pytest tests/ --cov=src --cov-report=html

# Specific test file
uv run pytest tests/test_calculators.py -v
```

### Code Quality

```bash
# Linting
uv run ruff check src/

# Formatting
uv run ruff format src/

# Type checking
uv run mypy src/
```

## Adding a New Calculator

### 1. Create the Calculator File

Create `src/domain/services/calculators/your_calculator.py`:

```python
from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ..base import BaseCalculator

class YourCalculator(BaseCalculator):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="your_calculator",
                name="Your Calculator Name",
                purpose="Brief description",
                input_params=["param1", "param2"],
            ),
            high_level=HighLevelKey(
                specialties=(Specialty.YOUR_SPECIALTY,),
                conditions=("Condition1", "Condition2"),
                clinical_contexts=(ClinicalContext.DIAGNOSIS,),
            ),
            references=(
                Reference(
                    citation="Author et al. Journal. Year;Vol:Pages",
                    pmid="12345678",
                ),
            ),
        )

    def calculate(self, **params) -> ScoreResult:
        # Your calculation logic
        pass
```

### 2. Register the Calculator

Add to `src/domain/services/calculators/__init__.py`:

```python
from .your_calculator import YourCalculator

__all__ = [
    # ... existing calculators
    "YourCalculator",
]

CALCULATORS = [
    # ... existing calculators
    YourCalculator,
]
```

### 3. Add Tests

Create `tests/e2e/test_your_calculator.py`.

### 4. Update Test Count

Update the expected count in:
- `tests/test_auto_discovery.py`
- `tests/test_infectious_disease.py`

## Pull Request Guidelines

1. **One calculator per PR** (or related group)
2. **Include tests** with clinical scenarios
3. **Add references** with PMID when possible
4. **Update documentation** if needed
5. **Pass all checks**: tests, lint, type check

## Code Style

- Follow existing patterns in the codebase
- Use type hints everywhere
- Include docstrings with parameter descriptions
- Keep functions focused and testable

## Questions?

Open an issue for discussion before starting large changes.
