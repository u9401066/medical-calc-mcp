import os
import re

def fix_remaining_optionals():
    test_dir = "tests"
    files = [f for f in os.listdir(test_dir) if f.endswith(".py")]
    
    for filename in files:
        filepath = os.path.join(test_dir, filename)
        with open(filepath, "r") as f:
            lines = f.readlines()
        
        new_lines = []
        for i, line in enumerate(lines):
            indent_match = re.match(r'^(\s*)', line)
            indent = indent_match.group(1) if indent_match else ""
            
            # 1. Handle 'in result.interpretation.summary'
            match = re.search(r'assert\s+.*?\s+in\s+([a-zA-Z0-9_]+\.interpretation\.[a-zA-Z0-9_]+)', line)
            if match:
                var = match.group(1)
                if i > 0 and f"assert {var} is not None" not in lines[i-1]:
                    new_lines.append(f"{indent}assert {var} is not None\n")
            
            # 2. Handle 'details["key"]' where details is result.calculation_details
            match = re.search(r'assert\s+details\[', line)
            if match:
                if i > 0 and "assert details is not None" not in lines[i-1]:
                    # Find where details was assigned
                    for j in range(i-1, max(0, i-10), -1):
                        if "details = " in lines[j]:
                            match_assign = re.search(r'details\s*=\s*([a-zA-Z0-9_]+\.calculation_details)', lines[j])
                            if match_assign:
                                var = match_assign.group(1)
                                # Insert assertion before assignment
                                new_lines[-1] = f"{indent}assert {var} is not None\n" + new_lines[-1]
                            break

            # 3. Handle 'result.interpretation.summary.lower()'
            match = re.search(r'([a-zA-Z0-9_]+\.interpretation\.[a-zA-Z0-9_]+)\.lower\(\)', line)
            if match:
                var = match.group(1)
                if i > 0 and f"assert {var} is not None" not in lines[i-1]:
                    new_lines.append(f"{indent}assert {var} is not None\n")

            new_lines.append(line)
            
        new_content = "".join(new_lines)
        with open(filepath, "w") as f:
            f.write(new_content)

if __name__ == "__main__":
    fix_remaining_optionals()
