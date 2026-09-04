#!/usr/bin/env python3
"""Surface-scan LaTeX citation contexts and BibTeX entries.

This helper is intentionally conservative. It does not verify source support or
metadata truth; it lists where citations occur and shows the local BibTeX entry
so an agent can perform evidence-based verification.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
CITE_RE = re.compile(
    r"\\(?P<cmd>cite|citet|citep|citealp|citeauthor|citeyear|autocite|parencite|textcite)"
    r"(?:\s*\[[^\]]*\]){0,2}\s*\{(?P<keys>[^}]+)\}"
)
BIB_RESOURCE_RE = re.compile(r"\\(?:bibliography|addbibresource)\{([^}]+)\}")
BIB_ENTRY_START_RE = re.compile(r"@\s*(?P<type>[A-Za-z]+)\s*\{\s*(?P<key>[^,\s]+)\s*,")
DOI_RE = re.compile(r"\bdoi\s*=\s*[{\"']([^}\"']+)[}\"']", re.IGNORECASE)
TITLE_RE = re.compile(r"\btitle\s*=\s*[{\"']([^}\"']+)[}\"']", re.IGNORECASE)
YEAR_RE = re.compile(r"\byear\s*=\s*[{\"']?([0-9]{4})", re.IGNORECASE)


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
    ordered: list[Path] = []

    def add(path: Path) -> None:
        try:
            resolved = path.resolve()
        except OSError:
            return
        if path.is_file() and resolved not in seen:
            ordered.append(path)
            seen.add(resolved)

    add(main)
    for line in main.read_text(errors="replace").splitlines():
        for match in INPUT_RE.finditer(strip_comment(line)):
            raw = match.group(1)
            candidate = root / raw
            if candidate.suffix != ".tex":
                candidate = candidate.with_suffix(".tex")
            add(candidate)
    return ordered


def bib_files(root: Path) -> list[Path]:
    main = root / "paper/main.tex"
    if not main.is_file():
        main = root / "main.tex"
    found: list[Path] = []
    if main.is_file():
        for line in main.read_text(errors="replace").splitlines():
            for match in BIB_RESOURCE_RE.finditer(strip_comment(line)):
                for raw in match.group(1).split(","):
                    candidate = root / raw.strip()
                    if candidate.suffix not in {".bib", ".biblatex"}:
                        candidate = candidate.with_suffix(".bib")
                    if candidate.is_file():
                        found.append(candidate)
    default = root / "all.bib"
    if default.is_file() and default not in found:
        found.append(default)
    return found


def split_keys(raw: str) -> list[str]:
    return [key.strip() for key in raw.split(",") if key.strip()]


def line_context(lines: list[str], lineno: int, radius: int) -> str:
    start = max(1, lineno - radius)
    end = min(len(lines), lineno + radius)
    return " ".join(strip_comment(lines[i - 1]).strip() for i in range(start, end + 1)).strip()


def find_citations(paths: list[Path], wanted: set[str], radius: int) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for path in paths:
        try:
            lines = path.read_text(errors="replace").splitlines()
        except OSError:
            continue
        for lineno, raw in enumerate(lines, start=1):
            line = strip_comment(raw)
            for match in CITE_RE.finditer(line):
                keys = split_keys(match.group("keys"))
                for key in keys:
                    if wanted and key not in wanted:
                        continue
                    context = line_context(lines, lineno, radius)
                    hits.setdefault(key, []).append(
                        f"{path}:{lineno}: \\{match.group('cmd')}{{{match.group('keys')}}} :: {context}"
                    )
    return hits


def parse_bib_entries(paths: list[Path]) -> tuple[dict[str, str], dict[str, list[str]]]:
    entries: dict[str, str] = {}
    duplicates: dict[str, list[str]] = {}
    for path in paths:
        text = path.read_text(errors="replace")
        starts = list(BIB_ENTRY_START_RE.finditer(text))
        for index, match in enumerate(starts):
            key = match.group("key")
            end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
            entry = text[match.start() : end].strip()
            location = f"{path}:{text.count(chr(10), 0, match.start()) + 1}"
            if key in entries:
                duplicates.setdefault(key, []).append(location)
            else:
                entries[key] = f"{location}\n{entry}"
    return entries, duplicates


def summarize_entry(entry: str) -> str:
    doi = DOI_RE.search(entry)
    title = TITLE_RE.search(entry)
    year = YEAR_RE.search(entry)
    pieces = []
    if title:
        pieces.append(f"title={title.group(1)}")
    if year:
        pieces.append(f"year={year.group(1)}")
    pieces.append(f"doi={doi.group(1) if doi else 'MISSING'}")
    return "; ".join(pieces)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="LaTeX repository root")
    parser.add_argument("--key", action="append", help="Citation key to filter; repeatable")
    parser.add_argument("--context-lines", type=int, default=1)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    wanted = set(args.key or [])
    tex_paths = source_files(root)
    bib_paths = bib_files(root)
    citations = find_citations(tex_paths, wanted, args.context_lines)
    entries, duplicates = parse_bib_entries(bib_paths)

    keys = sorted(wanted or citations.keys() or entries.keys())
    print(f"Root: {root}")
    print("Bib files: " + (", ".join(str(path) for path in bib_paths) or "none"))
    for key in keys:
        print(f"\n== {key} ==")
        for hit in citations.get(key, []):
            print(f"CITE {hit}")
        if key not in citations:
            print("CITE none found")
        if key in entries:
            print(f"BIB {summarize_entry(entries[key])}")
            print(entries[key])
        else:
            print("BIB MISSING")
        if key in duplicates:
            print("DUPLICATES " + ", ".join(duplicates[key]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
