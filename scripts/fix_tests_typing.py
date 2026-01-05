import os
import re

test_files = [
    "tests/test_acid_base.py",
    "tests/test_additional_scores.py",
    "tests/test_anesthesiology.py",
    "tests/test_api.py",
    "tests/test_cardiology.py",
    "tests/test_coverage_enhancement.py",
    "tests/test_critical_care.py",
    "tests/test_e2e.py",
    "tests/test_emergency.py",
    "tests/test_general.py",
    "tests/test_hepatology.py",
    "tests/test_infectious_disease.py",
    "tests/test_main.py",
    "tests/test_mcp_calculator_handlers.py",
    "tests/test_mcp_discovery.py",
    "tests/test_mcp_resources.py",
    "tests/test_nephrology.py",
    "tests/test_neurology.py",
    "tests/test_neurology_extended.py",
    "tests/test_obstetrics.py",
    "tests/test_parameter_validation.py",
    "tests/test_pediatric.py",
    "tests/test_pediatric_scores.py",
    "tests/test_phase10_calculators.py",
    "tests/test_phase11_calculators.py",
    "tests/test_phase18_calculators.py",
    "tests/test_phase9b_calculators.py",
    "tests/test_pulmonology.py",
    "tests/test_registry.py",
    "tests/test_security.py",
    "tests/test_surgery.py",
    "tests/test_use_cases.py",
    "tests/conftest.py"
]

def fix_file(filepath):
    if not os.path.exists(filepath):
        return
    
    with open(filepath, 'r') as f:
        lines = f.readlines()

    changed = False
    new_lines = []
    
    # Ensure Any is imported
    has_any = any("from typing import Any" in line or "import typing" in line for line in lines)
    if not has_any:
        new_lines.append("from typing import Any\n")
        changed = True

    i = 0
    while i < len(lines):
        line = lines[i]
        
        match = re.match(r'(\s*)def ([a-zA-Z0-9_]+)\(([^)]*)\)([^:]*):', line)
        if match:
            indent = match.group(1)
            name = match.group(2)
            args_str = match.group(3)
            suffix = match.group(4)
            
            args = []
            needs_fix = False
            
            # Special case for __init__
            if name == "__init__":
                if "->" in suffix and "None" not in suffix:
                    # Fix incorrect return type for __init__
                    new_suffix = suffix.replace("Any", "None")
                    needs_fix = True
                elif "->" not in suffix:
                    new_suffix = " -> None"
                    needs_fix = True
                else:
                    new_suffix = suffix
            else:
                if "->" not in suffix:
                    ret_type = "None" if name.startswith("test_") else "Any"
                    new_suffix = f" -> {ret_type}"
                    needs_fix = True
                else:
                    new_suffix = suffix
            
            for arg in args_str.split(','):
                arg = arg.strip()
                if not arg:
                    continue
                if arg == 'self':
                    args.append('self')
                elif ':' not in arg:
                    args.append(f"{arg}: Any")
                    needs_fix = True
                else:
                    args.append(arg)
            
            if needs_fix:
                new_line = f"{indent}def {name}({', '.join(args)}){new_suffix}:\n"
                new_lines.append(new_line)
                changed = True
                i += 1
                continue
        
        new_lines.append(line)
        i += 1

    if changed:
        with open(filepath, 'w') as f:
            f.writelines(new_lines)
        print(f"Fixed {filepath}")

if __name__ == "__main__":
    for f in test_files:
        fix_file(f)
