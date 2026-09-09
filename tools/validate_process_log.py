#!/usr/bin/env python3
"""Validate the six-section process log required in commit-message bodies."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


SECTIONS = (
    "Summary",
    "What changed & why",
    "Alternatives considered",
    "Dead ends & backtracks",
    "Open questions",
    "Next steps",
)
HEADING = re.compile(r"^(?:##\s+)?(" + "|".join(re.escape(item) for item in SECTIONS) + r")\s*$")


def validate(message: str) -> list[str]:
    errors: list[str] = []
    lines = message.splitlines()
    if not lines or not lines[0].strip():
        return ["commit subject is empty"]

    found: list[tuple[str, int]] = []
    for index, line in enumerate(lines[1:], start=1):
        match = HEADING.match(line.strip())
        if match:
            found.append((match.group(1), index))

    names = [name for name, _ in found]
    for section in SECTIONS:
        count = names.count(section)
        if count == 0:
            errors.append(f"missing section: {section}")
        elif count > 1:
            errors.append(f"duplicate section: {section}")

    if names != list(SECTIONS):
        errors.append("sections must appear once and in the required order")
        return errors

    for position, (name, line_index) in enumerate(found):
        end = found[position + 1][1] if position + 1 < len(found) else len(lines)
        content = [line.strip() for line in lines[line_index + 1 : end] if line.strip()]
        if not content:
            errors.append(f"empty section: {name}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message_file", type=Path)
    args = parser.parse_args()
    try:
        message = args.message_file.read_text(encoding="utf-8")
    except OSError as error:
        print(f"process-log validation failed: {error}", file=sys.stderr)
        return 2

    errors = validate(message)
    if errors:
        print("process-log validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        print("required body sections: " + " / ".join(SECTIONS), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
