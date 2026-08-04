#!/usr/bin/env python3
"""Audit source provenance, quantitative results, and manuscript artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HASHES = {
    "data/raw/GRL_Poromechanical_Measurements.xlsx":
        "c995782d56ef24e72a0df32999d49c12",
    "data/raw/Lawal_Kim_2026_Figure_3.jpg":
        "a8b16259f9f1689d5e40ab04037a4a8b",
}
EXPECTED_COUNTS = {"HT14": 16, "SP14": 15, "SP30": 15}


def md5(path: Path) -> str:
    digest = hashlib.md5()  # nosec: provenance checksum, not security
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for relative, expected in EXPECTED_HASHES.items():
        actual = md5(ROOT / relative)
        if actual != expected:
            raise SystemExit(f"{relative}: checksum {actual} != {expected}")

    observations = pd.read_csv(ROOT / "data/processed/lawal_kim_figure3c.csv")
    counts = observations.groupby("sample").size().to_dict()
    if counts != EXPECTED_COUNTS:
        raise SystemExit(f"unexpected Figure 3c point counts: {counts}")
    if observations["recompute_error"].abs().max() > 5.0e-15:
        raise SystemExit("released Biot coefficients fail B=1-K/K_s' check")

    metrics = json.loads(
        (ROOT / "validation/moose_pressure_path_metrics.json").read_text()
    )
    for sample in EXPECTED_COUNTS:
        values = metrics[sample]
        if values["maximum_implicit_tangent_error"] > 2.0e-6:
            raise SystemExit(f"{sample}: implicit tangent tolerance failed")
        if values["maximum_constraint_norm"] > 2.0e-8:
            raise SystemExit(f"{sample}: local constraint tolerance failed")
        if values["biot_rmse"] > 1.0e-2:
            raise SystemExit(f"{sample}: Biot RMSE tolerance failed")

    for relative in ("validation/acceptance.yml", "moose/source_manifest.yml"):
        document = yaml.safe_load((ROOT / relative).read_text())
        if not isinstance(document, dict):
            raise SystemExit(f"{relative}: expected a YAML mapping")

    expected_artifacts = (
        "figures/moose_lawal_kim_biot_replication.pdf",
        "figures/moose_lawal_kim_biot_replication.png",
        "paper/build/main.pdf",
    )
    for relative in expected_artifacts:
        if not (ROOT / relative).is_file():
            raise SystemExit(f"missing artifact: {relative}")

    log = (ROOT / "paper/build/main.log").read_text()
    forbidden = ("undefined references", "undefined citations", "Fatal error")
    for phrase in forbidden:
        if phrase in log:
            raise SystemExit(f"manuscript log contains: {phrase}")

    print(
        "PASS repository audit: 46 source points, three implicit-AD pressure "
        "paths, validated provenance, and compiled manuscript"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
