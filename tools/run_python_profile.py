#!/usr/bin/env python3
"""Run a repository script with a provisioned Python profile."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


def repository_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        text=True,
        capture_output=True,
    )
    return Path(result.stdout.strip()).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile")
    parser.add_argument("script")
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    root = repository_root()
    script = Path(args.script)
    if script.is_absolute() or ".." in script.parts:
        parser.error("script must be repository-relative")
    venv = root / ".agent-runtime" / "venvs" / args.profile
    python = venv / "Scripts" / "python.exe"
    if not python.is_file():
        python = venv / "bin" / "python"
    if not python.is_file():
        parser.error(f"profile is not provisioned: {args.profile}")
    return subprocess.run(
        [str(python), str(root / script), *args.arguments], cwd=root, check=False
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
