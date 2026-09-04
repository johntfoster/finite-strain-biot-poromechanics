#!/usr/bin/env python3
"""Surface-scan LaTeX derivation files for audit anchors.

This is intentionally conservative. It does not prove derivations; it lists
equation spans, labels, references, derivative/state-set cues, and keywords that
help an agent decide where to inspect source manually.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


DISPLAY_BEGIN_RE = re.compile(
    r"\\begin\{(?P<env>equation\*?|align\*?|aligned|gather\*?|multline\*?|split)\}"
)
DISPLAY_END_RE = re.compile(r"\\end\{(?P<env>[^}]+)\}")
INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:eqref|ref|cref|Cref)\{([^}]+)\}")
CITE_RE = re.compile(r"\\(?:cite|citet|citep|autocite)(?:\[[^]]*\])*\{([^}]+)\}")
DERIV_RE = re.compile(
    r"(\\frac\{\\partial\b|\\frac\{D\b|\\pdv\b|\\dv\b|\\partial\s|\\nabla\b|\\delta\b)"
)
STATE_RE = re.compile(
    r"(state set|constitutive|depends on|function of|argument|independent field|free energy|entropy inequality|dissipation|affinity|chemical potential|multiplier|chain rule)",
    re.IGNORECASE,
)
SYMBOL_RE = re.compile(
    r"(\\psi|\\mu|\\eta|\\rho|\\phi|\\gamma|\\mathcal\{A\}|\\lambda|\\Lambda|\\mathbf\{v\}|\\mathbf\{w\}|\\boldsymbol|\\sigma|\\tau|F\^\{?[epM]\}?)"
)


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


def scan_file(path: Path) -> None:
    try:
        lines = path.read_text(errors="replace").splitlines()
    except OSError as exc:
        print(f"{path}: error: {exc}")
        return

    print(f"\n== {path} ==")
    stack: list[tuple[str, int, list[str]]] = []
    for lineno, raw in enumerate(lines, start=1):
        line = strip_comment(raw)

        begin = DISPLAY_BEGIN_RE.search(line)
        if begin:
            stack.append((begin.group("env"), lineno, [line]))
        elif stack:
            env, start, body = stack[-1]
            body.append(line)
            end = DISPLAY_END_RE.search(line)
            if end and end.group("env") == env:
                text = "\n".join(body)
                labels = LABEL_RE.findall(text)
                refs = REF_RE.findall(text)
                deriv = bool(DERIV_RE.search(text))
                symbols = sorted(set(SYMBOL_RE.findall(text)))
                print(
                    f"{path}:{start}-{lineno}: display env={env}"
                    f" labels={labels or '-'} refs={refs or '-'}"
                    f" derivative_cues={'yes' if deriv else 'no'}"
                    f" symbols={symbols[:12] or '-'}"
                )
                stack.pop()
            continue

        labels = LABEL_RE.findall(line)
        refs = REF_RE.findall(line)
        cites = CITE_RE.findall(line)
        state = STATE_RE.search(line)
        deriv = DERIV_RE.search(line)
        if labels or refs or cites or state or deriv:
            fields = []
            if labels:
                fields.append(f"labels={labels}")
            if refs:
                fields.append(f"refs={refs}")
            if cites:
                fields.append(f"cites={cites}")
            if state:
                fields.append(f"keyword={state.group(1)}")
            if deriv:
                fields.append("derivative_cue=yes")
            print(f"{path}:{lineno}: " + " ".join(fields))


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
