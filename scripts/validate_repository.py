#!/usr/bin/env python3
"""Fail-closed audit of the standalone nonlinear-Biot repository."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def audit_portability() -> None:
    forbidden = (
        "/home/jfoster",
        "$HOME/projects",
        "../multicomponent_reactive_flow",
        "PARENT_APP_DIR",
        "parent_base_18e88c43",
        "upstream_worktree.patch"
    )
    excluded = {".git", ".agent-runtime", "build", "__pycache__"}
    suffixes = {".md", ".tex", ".py", ".json", ".yml", ".yaml", ".i", ".txt", ""}
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in excluded for part in path.relative_to(ROOT).parts):
            continue
        relative = path.relative_to(ROOT)
        if path.resolve() == Path(__file__).resolve() or relative == Path("moose_app/.previous_test_results.json"):
            continue
        if path.suffix.lower() not in suffixes:
            continue
        content = path.read_bytes()
        if b"\x00" in content:
            continue
        text = content.decode("utf-8", errors="ignore")
        require(not any(token in text for token in forbidden), f"nonportable path or obsolete reconstruction reference in {path.relative_to(ROOT)}")


def audit_q2_q1_scope() -> None:
    paths = [
        ROOT / "AGENTS.md",
        ROOT / "README.md",
        ROOT / "validation/acceptance.yml",
        ROOT / "validation/equation_to_moose_map.yml",
        ROOT / "validation/theory_traceability.yml",
        ROOT / "moose_app/test/tests/mandel_implicit_biot/mandel_water_q2_q1.i",
        ROOT / "moose_app/test/tests/mandel_implicit_biot/implicit_biot_q2_q1_jacobian.i"
    ]
    forbidden_objects = ("ADEGReconstructedScalarMaterial", "ADEnrichedGalerkin", "p_enr", "p_total")
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    require(not any(token in combined for token in forbidden_objects), "active Q2/Q1 path still references an EG object or reconstructed pressure")
    deck = paths[-2].read_text(encoding="utf-8")
    require("type = ADBiotPressureStorageMaterial" in deck, "Mandel deck lacks exact water mass storage")
    require("reference_density = ${water_density_kg_m3}" in deck, "Mandel water storage lacks the barotropic density reference")
    require(
        "reference_solid_volume_fraction = ${initial_solid_volume_fraction}" in deck,
        "Mandel water storage lacks the undeformed reference accumulation state",
    )
    require("solid_bulk_modulus" not in deck, "Mandel water storage still imposes a Biot storage modulus")
    require("type = ADBiotDarcyReferenceFluxMaterial" in deck, "Mandel deck lacks reduced Biot Darcy flux")


def audit_sync() -> None:
    result = subprocess.run(
        [str(ROOT / "tools/sync_biot_moose.py"), "check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False
    )
    require(result.returncode == 0, result.stderr.strip() or result.stdout.strip())


def audit_curated_data() -> None:
    required = {
        "validation/mandel_pressure_profiles.csv": {"time", "x"},
        "validation/mandel_displacement_profiles.csv": {"time", "component", "coordinate", "displacement"},
        "validation/mandel_large_deformation.csv": {"time"},
        "validation/mandel_biot_contours.csv": {"time", "X", "Y", "biot_coefficient"},
        "validation/mandel_density_contours.csv": {"time", "X", "Y", "intrinsic_solid_density_ratio"}
    }
    for name, columns in required.items():
        with (ROOT / name).open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            require(reader.fieldnames is not None and columns.issubset(reader.fieldnames), f"missing required columns in {name}")
            require(next(reader, None) is not None, f"empty curated result: {name}")
    summary = (ROOT / "validation/mandel_implicit_biot.yml").read_text(encoding="utf-8")
    require("status: pass" in summary, "Mandel benchmark is not recorded as passing")
    require("pressure_enrichment: false" in summary, "Mandel record does not declare pure Q1 pressure")


def audit_finite_deformation_results() -> None:
    """Recompute the publication metrics from the curated continuation artifacts."""
    with (ROOT / "validation/mandel_large_deformation.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        rows = [
            {name: float(value) for name, value in row.items()}
            for row in csv.DictReader(stream)
        ]
    require(rows, "empty finite-deformation continuation")
    final = rows[-1]
    require(abs(max(row["side_displacement"] for row in rows) - 0.03679468984281) <= 1.0e-12,
            "finite-deformation maximum lateral displacement drift")
    require(abs(final["side_displacement"] - 0.027204092415354) <= 1.0e-12,
            "finite-deformation final lateral displacement drift")
    require(abs(final["biot_average"] - 0.51417410820727) <= 1.0e-12,
            "finite-deformation final average Biot coefficient drift")
    require(abs(min(row["biot_minimum"] for row in rows if row["time"] == final["time"])
                - 0.51360255434187) <= 1.0e-12,
            "finite-deformation final minimum Biot coefficient drift")
    require(abs(max(row["biot_maximum"] for row in rows if row["time"] == final["time"])
                - 0.51450277385234) <= 1.0e-12,
            "finite-deformation final maximum Biot coefficient drift")
    require(max(row["solid_material_mass_constraint_l2"] for row in rows) <= 2.8e-5,
            "finite-deformation solid-mass diagnostic exceeds recorded bound")
    require(max(row["solid_mineral_eos_constraint_l2"] for row in rows) <= 3.0e-17,
            "finite-deformation mineral-EOS residual exceeds recorded bound")
    require(max(row["biot_analytic_error_l2"] for row in rows) <= 4.0e-17,
            "finite-deformation Biot identity exceeds recorded bound")

    contour_specs = (
        ("validation/mandel_biot_contours.csv", "biot_coefficient"),
        ("validation/mandel_density_contours.csv", "intrinsic_solid_density_ratio"),
    )
    contour_keys = []
    for name, value_name in contour_specs:
        with (ROOT / name).open(newline="", encoding="utf-8") as stream:
            contour_rows = list(csv.DictReader(stream))
        require(contour_rows and all(value_name in row for row in contour_rows),
                f"invalid finite-deformation contour artifact: {name}")
        times = {float(row["time"]) for row in contour_rows}
        require(times == {0.0, 0.046, 0.094, 0.206, 0.398, 0.702},
                f"unexpected contour times in {name}")
        contour_keys.append({(row["time"], row["X"], row["Y"]) for row in contour_rows})
    require(contour_keys[0] == contour_keys[1],
            "Biot and intrinsic-density contours use different samples")


def audit_provenance() -> None:
    record = json.loads((ROOT / "validation/provenance.yml").read_text(encoding="utf-8"))
    require(record.get("schema_version") == 1, "unsupported provenance schema")
    for name, expected in record.get("sha256", {}).items():
        path = ROOT / name
        require(path.is_file(), f"missing provenance input: {name}")
        require(sha256(path) == expected, f"provenance drift: {name}")


def audit_manuscript() -> None:
    required = [
        "paper/main.tex",
        "paper/defs.tex",
        "paper/build/main.pdf",
        "paper/build/main.log",
        "figures/mandel_pressure_profiles.pgf",
        "figures/mandel_displacements.pgf",
        "figures/mandel_finite_deformation.pgf",
        "figures/mandel_biot_contours.pgf",
        "figures/mandel_density_contours.pgf"
    ]
    for name in required:
        require((ROOT / name).is_file(), f"missing manuscript resource: {name}")
    log = (ROOT / "paper/build/main.log").read_text(encoding="utf-8", errors="ignore")
    require("Undefined control sequence" not in log, "LaTeX undefined control sequence")
    require("There were undefined references" not in log, "LaTeX undefined references")
    require("Citation" not in log or "undefined" not in log.lower(), "LaTeX undefined citation")
    require((ROOT / "moose_app/nonlinear_biot_ad-opt").is_file(), "standalone MOOSE executable is missing")


def main() -> int:
    audits = (
        audit_portability,
        audit_q2_q1_scope,
        audit_sync,
        audit_curated_data,
        audit_finite_deformation_results,
        audit_provenance,
        audit_manuscript
    )
    for audit in audits:
        audit()
        print(f"PASS {audit.__name__}")
    print("PASS standalone nonlinear-Biot repository audit")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        raise SystemExit(1)
