#!/usr/bin/env python3
"""Provision one repository-local Python dependency profile."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


PROFILES = {"research", "publication"}


def repository_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        text=True,
        capture_output=True,
    )
    return Path(result.stdout.strip()).resolve()


def venv_python(venv: Path) -> Path:
    windows = venv / "Scripts" / "python.exe"
    return windows if windows.is_file() else venv / "bin" / "python"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", choices=sorted(PROFILES))
    args = parser.parse_args()

    root = repository_root()
    requirements = root / "agent_environment" / "requirements" / f"{args.profile}.txt"
    venv = root / ".agent-runtime" / "venvs" / args.profile
    if not venv_python(venv).is_file():
        subprocess.run([sys.executable, "-m", "venv", str(venv)], cwd=root, check=True)
    python = venv_python(venv)
    environment = os.environ.copy()
    environment.setdefault("PIP_DISABLE_PIP_VERSION_CHECK", "1")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--requirement", str(requirements)],
        cwd=root,
        env=environment,
        check=True,
    )
    print(f"provisioned {args.profile} under .agent-runtime/venvs/{args.profile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
