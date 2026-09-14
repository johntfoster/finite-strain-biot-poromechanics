#!/usr/bin/env python3
"""Check one lazily provisioned dependency profile."""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def module_in(profile: str, name: str) -> bool:
    python = ROOT / ".agent-runtime" / "venvs" / profile / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    if not python.is_file():
        return False
    return subprocess.run([str(python), "-c", f"import {name}"], cwd=ROOT).returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", choices=["manuscript", "research", "publication", "moose"])
    profile = parser.parse_args().profile
    if profile == "manuscript":
        return 0 if all(shutil.which(name) for name in ("pdflatex", "bibtex")) else 1
    if profile == "research":
        return 0 if module_in(profile, "pypdf") else 1
    if profile == "publication":
        binary = ROOT / ".agent-runtime/venvs/publication/bin/git-filter-repo"
        if sys.platform == "win32":
            binary = ROOT / ".agent-runtime/venvs/publication/Scripts/git-filter-repo.exe"
        return 0 if binary.is_file() else 1
    helper = ROOT / ".agent/shared/skills/setup-moose-conda/scripts/moose_conda_env.sh"
    return subprocess.run([str(helper), "status"], cwd=ROOT).returncode


if __name__ == "__main__":
    raise SystemExit(main())
