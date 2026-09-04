#!/usr/bin/env python3
"""Generate the manuscript AI-use disclosure from Git and a structured registry."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


GENERATED_MARKDOWN = Path("provenance/AI_USE.md")
GENERATED_LATEX = Path("provenance/ai_use_statement.tex")
REGISTRY = Path("provenance/ai-use.yml")


def git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=root, check=False, text=True, capture_output=True
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return completed.stdout.strip()


def repository_root() -> Path:
    return Path(git(Path.cwd(), "rev-parse", "--show-toplevel")).resolve()


def load_registry(root: Path) -> dict[str, Any]:
    # JSON is a strict, dependency-free subset of YAML. The .yml file therefore
    # remains usable by YAML tooling while fresh clones need only Python.
    data = json.loads((root / REGISTRY).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("unsupported provenance schema_version")
    status = data.get("disclosure", {}).get("status")
    if status not in {"active", "submission-frozen"}:
        raise ValueError("disclosure.status must be active or submission-frozen")
    paths = data.get("manuscript_paths")
    if not isinstance(paths, list) or not paths or not all(isinstance(p, str) for p in paths):
        raise ValueError("manuscript_paths must be a nonempty list of paths")
    for path in paths:
        candidate = Path(path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError(f"manuscript path must be repository-relative: {path}")
    return data


def commit_record(root: Path, revision: str, paths: list[str] | None = None) -> dict[str, str]:
    args = ["log", "-1", "--format=%H%x09%aI", revision]
    if paths:
        args.extend(["--", *paths])
    line = git(root, *args)
    if not line:
        raise RuntimeError(f"no Git commit found for {revision}")
    commit_hash, timestamp = line.split("\t", 1)
    return {"commit": commit_hash, "date": timestamp[:10]}


def first_manuscript_commit(root: Path, paths: list[str]) -> dict[str, str]:
    output = git(root, "log", "--reverse", "--format=%H%x09%aI", "--", *paths)
    if not output:
        raise RuntimeError("no manuscript-touching commit found")
    commit_hash, timestamp = output.splitlines()[0].split("\t", 1)
    return {"commit": commit_hash, "date": timestamp[:10]}


def human_date(value: str) -> str:
    parsed = dt.date.fromisoformat(value)
    return f"{parsed.day} {parsed.strftime('%B %Y')}"


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in value)


def tool_phrase(tools: list[dict[str, Any]], latex: bool = False) -> str:
    entries = []
    for item in tools:
        name = item["name"]
        versions = item.get("model_versions")
        if versions:
            name += f" ({', '.join(versions)})"
        else:
            name += " (model versions were not consistently recorded)"
        entries.append(latex_escape(name) if latex else name)
    if len(entries) == 1:
        return entries[0]
    if len(entries) == 2:
        return f"{entries[0]} and {entries[1]}"
    return ", ".join(entries[:-1]) + f", and {entries[-1]}"


def coverage(root: Path, registry: dict[str, Any], pending_date: str | None) -> dict[str, str]:
    status = registry["disclosure"]["status"]
    if status == "submission-frozen":
        tag = registry["disclosure"].get("submission_tag")
        if not tag:
            raise ValueError("submission-frozen disclosure requires submission_tag")
        # The tag, rather than a hash embedded in the commit itself, identifies
        # the immutable submission snapshot without a self-reference problem.
        git(root, "rev-parse", "--verify", f"refs/tags/{tag}")
        record = commit_record(root, tag)
        return {"kind": "final", "date": record["date"], "tag": tag}
    if pending_date:
        dt.date.fromisoformat(pending_date)
        return {"kind": "pending", "date": pending_date}
    record = commit_record(root, "HEAD")
    return {"kind": "latest", "date": record["date"], "commit": record["commit"]}


def render_markdown(registry: dict[str, Any], first: dict[str, str], end: dict[str, str]) -> str:
    start = human_date(first["date"])
    finish = human_date(end["date"])
    tools = tool_phrase(registry["tools"])
    if end["kind"] == "final":
        end_description = f"the final manuscript commit on {finish}, identified by tag `{end['tag']}`"
        state = "Submission-frozen"
    else:
        # Active output deliberately uses a date-only endpoint. A pre-commit
        # hook cannot know its containing commit hash, and embedding different
        # pending/latest wording would make the committed file instantly stale.
        end_description = f"the latest covered commit on {finish}"
        state = "Active"
    uses = "; ".join(registry["uses"])
    checks = "\n".join(f"- {item}" for item in registry["verification"])
    public_url = registry["project"].get("public_repository_url")
    public_record = public_url or "Unknown: a public repository URL has not yet been assigned."
    return f"""<!-- Generated by tools/update_ai_disclosure.py; edit provenance/ai-use.yml instead. -->
# AI-use provenance

Status: **{state}**

## Journal-facing statement

From {start} through {end_description}, the author used {tools} within an author-directed, version-controlled manuscript-development workflow. AI assistance was used for {uses}. The author determined the scientific questions, theoretical structure, assumptions, mathematical arguments, physical interpretations, and final wording. Every accepted change was reviewed by the author; equations and citations were checked against manuscript source and primary literature as applicable, and computational changes were subjected to the repository's applicable validation procedures. AI output was not treated as a scholarly source or credited with authorship. The author takes full responsibility for the accuracy, originality, and integrity of the work.

## Record boundaries

- First manuscript-touching commit: `{first['commit']}` ({start}).
- Coverage endpoint: {end_description}.
- Public record: {public_record}
- Model versions: Unknown where the structured registry records `unknown_not_consistently_recorded`; no versions have been inferred retrospectively.
- Git records accepted changes. It is not a complete transcript of prompts, rejected suggestions, transient output, or undocumented historical sessions.

## Recorded uses

""" + "\n".join(f"- {item[0].upper() + item[1:]}." for item in registry["uses"]) + f"""

## Human verification and responsibility

{checks}
- AI output was not treated as a scholarly source.
- The author retains responsibility for the work.
"""


def render_latex(registry: dict[str, Any], first: dict[str, str], end: dict[str, str]) -> str:
    start = human_date(first["date"])
    finish = human_date(end["date"])
    tools = tool_phrase(registry["tools"], latex=True)
    if end["kind"] == "final":
        endpoint = f"the final manuscript commit on {finish}, identified by tag {latex_escape(end['tag'])}"
    else:
        endpoint = f"the latest covered commit on {finish}"
    uses = "; ".join(registry["uses"])
    return f"""% Generated by tools/update_ai_disclosure.py; edit provenance/ai-use.yml instead.
\\section*{{Declaration of generative AI and AI-assisted technologies}}

From {start} through {endpoint}, the author used {tools} within an author-directed, version-controlled manuscript-development workflow. AI assistance was used for {latex_escape(uses)}. The author determined the scientific questions, theoretical structure, assumptions, mathematical arguments, physical interpretations, and final wording. Every accepted change was reviewed by the author; equations and citations were checked against manuscript source and primary literature as applicable, and computational changes were subjected to the repository's applicable validation procedures. AI output was not treated as a scholarly source or credited with authorship. The author takes full responsibility for the accuracy, originality, and integrity of the work.
"""


def update(path: Path, content: str, check: bool) -> bool:
    existing = path.read_text(encoding="utf-8") if path.exists() else None
    if existing == content:
        return True
    if check:
        print(f"stale generated file: {path}", file=sys.stderr)
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"updated {path}")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated files are stale")
    parser.add_argument(
        "--pending-date",
        metavar="YYYY-MM-DD",
        help="describe the pending commit using this date; intended for the pre-commit hook",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repository_root()
    registry = load_registry(root)
    first = first_manuscript_commit(root, registry["manuscript_paths"])
    end = coverage(root, registry, args.pending_date)
    markdown = render_markdown(registry, first, end)
    latex = render_latex(registry, first, end)
    results = [
        update(root / GENERATED_MARKDOWN, markdown, args.check),
        update(root / GENERATED_LATEX, latex, args.check),
    ]
    return 0 if all(results) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
