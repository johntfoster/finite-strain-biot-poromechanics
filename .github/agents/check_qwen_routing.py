#!/usr/bin/env python3
"""Validate qwen-routing.yml against the actual skill inventory.

Guarantees (exit nonzero on any failure):
  1. Every skill under agent_environment/skills/ is listed under exactly one
     destination in qwen-routing.yml (no gaps, no dupes).
  2. Every destination key is one of the allowed tokens.
  3. Every qwen* destination name exists in models.installed.
  4. Built-in skills (which may live in the VS Code copilot asset tree) are
     accepted by name without a portable file check.
  5. YAML parses and required top-level keys exist.

Usage:  python3 .github/agents/check_qwen_routing.py [repo_root]
Run from the repository root.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ALLOWED_DESTINATIONS = {
    "deepseek-keep",
    "qwen3:4b",
    "qwen3:30b-a3b",
    "qwen3-coder-next:q4_K_M",
    "direct-run",
}
QWEN_DESTINATIONS = {d for d in ALLOWED_DESTINATIONS if d.startswith("qwen")}


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    manifest_path = root / ".github" / "agents" / "qwen-routing.yml"
    skills_dir = root / "agent_environment" / "skills"

    problems: list[str] = []

    if not manifest_path.is_file():
        print(f"FAIL: manifest not found: {manifest_path}")
        return 1
    data = yaml.safe_load(manifest_path.read_text())
    if not isinstance(data, dict):
        print("FAIL: manifest is not a YAML mapping")
        return 1

    for key in ("models", "skills", "builtin_skills", "unlisted_rules", "availability_fallback"):
        if key not in data:
            problems.append(f"missing required key: {key}")

    models = data.get("models", {})
    installed = set(models.get("installed", []))
    default = models.get("default")
    if default not in installed:
        problems.append(f"models.default {default!r} not in models.installed")

    skills_map = data.get("skills", {})
    if not isinstance(skills_map, dict):
        problems.append("skills must be a mapping destination -> list")

    listed: list[str] = []
    for dest, names in (skills_map or {}).items():
        if dest not in ALLOWED_DESTINATIONS:
            problems.append(f"unknown destination key: {dest!r}")
        if not isinstance(names, list):
            problems.append(f"skills[{dest!r}] must be a list")
            continue
        listed.extend(names)
        if dest in QWEN_DESTINATIONS and dest not in installed:
            problems.append(f"destination {dest!r} is not an installed model")

    if len(listed) != len(set(listed)):
        dupes = {n for n in listed if listed.count(n) > 1}
        problems.append(f"skills listed more than once: {sorted(dupes)}")

    actual = sorted(p.name for p in skills_dir.glob("*/") if (p / "SKILL.md").is_file())
    missing = sorted(set(actual) - set(listed))
    unknown = sorted(set(listed) - set(actual))
    if missing:
        problems.append(f"skills NOT in manifest: {missing}")
    if unknown:
        problems.append(f"manifest lists non-existent skills: {unknown}")

    if not problems:
        print(
            f"OK: {len(actual)} manuscript skills covered; "
            f"{len(data.get('builtin_skills', []))} built-ins; "
            f"default model {default!r}"
        )
        return 0
    print("FAIL:")
    for p in problems:
        print(f"  - {p}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
