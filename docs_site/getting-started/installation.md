# Installation

## Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.11+ |
| OS | Windows, macOS, Linux |

## Installation Methods

### Method 1: uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/u9401066/medical-calc-mcp.git
cd medical-calc-mcp
uv sync
```

### Method 2: pip

```bash
git clone https://github.com/u9401066/medical-calc-mcp.git
cd medical-calc-mcp
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Method 3: Docker

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/u9401066/medical-calc-mcp:latest

# Or build locally
docker build -t medical-calc-mcp .
```

## Verify Installation

```bash
# Run tests
uv run pytest tests/ -q

# Check version
uv run python -c "from src import __version__; print(__version__)"
```

Expected output: `1.5.0`

## Development Installation

For contributing or development:

```bash
uv sync --all-extras
uv run pre-commit install
```
