#!/usr/bin/env python3
"""
Fix common mypy type errors in calculator files.

This script fixes:
1. list[str] passed to Interpretation fields that expect tuple[str, ...]
2. tuple[Reference, ...] passed to ScoreResult where list[Reference] is expected
3. Missing type annotations on calculate methods
4. Missing type parameters for generic dict
"""

import re
import sys
from pathlib import Path


def fix_interpretation_lists(content: str) -> str:
    """Convert list literals to tuple() calls for Interpretation parameters."""
    # Pattern for recommendations=[], warnings=[], next_steps=[] with list literals
    patterns = [
        (r'(recommendations=)\[([^\]]*)\]', r'\1tuple([\2])'),
        (r'(warnings=)\[([^\]]*)\]', r'\1tuple([\2])'),
        (r'(next_steps=)\[([^\]]*)\]', r'\1tuple([\2])'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Pattern for variable references: recommendations=recommendations -> recommendations=tuple(recommendations)
    # But only inside Interpretation(...) calls
    # This is tricky - we need context-aware replacement
    # Use a simpler approach: only convert bare variable if it's a known pattern
    
    # For variables being passed in (not literals), wrap in tuple()
    # Pattern: only match if NOT already tuple() wrapped
    var_patterns = [
        (r'(\s+recommendations=)(?!tuple\()([a-z_]+),', r'\1tuple(\2),'),
        (r'(\s+warnings=)(?!tuple\()([a-z_]+),', r'\1tuple(\2),'),
        (r'(\s+next_steps=)(?!tuple\()([a-z_]+),', r'\1tuple(\2),'),
    ]
    
    for pattern, replacement in var_patterns:
        content = re.sub(pattern, replacement, content)
    
    return content


def fix_references_tuple(content: str) -> str:
    """Convert tuple references to list for ScoreResult."""
    # Pattern: references=self.metadata.references or references=tuple(...)
    content = re.sub(
        r'references=self\.metadata\.references,',
        'references=list(self.metadata.references),',
        content
    )
    content = re.sub(
        r'references=tuple\(self\.references\),',
        'references=list(self.references),',
        content
    )
    return content


def fix_calculate_method_signature(content: str) -> str:
    """Add type annotation to calculate method's **params parameter."""
    # Pattern: def calculate(self, **params) -> ScoreResult:
    content = re.sub(
        r'def calculate\(self, \*\*params\) -> ScoreResult:',
        'def calculate(self, **params: Any) -> ScoreResult:',
        content
    )
    return content


def fix_missing_dict_type_params(content: str) -> str:
    """Add type parameters to bare dict type hints."""
    # Pattern: ': dict =' where dict lacks type params
    content = re.sub(
        r': dict = \{',
        ': dict[str, Any] = {',
        content
    )
    return content


def ensure_any_import(content: str) -> str:
    """Ensure Any is imported from typing."""
    if 'from typing import' in content:
        # Check if Any is already imported
        import_match = re.search(r'from typing import ([^\n]+)', content)
        if import_match:
            imports = import_match.group(1)
            if 'Any' not in imports:
                # Add Any to the import
                new_imports = imports.rstrip() + ', Any'
                content = content.replace(
                    f'from typing import {imports}',
                    f'from typing import {new_imports}'
                )
    else:
        # Add typing import after docstring or at top
        if '"""' in content:
            # Find end of module docstring
            match = re.search(r'""".*?"""', content, re.DOTALL)
            if match:
                end = match.end()
                content = content[:end] + '\n\nfrom typing import Any' + content[end:]
        else:
            content = 'from typing import Any\n\n' + content
    
    return content


def fix_file(filepath: Path) -> bool:
    """Fix mypy errors in a single file. Returns True if changes were made."""
    content = filepath.read_text(encoding='utf-8')
    original = content
    
    # Apply fixes
    content = fix_interpretation_lists(content)
    content = fix_references_tuple(content)
    content = fix_calculate_method_signature(content)
    content = fix_missing_dict_type_params(content)
    
    # Ensure Any is imported if we added type annotations
    if content != original and 'Any' in content:
        content = ensure_any_import(content)
    
    if content != original:
        filepath.write_text(content, encoding='utf-8')
        return True
    return False


def main() -> None:
    """Main entry point."""
    # Files with known issues from mypy output
    calculator_dir = Path('src/domain/services/calculators')
    
    problem_files = [
        'tug.py', 'toronto_css.py', 'stone_score.py', 'sflt_plgf.py',
        'scorad.py', 'salt.py', 'pop_q.py', 'pasi.py', 'nds.py',
        'moca.py', 'mna.py', 'mmse.py', 'ipss.py', 'iciq_sf.py',
        'findrisc.py', 'epds.py', 'dlqi.py', 'cushingoid.py', 'cfs.py',
        'cas_graves.py', 'bsa_derm.py', 'bosniak.py', 'barthel_index.py',
        'score2.py', 'nutric_score.py', 'nrs_2002.py', 'icdsc.py', 'hfa_peff.py',
    ]
    
    fixed_count = 0
    for filename in problem_files:
        filepath = calculator_dir / filename
        if filepath.exists():
            if fix_file(filepath):
                print(f"Fixed: {filepath}")
                fixed_count += 1
            else:
                print(f"No changes: {filepath}")
        else:
            print(f"Not found: {filepath}")
    
    print(f"\nTotal files fixed: {fixed_count}")


if __name__ == '__main__':
    main()
