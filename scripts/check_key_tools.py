#!/usr/bin/env python
"""Check if key tools from guidelines exist."""

from src.infrastructure.mcp.server import MedicalCalculatorServer


def main():
    s = MedicalCalculatorServer()
    r = s._registry

    # 檢查關鍵工具
    check_tools = [
        # GI Bleeding
        ("glasgow_blatchford", "GI - Glasgow-Blatchford"),
        ("aims65", "GI - AIMS65"),
        ("rockall_score", "GI - Rockall"),
        # Pediatrics
        ("pews", "Peds - PEWS"),
        ("pediatric_sofa", "Peds - pSOFA/Phoenix"),
        ("pim3", "Peds - PIM-3"),
        # Trauma/Burns
        ("iss", "Trauma - ISS"),
        ("parkland_formula", "Burns - Parkland"),
        ("tbsa", "Burns - TBSA"),
        # Pulmonology
        ("spesi", "Pulm - sPESI"),
        # Neurology
        ("fisher_grade", "Neuro - Fisher Grade"),
        ("hunt_hess", "Neuro - Hunt & Hess"),
        # Check non-existent
        ("phoenix_sepsis", "Peds - Phoenix (separate?)"),
        ("rts", "Trauma - RTS"),
        ("triss", "Trauma - TRISS"),
        ("maddrey_df", "Hepat - Maddrey DF"),
        ("lille_model", "Hepat - Lille"),
        ("euroscore_ii", "Cardiac - EuroSCORE II"),
    ]

    print("=" * 60)
    print("Key Tool Existence Check")
    print("=" * 60)

    found = 0
    missing = []

    for tool_id, desc in check_tools:
        exists = r.get_calculator(tool_id) is not None
        status = "YES" if exists else "NO"
        print(f"  [{status:3}] {tool_id:25} - {desc}")
        if exists:
            found += 1
        else:
            missing.append((tool_id, desc))

    print("=" * 60)
    print(f"Found: {found}/{len(check_tools)}")
    print("=" * 60)

    if missing:
        print("\nMissing (need to implement):")
        for tool_id, desc in missing:
            print(f"  - {tool_id} ({desc})")

    return found


if __name__ == "__main__":
    main()
