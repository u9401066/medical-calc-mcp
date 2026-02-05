#!/usr/bin/env python
"""Count and list all implemented calculators."""

from src.infrastructure.mcp.server import MedicalCalculatorServer


def main():
    """Count and list all tools."""
    s = MedicalCalculatorServer()

    # Use registry to get tools
    registry = s._registry
    tool_count = registry.count()
    tools = registry.list_all()  # Returns list[ToolMetadata]

    print("=" * 60)
    print(f"Total calculators: {tool_count}")
    print("=" * 60)

    # Group by specialty
    by_specialty: dict[str, list[str]] = {}
    for meta in tools:
        specs = meta.high_level.specialties if meta.high_level.specialties else []
        if not specs:
            spec_name = "Other"
            if spec_name not in by_specialty:
                by_specialty[spec_name] = []
            by_specialty[spec_name].append(meta.low_level.tool_id)
        else:
            spec = specs[0]  # Take first specialty
            spec_name = spec.value if hasattr(spec, "value") else str(spec)
            if spec_name not in by_specialty:
                by_specialty[spec_name] = []
            by_specialty[spec_name].append(meta.low_level.tool_id)

    print("\nBy Specialty:")
    for spec in sorted(by_specialty.keys()):
        print(f"\n  {spec} ({len(by_specialty[spec])}):")
        for tool_id in sorted(by_specialty[spec]):
            print(f"    - {tool_id}")

    print(f"\n{'=' * 60}")
    print(f"TOTAL: {tool_count} calculators")
    print(f"{'=' * 60}")

    return tool_count


if __name__ == "__main__":
    main()
