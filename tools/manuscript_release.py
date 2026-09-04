#!/usr/bin/env python3
"""Audit, freeze, or history-filter a future standalone manuscript release."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


MANIFEST = Path("provenance/manuscript-export.json")
REGISTRY = Path("provenance/ai-use.yml")


def run(root: Path, argv: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(argv, cwd=root, text=True, capture_output=True, check=False)
    if check and result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"{' '.join(argv)} failed: {detail}")
    return result


def repository_root() -> Path:
    result = run(Path.cwd(), ["git", "rev-parse", "--show-toplevel"])
    return Path(result.stdout.strip()).resolve()


def load_manifest(root: Path) -> list[str]:
    data = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("unsupported export manifest schema_version")
    paths = data.get("paths")
    if not isinstance(paths, list) or not paths:
        raise ValueError("export manifest paths must be a nonempty list")
    for value in paths:
        path = Path(value)
        if not isinstance(value, str) or path.is_absolute() or ".." in path.parts:
            raise ValueError(f"export path must be repository-relative: {value}")
    return paths


def audit(root: Path) -> int:
    paths = load_manifest(root)
    missing = [path for path in paths if not (root / path).exists()]
    tracked = set(run(root, ["git", "ls-files"]).stdout.splitlines())
    uncovered = []
    for path in paths:
        candidate = root / path
        if candidate.is_file() and path not in tracked:
            uncovered.append(path)
        elif candidate.is_dir() and not any(item == path or item.startswith(path + "/") for item in tracked):
            uncovered.append(path)
    if missing:
        print("missing export paths:", *missing, sep="\n  ", file=sys.stderr)
    if uncovered:
        print("export paths with no tracked content:", *uncovered, sep="\n  ", file=sys.stderr)
    if missing or uncovered:
        return 1
    print(f"export manifest covers {len(paths)} repository-relative paths")
    return 0


def require_relative_destination(root: Path, value: str) -> Path:
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("destination must be repository-relative and contain no '..'")
    destination = (root / relative).resolve()
    runtime = (root / ".agent-runtime" / "exports").resolve()
    if destination.parent != runtime:
        raise ValueError("destination must be directly under .agent-runtime/exports/")
    return destination


def extract(root: Path, destination_value: str, dry_run: bool) -> int:
    paths = load_manifest(root)
    destination = require_relative_destination(root, destination_value)
    if destination.exists():
        raise ValueError(f"destination already exists: {destination_value}")
    commands = [
        ["git", "clone", "--no-local", ".", destination_value],
        [str(root / ".agent-runtime/venvs/publication/bin/git-filter-repo"),
         "--force", *[part for path in paths for part in ("--path", path)]],
    ]
    if dry_run:
        for command in commands:
            print(" ".join(command))
        return 0
    filter_repo = Path(commands[1][0])
    if not filter_repo.is_file():
        raise RuntimeError("publication profile is not provisioned; run tools/agentctl provision publication")
    destination.parent.mkdir(parents=True, exist_ok=True)
    run(root, commands[0])
    run(destination, commands[1])
    print(f"extracted manuscript history to {destination_value}")
    return 0


def freeze(root: Path, tag: str, apply: bool) -> int:
    if not tag or tag.startswith("-") or any(character.isspace() for character in tag):
        raise ValueError("tag must be a nonempty Git tag name without whitespace")
    run(root, ["git", "check-ref-format", f"refs/tags/{tag}"])
    dirty = run(root, ["git", "status", "--porcelain"]).stdout.strip()
    if dirty:
        raise RuntimeError("submission freeze requires a clean worktree")
    if not apply:
        print(f"would create annotated tag {tag} at HEAD")
        print("would set provenance/ai-use.yml to submission-frozen and regenerate disclosures")
        return 0
    run(root, ["git", "tag", "-a", tag, "-m", f"Freeze manuscript submission {tag}"])
    registry = json.loads((root / REGISTRY).read_text(encoding="utf-8"))
    registry["disclosure"]["status"] = "submission-frozen"
    registry["disclosure"]["submission_tag"] = tag
    (root / REGISTRY).write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    run(root, [sys.executable, "tools/update_ai_disclosure.py"])
    print("submission snapshot tagged; commit the provenance-only follow-up changes")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("audit")
    extract_parser = subparsers.add_parser("extract")
    extract_parser.add_argument("--destination", default=".agent-runtime/exports/manuscript")
    extract_parser.add_argument("--dry-run", action="store_true")
    freeze_parser = subparsers.add_parser("freeze")
    freeze_parser.add_argument("--tag", required=True)
    freeze_parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repository_root()
    if args.command == "audit":
        return audit(root)
    if args.command == "extract":
        return extract(root, args.destination, args.dry_run)
    return freeze(root, args.tag, args.apply)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
