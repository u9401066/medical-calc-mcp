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
    "tests/test_use_cases.py"
]

def fix_file(filepath):
    if not os.path.exists(filepath):
        return

    with open(filepath) as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []

    for i, line in enumerate(lines):
        indent_match = re.match(r'^(\s*)', line)
        indent = indent_match.group(1) if indent_match else ""

        # Case: result.value comparison
        match = re.search(r'assert\s+([a-zA-Z0-9_]+\.value)\s*[=<>!]+', line)
        if match:
            var = match.group(1)
            if i > 0 and f"assert {var} is not None" not in lines[i-1]:
                new_lines.append(f"{indent}assert {var} is not None")

        # Case: result.interpretation.summary/details/etc 'in' check
        match = re.search(r'assert\s+.*?\s+in\s+([a-zA-Z0-9_]+\.interpretation\.[a-zA-Z0-9_]+)', line)
        if match:
            var = match.group(1)
            if i > 0 and f"assert {var} is not None" not in lines[i-1]:
                new_lines.append(f"{indent}assert {var} is not None")

        # Case: result.calculation_details indexing
        match = re.search(r'([a-zA-Z0-9_]+\.calculation_details)\[', line)
        if match:
            var = match.group(1)
            if i > 0 and f"assert {var} is not None" not in lines[i-1]:
                new_lines.append(f"{indent}assert {var} is not None")

        # Case: result.interpretation.severity/risk_level access
        match = re.search(r'([a-zA-Z0-9_]+\.interpretation\.(severity|risk_level))', line)
        if match:
            var = match.group(1)
            if i > 0 and f"assert {var} is not None" not in lines[i-1]:
                new_lines.append(f"{indent}assert {var} is not None")

        # Case: result.unit access
        match = re.search(r'([a-zA-Z0-9_]+\.unit)', line)
        if match and "is not None" not in line and "assert" in line:
            var = match.group(1)
            if i > 0 and f"assert {var} is not None" not in lines[i-1]:
                new_lines.append(f"{indent}assert {var} is not None")

        new_lines.append(line)

    new_content = '\n'.join(new_lines)
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")

if __name__ == "__main__":
    for f in test_files:
        fix_file(f)
