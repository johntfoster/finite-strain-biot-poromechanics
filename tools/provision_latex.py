#!/usr/bin/env python3
"""Provision a LaTeX toolchain with the host's supported package manager."""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys


def run(argv: list[str]) -> None:
    subprocess.run(argv, check=True)


def main() -> int:
    if shutil.which("pdflatex") and shutil.which("bibtex"):
        print("LaTeX toolchain already available")
        return 0
    system = platform.system()
    if system == "Linux" and shutil.which("apt-get"):
        prefix = [] if getattr(__import__("os"), "geteuid", lambda: 1)() == 0 else ["sudo"]
        run([*prefix, "apt-get", "update"])
        run([*prefix, "apt-get", "install", "-y", "texlive-latex-extra", "texlive-bibtex-extra", "texlive-fonts-recommended"])
    elif system == "Darwin" and shutil.which("brew"):
        run(["brew", "install", "--cask", "mactex-no-gui"])
    elif system == "Windows" and shutil.which("winget"):
        run(["winget", "install", "--id", "MiKTeX.MiKTeX", "--exact"])
    else:
        print("no supported package manager found; install pdflatex and bibtex", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
