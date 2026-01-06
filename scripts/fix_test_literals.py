import os
import re


def fix_test_literals():
    filepath = "tests/test_parameter_validation.py"
    if not os.path.exists(filepath):
        return

    with open(filepath) as f:
        content = f.read()

    new_content = content

    # Fix Literal issues by casting to Any or using Any type hint
    # 1. for asa_class in [1, 2, 3, 4, 5, 6]:
    new_content = re.sub(r"for asa_class in \[1, 2, 3, 4, 5, 6\]:", "for asa_class in [1, 2, 3, 4, 5, 6]:\n            asa_class: Any = asa_class", new_content)

    # 2. for mal_class in [1, 2, 3, 4]:
    new_content = re.sub(r"for mal_class in \[1, 2, 3, 4\]:", "for mal_class in [1, 2, 3, 4]:\n            mal_class: Any = mal_class", new_content)

    # 3. for score in [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4]:
    new_content = re.sub(r"for score in \[-5, -4, -3, -2, -1, 0, 1, 2, 3, 4\]:", "for score in [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4]:\n            score: Any = score", new_content)

    # 4. for consciousness in ["A", "V", "P", "U", "C"]:
    new_content = re.sub(r"for consciousness in \[\"A\", \"V\", \"P\", \"U\", \"C\"\]:", "for consciousness in [\"A\", \"V\", \"P\", \"U\", \"C\"]:\n            consciousness: Any = consciousness", new_content)

    # 5. for admission_type in ["nonoperative", "elective_postop", "emergency_postop"]:
    new_content = re.sub(r"for admission_type in \[\"nonoperative\", \"elective_postop\", \"emergency_postop\"\]:", "for admission_type in [\"nonoperative\", \"elective_postop\", \"emergency_postop\"]:\n            admission_type: Any = admission_type", new_content)

    # 6. for sex in ["male", "female"]:
    new_content = re.sub(r"for sex in \[\"male\", \"female\"\]:", "for sex in [\"male\", \"female\"]:\n            sex: Any = sex", new_content)

    # Fix ApacheIiCalculator **dict issues
    # result = calc.calculate(**params)
    # mypy complains about **dict[str, float] not matching specific types
    new_content = re.sub(r"result = calc\.calculate\(\*\*params\)", "result = calc.calculate(**cast(dict[str, Any], params))", new_content)

    # Add cast import if needed
    if "from typing import Any, cast" not in new_content and "from typing import Any" in new_content:
        new_content = new_content.replace("from typing import Any", "from typing import Any, cast")
    elif "from typing import cast" not in new_content:
        new_content = "from typing import Any, cast\n" + new_content

    if new_content != content:
        with open(filepath, "w") as f:
            f.write(new_content)
        print(f"Fixed literals in {filepath}")

def fix_coverage_enhancement():
    filepath = "tests/test_coverage_enhancement.py"
    if not os.path.exists(filepath):
        return

    with open(filepath) as f:
        content = f.read()

    # Change 'calc = ' to 'calc: Any = ' to avoid type inference issues
    new_content = re.sub(r"calc = ", "calc: Any = ", content)

    if new_content != content:
        with open(filepath, "w") as f:
            f.write(new_content)
        print(f"Fixed coverage enhancement in {filepath}")

if __name__ == "__main__":
    fix_test_literals()
    fix_coverage_enhancement()
