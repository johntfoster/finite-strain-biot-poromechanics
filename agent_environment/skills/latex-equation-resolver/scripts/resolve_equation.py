#!/usr/bin/env python3
"""Resolve rendered LaTeX equation numbers to labels via .aux files."""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


NEWLABEL_RE = re.compile(
    r"""\\newlabel\{(?P<label>[^}]+)\}\{\{(?P<number>(?:[^{}]|\{[^{}]*\})*)\}"""
)


def normalize_number(value: str) -> str:
    value = value.strip()
    if value.startswith("(") and value.endswith(")"):
        value = value[1:-1]
    value = value.strip()
    value = re.sub(r"\s+", "", value)
    value = value.replace(r"\theequation", "")
    return value


def strip_tex_markup(value: str) -> str:
    value = value.replace(r"\relax", "")
    value = re.sub(r"\\(?:textup|mathrm|mathbf|mathit|textrm)\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\[a-zA-Z]+", "", value)
    value = value.replace("{", "").replace("}", "")
    return normalize_number(value)


def iter_aux_files(root: Path) -> list[Path]:
    preferred_names = [
        "paper/build/main.aux",
        "paper/main.aux",
        "build/main.aux",
        "main.aux",
        "out/main.aux",
        "latex.out/main.aux",
    ]
    seen: set[Path] = set()
    aux_files: list[Path] = []

    for name in preferred_names:
        path = root / name
        if path.is_file():
            resolved = path.resolve()
            seen.add(resolved)
            aux_files.append(path)

    for path in sorted(root.rglob("*.aux")):
        ignored_parts = {".git", ".ragpi", ".mechpi", ".latex-edit-pi"}
        if ignored_parts.intersection(path.parts):
            continue
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            aux_files.append(path)

    return aux_files


def parse_aux(path: Path) -> list[tuple[str, str, Path]]:
    matches: list[tuple[str, str, Path]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return matches

    for match in NEWLABEL_RE.finditer(text):
        label = match.group("label")
        number = strip_tex_markup(match.group("number"))
        if number:
            matches.append((label, number, path))
    return matches


def candidate_source_files(root: Path) -> list[Path]:
    suffixes = {".tex", ".ltx", ".sty", ".cls"}
    ignored_dirs = {".git", "build", "out", ".ragpi", ".mechpi", ".latex-edit-pi"}
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in suffixes:
            continue
        if ignored_dirs.intersection(path.parts):
            continue
        files.append(path)
    return files


def find_label_locations(root: Path, labels: list[str]) -> dict[str, list[tuple[Path, int, bool]]]:
    escaped = {label: re.compile(r"\\label\{" + re.escape(label) + r"\}") for label in labels}
    locations: dict[str, list[tuple[Path, int, bool]]] = {label: [] for label in labels}
    equation_envs = {
        "equation",
        "align",
        "gather",
        "multline",
        "flalign",
        "alignat",
        "eqnarray",
    }
    begin_re = re.compile(r"\\begin\{([^}]+)\}")
    end_re = re.compile(r"\\end\{([^}]+)\}")
    for path in candidate_source_files(root):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        env_stack: list[str] = []
        for lineno, line in enumerate(lines, start=1):
            for env in begin_re.findall(line):
                env_stack.append(env.rstrip("*"))
            in_equation_env = any(env in equation_envs for env in env_stack)
            for label, pattern in escaped.items():
                if pattern.search(line):
                    looks_equation = in_equation_env or label.startswith(("eq:", "eqn:"))
                    locations[label].append((path, lineno, looks_equation))
            for env in end_re.findall(line):
                env = env.rstrip("*")
                if env in env_stack:
                    index = len(env_stack) - 1 - env_stack[::-1].index(env)
                    del env_stack[index:]
    return locations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("number", help="Rendered equation number, e.g. 12, (12), 3.7, A.4")
    parser.add_argument("root", nargs="?", default=".", help="LaTeX repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    target = normalize_number(args.number)
    if not root.is_dir():
        parser.error(f"root is not a directory: {root}")

    records: list[tuple[str, str, Path]] = []
    for aux_file in iter_aux_files(root):
        records.extend(parse_aux(aux_file))

    matches: list[tuple[str, str, Path]] = []
    seen_matches: set[tuple[str, str]] = set()
    for label, number, aux in records:
        if number != target:
            continue
        key = (label, number)
        if key in seen_matches:
            continue
        seen_matches.add(key)
        matches.append((label, number, aux))
    if not matches:
        print(f"No label found for rendered equation number {args.number!r} under {root}")
        if records:
            available = sorted({number for _, number, _ in records})
            print("Available rendered numbers include: " + ", ".join(available[:80]))
        else:
            print("No .aux labels found. Compile the manuscript first.")
        return 1

    locations = find_label_locations(root, [label for label, _, _ in matches])
    equation_matches = [
        match for match in matches
        if any(is_equation for _, _, is_equation in locations.get(match[0], []))
        or match[0].startswith(("eq:", "eqn:"))
    ]
    if equation_matches:
        matches = equation_matches

    for label, number, aux in matches:
        print(f"{number}\t{label}\taux={os.path.relpath(aux, root)}")
        for source, lineno, _ in locations.get(label, []):
            print(f"  source={os.path.relpath(source, root)}:{lineno}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
