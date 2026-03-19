#!/usr/bin/env python
"""Validate commit messages against a conventional-commit style policy."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOWED_PREFIXES = "build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test"
COMMIT_PATTERN = re.compile(rf"^(?:{ALLOWED_PREFIXES})(?:\([a-z0-9_./-]+\))?!?: [^\s].{{0,71}}$")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_commit_message.py <commit-msg-file>")
        return 2

    message = Path(sys.argv[1]).read_text(encoding="utf-8").strip()
    if COMMIT_PATTERN.match(message):
        return 0

    print("Invalid commit message.")
    print("Expected format: type(scope): summary")
    print("Allowed types: build, chore, ci, docs, feat, fix, perf, refactor, revert, style, test")
    print("Example: fix(mcp): align health endpoint version with pyproject")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
