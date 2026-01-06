import os
import re


def cleanup_bad_assertions():
    test_dir = "tests"
    files = [f for f in os.listdir(test_dir) if f.endswith(".py")]


    for filename in files:
        filepath = os.path.join(test_dir, filename)
        with open(filepath) as f:
            content = f.read()

        new_content = content

        # Fix specific bad assertions
        new_content = re.sub(r"assert severity\.value is not None\n\s+", "", new_content)
        new_content = re.sub(r"assert risk_level\.value is not None\n\s+", "", new_content)
        new_content = re.sub(r"assert unit\.value is not None\n\s+", "", new_content)
        new_content = re.sub(r"assert calculation_details\.value is not None\n\s+", "", new_content)

        # Fix cases where I added 'assert severity is not None' but it should be 'result.interpretation.severity'
        new_content = re.sub(r"assert severity is not None", "assert result.interpretation.severity is not None", new_content)
        new_content = re.sub(r"assert risk_level is not None", "assert result.interpretation.risk_level is not None", new_content)
        new_content = re.sub(r"assert unit is not None", "assert result.unit is not None", new_content)
        new_content = re.sub(r"assert calculation_details is not None", "assert result.interpretation.calculation_details is not None", new_content)

        if new_content != content:
            with open(filepath, "w") as f:
                f.write(new_content)
            print(f"Cleaned up {filename}")

if __name__ == "__main__":
    cleanup_bad_assertions()
