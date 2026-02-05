#!/usr/bin/env python
"""
Count and analyze references across all calculators.

Usage:
    uv run python scripts/count_references.py

    # Or with PYTHONPATH
    $env:PYTHONPATH = "."; python scripts/count_references.py
"""

from collections import defaultdict

from src.infrastructure.mcp.server import MedicalCalculatorServer


def main() -> None:
    """Count and analyze all references."""
    s = MedicalCalculatorServer()
    registry = s._registry
    tools = registry.list_all()

    # Collect statistics
    total_refs = 0
    refs_by_tool: dict[str, int] = {}
    unique_pmids: set[str] = set()
    unique_dois: set[str] = set()
    refs_by_specialty: dict[str, int] = defaultdict(int)
    tools_without_refs: list[str] = []
    refs_by_year: dict[int, int] = defaultdict(int)

    for meta in tools:
        refs = meta.references
        tool_id = meta.low_level.tool_id
        refs_by_tool[tool_id] = len(refs)
        total_refs += len(refs)

        if len(refs) == 0:
            tools_without_refs.append(tool_id)

        # Get specialty
        specs = meta.high_level.specialties if meta.high_level.specialties else []
        spec_name = specs[0].value if specs else "Other"

        for ref in refs:
            refs_by_specialty[spec_name] += 1
            if ref.pmid:
                unique_pmids.add(ref.pmid)
            if ref.doi:
                unique_dois.add(ref.doi)
            if ref.year:
                refs_by_year[ref.year] += 1

    # Print report
    print("=" * 70)
    print("Medical Calculator MCP - Reference Statistics")
    print("=" * 70)
    print()
    print("📊 Overall Statistics:")
    print(f"   Total calculators:          {len(tools)}")
    print(f"   Total reference entries:    {total_refs}")
    print(f"   Unique PMIDs:               {len(unique_pmids)}")
    print(f"   Unique DOIs:                {len(unique_dois)}")
    print(f"   Average refs per calc:      {total_refs/len(tools):.2f}")
    print(f"   Calculators without refs:   {len(tools_without_refs)}")
    print()

    # References by specialty
    print("📚 References by Specialty:")
    for spec in sorted(refs_by_specialty.keys(), key=lambda x: refs_by_specialty[x], reverse=True):
        print(f"   {spec:30} {refs_by_specialty[spec]:4} refs")
    print()

    # Top referenced calculators
    print("🏆 Calculators with Most References:")
    sorted_tools = sorted(refs_by_tool.items(), key=lambda x: x[1], reverse=True)[:10]
    for tool_id, count in sorted_tools:
        print(f"   {tool_id:35} {count} refs")
    print()

    # References by year (publication year distribution)
    if refs_by_year:
        print("📅 References by Publication Year:")
        for year in sorted(refs_by_year.keys(), reverse=True)[:10]:
            print(f"   {year}: {refs_by_year[year]} refs")
        print()

    # Tools without references
    if tools_without_refs:
        print("⚠️  Calculators without references:")
        for tool_id in sorted(tools_without_refs):
            print(f"   - {tool_id}")
        print()

    # Summary badge format
    print("=" * 70)
    print("📌 Summary for README badges:")
    print(f"   References: {len(unique_pmids)} PMIDs, {len(unique_dois)} DOIs")
    print(f"   Coverage: {(len(tools) - len(tools_without_refs)) / len(tools) * 100:.0f}% calculators have citations")
    print("=" * 70)

    return


if __name__ == "__main__":
    main()
