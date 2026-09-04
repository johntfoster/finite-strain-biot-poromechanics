#!/usr/bin/env python3
"""Flag likely display-math style issues in LaTeX source."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


DISPLAY_BEGIN_RE = re.compile(
    r"\\begin\{(?P<env>equation\*?|align\*?|gather\*?|multline\*?|flalign\*?|eqnarray\*?)\}"
)
DISPLAY_END_RE = re.compile(r"\\end\{(?P<env>[^}]+)\}")
INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
LOCK_BEGIN = "% AGENT-LOCK-BEGIN"
LOCK_END = "% AGENT-LOCK-END"


def strip_comment(line: str) -> str:
    escaped = False
    for i, ch in enumerate(line):
        if ch == "\\" and not escaped:
            escaped = True
            continue
        if ch == "%" and not escaped:
            return line[:i]
        escaped = False
    return line


def source_files(root: Path) -> list[Path]:
    main = root / "paper/main.tex"
    if not main.is_file():
        main = root / "main.tex"
    if not main.is_file():
        return sorted(root.glob("paper/sections/*.tex")) or sorted(root.glob("*.tex"))
    seen: set[Path] = set()
    ordered: list[Path] = [main]
    seen.add(main.resolve())
    for line in main.read_text(errors="replace").splitlines():
        for match in INPUT_RE.finditer(line):
            raw = match.group(1)
            path = (root / raw).with_suffix(".tex") if not raw.endswith(".tex") else root / raw
            try:
                resolved = path.resolve()
            except OSError:
                continue
            if path.is_file() and resolved not in seen:
                ordered.append(path)
                seen.add(resolved)
    return ordered


def selected_files(root: Path, names: list[str] | None) -> list[Path]:
    if names:
        return [(root / name).resolve() if not Path(name).is_absolute() else Path(name) for name in names]
    return source_files(root)


def equal_count(line: str) -> int:
    text = strip_comment(line)
    text = re.sub(r"\\(?:leq|geq|neq|equiv|approx|sim|to|in)\b", "", text)
    return len(re.findall(r"(?<![<>=])=(?![<>=])", text))


def body_lines(body: list[str]) -> list[tuple[int, str]]:
    return [(lineno, line) for lineno, line in body if strip_comment(line).strip()]


def analyze_display(path: Path, env: str, start: int, end: int, body: list[tuple[int, str]], locked: bool) -> None:
    text = "\n".join(line for _, line in body)
    numbered = not env.endswith("*")
    issues: list[str] = []

    for lineno, line in body_lines(body):
        if equal_count(line) >= 2:
            issues.append(f"line {lineno}: chained_equals")
        if len(strip_comment(line)) > 120:
            issues.append(f"line {lineno}: overlong_display_line")

    labels = LABEL_RE.findall(text)
    if env.startswith("eqnarray"):
        issues.append("legacy_eqnarray_environment")
    if numbered and not labels and re.search(r"\\(?:equiv|coloneqq|defeq)\b|:=", text):
        issues.append("numbered_helper_definition_without_label")
    if env.startswith("align") and numbered:
        row_count = sum(1 for _, line in body if r"\\" in strip_comment(line))
        label_count = len(labels)
        nonumber_count = len(re.findall(r"\\(?:notag|nonumber)\b", text))
        if row_count > 1 and label_count == 0 and nonumber_count == 0:
            issues.append("multirow_align_all_lines_numbered")
    if locked and issues:
        issues = ["locked_region_candidate:" + issue for issue in issues]

    if issues:
        print(f"{path}:{start}-{end}: env={env} labels={labels or '-'}")
        for issue in issues:
            print(f"  - {issue}")


def scan_file(path: Path) -> None:
    try:
        lines = path.read_text(errors="replace").splitlines()
    except OSError as exc:
        print(f"{path}: error: {exc}")
        return

    print(f"\n== {path} ==")
    locked = False
    stack: list[tuple[str, int, list[tuple[int, str]], bool]] = []
    for lineno, raw in enumerate(lines, start=1):
        if LOCK_BEGIN in raw:
            locked = True
        line = strip_comment(raw)
        begin = DISPLAY_BEGIN_RE.search(line)
        if begin:
            stack.append((begin.group("env"), lineno, [(lineno, line)], locked))
        elif stack:
            env, start, body, was_locked = stack[-1]
            body.append((lineno, line))
            end = DISPLAY_END_RE.search(line)
            if end and end.group("env") == env:
                analyze_display(path, env, start, lineno, body, was_locked or locked)
                stack.pop()
        if LOCK_END in raw:
            locked = False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="LaTeX repository root")
    parser.add_argument("--files", nargs="*", help="Specific .tex files to scan")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    for path in selected_files(root, args.files):
        scan_file(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
