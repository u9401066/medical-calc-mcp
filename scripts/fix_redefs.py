import os
import re

def fix_coverage():
    filepath = "tests/test_coverage_enhancement.py"
    if not os.path.exists(filepath):
        return
    with open(filepath, "r") as f:
        lines = f.readlines()
    
    new_lines = []
    seen_calc = False
    for line in lines:
        if "def test_" in line:
            seen_calc = False
        
        if "calc: Any =" in line:
            if seen_calc:
                line = line.replace("calc: Any =", "calc =")
            else:
                seen_calc = True
        new_lines.append(line)
    
    with open(filepath, "w") as f:
        f.writelines(new_lines)

def fix_validation():
    filepath = "tests/test_parameter_validation.py"
    if not os.path.exists(filepath):
        return
    with open(filepath, "r") as f:
        content = f.read()
    
    # Clean up the mess I made with sed
    content = re.sub(r"asa_class: Any = val\n\s+asa_class: Any = asa_class", "asa_class: Any = val", content)
    content = re.sub(r"mal_class: Any = val\n\s+mal_class: Any = mal_class", "mal_class: Any = val", content)
    content = re.sub(r"score: Any = val\n\s+score: Any = score", "score: Any = val", content)
    content = re.sub(r"consciousness: Any = val\n\s+consciousness: Any = consciousness", "consciousness: Any = val", content)
    content = re.sub(r"admission_type: Any = val\n\s+admission_type: Any = admission_type", "admission_type: Any = val", content)
    content = re.sub(r"sex: Any = val\n\s+sex: Any = sex", "sex: Any = val", content)
    
    with open(filepath, "w") as f:
        f.write(content)

if __name__ == "__main__":
    fix_coverage()
    fix_validation()
