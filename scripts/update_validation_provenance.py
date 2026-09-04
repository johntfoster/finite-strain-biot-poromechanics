#!/usr/bin/env python3
"""Regenerate content hashes for the public nonlinear-Biot package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "validation/provenance.yml"

FILES = [
    "paper/main.tex",
    "paper/defs.tex",
    "paper/sections/introduction.tex",
    "paper/sections/finite_deformation_biot.tex",
    "paper/sections/implicit_ad_implementation.tex",
    "paper/sections/mandel_verification.tex",
    "paper/sections/conclusions.tex",
    "validation/mandel_implicit_biot.yml",
    "validation/mandel_pressure_profiles.csv",
    "validation/mandel_displacement_profiles.csv",
    "validation/mandel_large_deformation.csv",
    "validation/mandel_biot_contours.csv",
    "validation/mandel_density_contours.csv",
    "figures/mandel_pressure_profiles.pgf",
    "figures/mandel_displacements.pgf",
    "figures/mandel_finite_deformation.pgf",
    "figures/mandel_biot_contours.pgf",
    "figures/mandel_density_contours.pgf",
    "scripts/curate_mandel_profiles.py",
    "scripts/extract_mandel_density_contours.py",
    "scripts/plot_mandel_extended_results.py",
    "scripts/validate_repository.py",
    "scripts/update_validation_provenance.py",
    "moose/sync_manifest.json",
    "moose/sync_state.json"
]


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main() -> int:
    missing = [name for name in FILES if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit("missing provenance inputs: " + ", ".join(missing))
    record = {
        "schema_version": 1,
        "environment": {
            "moose_commit": "abafb58b67a6037c6723ffeb19647c84484466da",
            "moose_dev": "2026.02.20",
            "moose_libmesh": "2026.02.18_f8a1758",
            "moose_tools": "2026.02.16",
            "petsc": "3.24.4",
            "pandas": "3.0.1"
        },
        "commands": {
            "reproduce": "make reproduce",
            "build": "make build",
            "tests": "make test",
            "mandel": "make mandel",
            "figures": "make figures",
            "paper": "make paper",
            "validate": "make validate"
        },
        "sha256": {name: sha256(ROOT / name) for name in FILES}
    }
    OUTPUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUTPUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
