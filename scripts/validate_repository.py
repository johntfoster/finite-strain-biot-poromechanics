#!/usr/bin/env python3
"""Fail-closed audit of the standalone nonlinear-Biot repository."""

from __future__ import annotations

import csv
import argparse
import hashlib
import json
import re
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


def audit_conservative_initialization() -> None:
    provenance = json.loads((ROOT/'validation/conservative_formulation.json').read_text())
    for name, hashes in provenance['files'].items():
        require(sha256(ROOT/name) == hashes['local_sha256'], f'changed common kernel: {name}')
        upstream = (ROOT/name).read_bytes().replace(b'MulticomponentReactiveFlowApp', b'AnisotropicBiotApp')
        require(hashlib.sha256(upstream).hexdigest() == hashes['upstream_sha256'],
                f'common kernel differs beyond registration: {name}')
    elastic = json.loads((ROOT/'validation/conservative_initial_state.json').read_text())
    plastic = json.loads((ROOT/'validation/conservative_plastic_initial_state.json').read_text())
    require(elastic['accepted'] and plastic['accepted'], 'initial-state verification failed')
    require(max(elastic['maximum_mass_error'], elastic['maximum_pressure_error'],
                elastic['maximum_solid_mass_error']) < 1e-10,
            'nonzero elastic initial state violates sealed conservation')
    require(max(plastic['errors'].values()) < 1e-10,
            'prescribed plastic initial history violates sealed conservation')


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
        "validation/implicit_poroplastic_history.csv": {"time", "density", "solid_fraction", "b_avg", "a_p_avg"},
        "validation/implicit_poroplastic_feedback.csv": {"pressure", "B", "a_p", "a_p_reference"},
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
    require(abs(max(row["side_displacement"] for row in rows) - 0.040385621094306) <= 1.0e-12,
            "finite-deformation maximum lateral displacement drift")
    require(abs(final["side_displacement"] - 0.027017733345284) <= 1.0e-12,
            "finite-deformation final lateral displacement drift")
    require(abs(final["biot_average"] - 0.58219454704313) <= 1.0e-12,
            "finite-deformation final average Biot coefficient drift")
    require(abs(min(row["biot_minimum"] for row in rows if row["time"] == final["time"])
                - 0.58209924642057) <= 1.0e-12,
            "finite-deformation final minimum Biot coefficient drift")
    require(abs(max(row["biot_maximum"] for row in rows if row["time"] == final["time"])
                - 0.58224932954368) <= 1.0e-12,
            "finite-deformation final maximum Biot coefficient drift")
    require(max(row["solid_material_mass_constraint_l2"] for row in rows) <= 1.0e-12,
            "finite-deformation solid-mass diagnostic exceeds recorded bound")
    require(max(row["solid_mineral_eos_constraint_l2"] for row in rows) <= 3.0e-17,
            "finite-deformation mineral-EOS residual exceeds recorded bound")
    # This is a curated-data regression value for the matched logarithmic model.
    # The independent constitutive acceptance limit remains 1e-12.
    biot_error = max(row["biot_analytic_error_l2"] for row in rows)
    require(abs(biot_error - 4.6774019102469e-17) <= 1e-28,
            "finite-deformation Biot diagnostic differs from the recorded result")
    require(biot_error <= 1e-12, "finite-deformation Biot identity failed")

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
        require(times == {0.04, 0.1, 0.2, 0.3, 0.5, 0.7},
                f"unexpected contour times in {name}")
        contour_keys.append({(row["time"], row["X"], row["Y"]) for row in contour_rows})
    require(contour_keys[0] == contour_keys[1],
            "Biot and intrinsic-density contours use different samples")


def audit_implicit_poroplastic_results() -> None:
    record = json.loads((ROOT / "validation/implicit_poroplastic_verification.json").read_text())
    require(record.get("accepted") is True, "implicit poroplastic verification did not pass")
    require(record.get('parameters', {}).get('cohesion_Pa') == 2e7 and
            record.get('parameters', {}).get('hardening_modulus_Pa') == 1e8,
            'material-point publication does not use the coupled hardening parameters')
    limits = {"accumulated": 1e-10, "mass": 1e-10, "eos": 1e-10, "biot": 5e-8, "flow": 1e-9,
              "yield_residual": 1e-9, "stress": 2e-7, "determinant": 1e-9,
              "drained_stress": 2e-7, "double_prime_stress": 2e-7,
              "stress_transforms": 2e-7, "pressure_tangent": 2e-7,
              "pressure_integral": 2e-7}
    for name in ("history", "nonaxisymmetric", "rotated", "pressure_4e+08"):
        require(name in record, f"missing constitutive verification case: {name}")
        for metric, limit in limits.items():
            require(0 <= record[name][metric] <= limit, f"failed {name} {metric}")
    require(record["objectivity_stress_error"] <= 1e-10, "objectivity check failed")
    for stem in ("implicit_poroplastic_history", "implicit_poroplastic_feedback"):
        require(sha256(ROOT / "figures" / (stem + ".png")) ==
                sha256(ROOT / "docs/assets/img" / (stem + ".png")),
                f"manuscript and website figure mismatch: {stem}")


def audit_poroplastic_mandel_results() -> None:
    record = json.loads((ROOT / "validation/poroplastic_mandel_verification.json").read_text())
    require(record.get("accepted") is True, "coupled poroplastic verification did not pass")
    for name, expected in record["source_sha256"].items():
        require(sha256(ROOT / name) == expected, f"stale coupled verification source: {name}")
    require(record["storage"]["active_samples"] > 0, "plastic storage was not exercised")
    for metric, limit in record["storage"]["tolerances"].items():
        require(0 <= record["storage"]["errors"][metric] <= limit,
                f"coupled storage check failed: {metric}")
    require(record["jacobian"]["relative"] <= 1e-7 and
            record["jacobian"]["absolute"] <= 1e-5, "coupled plastic Jacobian failed")
    for case, values in record["mass"].items():
        for metric, tolerance in (("max_relative_reaction_mass_defect", 1e-8),
                                  ("max_relative_discrete_storage_defect", 1e-10),
                                  ("solid_mass_l2", 1e-12)):
            require(values[metric] <= tolerance, f"{case}: conservative balance failed: {metric}")
    require(record["mass"]["spatial_fine"]["max_relative_mass_defect"] <= .01,
            "water mass and Darcy outflow disagree by more than 1% of initial water mass")
    require(all(v <= 1e-7 for v in record["elastic_limit"]["field_errors"].values()),
            "coupled elastic-limit recovery failed")
    with (ROOT / "validation/poroplastic_mandel_contours.csv").open() as stream:
        rows = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(stream)]
    require({r["time"] for r in rows} == {0.04, 0.1, 0.2, 0.3, 0.5, 0.7},
            "plastic and elastic contour snapshot times must match")
    require(max(r["delta_B"] for r in rows) > 1e-3, "plastic coefficient contrast is absent")
    require(all(abs(r["B"] - r["B_el"] - r["delta_B"]) < 1e-10 for r in rows),
            "same-state elastic comparison is inconsistent")
    require(record['parameters'].get('hardening_modulus') == 1e8,
            'coupled publication data do not use the documented hardening law')
    b0 = 1. - record['parameters']['K']/record['parameters']['Ks']
    require(abs(b0 - .6) < 1e-12, 'publication figures use different reference coefficients')
    require(all(.965 <= r['B']/b0 <= 1.02 for r in rows),
            'Biot ratios lie outside the shared publication color scale')
    for case in ('temporal_fine', 'spatial_fine'):
        for field, limit in [('delta_b', 1e-8), ('ap', 1e-7), ('gamma', 1e-8)]:
            require(record['spatial_structure'][case][field]['maximum_transverse_rms'] <= limit,
                    f'unresolved spatial variation: {case} {field}')
    for stem in ("poroplastic_mandel_biot_ratio", "poroplastic_mandel_history"):
        require(sha256(ROOT / "figures" / (stem + ".png")) ==
                sha256(ROOT / "docs/assets/img" / (stem + ".png")),
                f"manuscript and website figure mismatch: {stem}")


def audit_poroplastic_spatial_stability() -> None:
    record = json.loads((ROOT/'validation/poroplastic_spatial_stability.json').read_text())
    require(record.get('accepted') is True and record.get('status') == 'complete',
            'spatial-stability verification is incomplete')
    for name, expected in record['source_sha256'].items():
        require(sha256(ROOT/name) == expected, f'stale spatial-stability source: {name}')
    baseline = record['cases']['baseline_perfect_plastic']['acoustic']['acoustic']
    require(any(r['determinant_changes_sign'] for r in baseline), 'baseline acoustic diagnosis missing')
    for name in ('hardening_coarse', 'hardening_fine', 'hardening_half_dt'):
        case = record['cases'][name]
        require(min(r['minimum_determinant_GPa2'] for r in case['acoustic']['acoustic']) > 0.,
                f'nonpositive sampled acoustic determinant: {name}')
        require(case['spatial_structure']['delta_b']['maximum_transverse_rms'] <= 1e-8,
                f'unresolved spatial variation: {name}')
    require(max(r['maximum'] for r in record['corrected_temporal_differences'].values()) <= 5e-6,
            'fine-grid time-step difference exceeds the stability verification limit')


def audit_provenance() -> None:
    record = json.loads((ROOT / "validation/provenance.yml").read_text(encoding="utf-8"))
    require(record.get("schema_version") == 2, "unsupported provenance schema")
    require('required_environment' in record and 'environment' not in record,
            'required and observed environments must be distinguished')
    require(set(record.get('execution_provenance', {})) ==
            {'material_point', 'coupled_plastic', 'spatial_stability', 'elastic_mandel', 'supplementary'},
            'missing execution provenance status')
    for name, expected in record.get("sha256", {}).items():
        path = ROOT / name
        require(path.is_file(), f"missing provenance input: {name}")
        require(sha256(path) == expected, f"provenance drift: {name}")


def audit_formulation_consistency() -> None:
    retired = ("ADTensorialPoroplasticBiotMaterial", "ADDruckerPragerPoroplasticBiotMaterial")
    for deck in (ROOT / "moose_app/test/tests").rglob("*.i"):
        require(not any(name in deck.read_text() for name in retired),
                f"obsolete constitutive model in {deck.relative_to(ROOT)}")
    for name in retired:
        require(not (ROOT / f"moose_app/src/materials/{name}.C").exists(),
                f"obsolete compiled constitutive model: {name}")
    for png in (ROOT / "figures").glob("*.png"):
        site = ROOT / "docs/assets/img" / png.name
        require(site.is_file() and sha256(png) == sha256(site),
                f"manuscript and website image mismatch: {png.name}")
    for page in (ROOT / "docs").glob("*.html"):
        for source in re.findall(r'<img[^>]+src="([^"]+)"', page.read_text()):
            require((page.parent / source).is_file(), f"missing image in {page.name}: {source}")
    with (ROOT / "validation/implicit_poroplastic_feedback.csv").open() as stream:
        final = list(csv.DictReader(stream))[-1]
    prose = (ROOT / "paper/sections/poroplastic_results.tex").read_text()
    require(float(final['B']) > float(final['B_virgin']) and
            float(final['a_p']) < float(final['a_p_reference']),
            'publication feedback does not support the stated restraint of dilation')
    require(r"c_0=20\ \mathrm{MPa}" in prose and r"H=100\ \mathrm{MPa}" in prose,
            'material-point manuscript parameters disagree with publication runs')
    domain = json.loads((ROOT / "validation/poroplastic_domain_checks.json").read_text())
    require(len(domain) == 1 and domain[0]["mean_stress_at_apex"] < 0
            and domain[0]["outcome"] == "rejected_outside_smooth_cone",
            "missing independently identified smooth-cone domain rejection")


def audit_manuscript() -> None:
    required = [
        "paper/main.tex",
        "paper/defs.tex",
        "paper/build/main.pdf",
        "paper/build/main.log",
        "figures/implicit_poroplastic_history.pgf",
        "figures/implicit_poroplastic_feedback.pgf",
        "figures/mandel_pressure_profiles.pgf",
        "figures/mandel_displacements.pgf",
        "figures/mandel_finite_deformation.pgf",
        "figures/mandel_normalized_biot_contours.pgf",
        "figures/poroplastic_mandel_biot_ratio.pgf",
        "figures/poroplastic_mandel_history.pgf"
    ]
    for name in required:
        require((ROOT / name).is_file(), f"missing manuscript resource: {name}")
    log = (ROOT / "paper/build/main.log").read_text(encoding="utf-8", errors="ignore")
    require("Undefined control sequence" not in log, "LaTeX undefined control sequence")
    require("There were undefined references" not in log, "LaTeX undefined references")
    require("Citation" not in log or "undefined" not in log.lower(), "LaTeX undefined citation")
    require((ROOT / "moose_app/nonlinear_biot_ad-opt").is_file(), "standalone MOOSE executable is missing")


def audit_equation_traceability() -> None:
    # PyYAML is pinned in the MOOSE environment, not required of system Python.
    result = subprocess.run(
        [str(ROOT / ".agent/shared/skills/setup-moose-conda/scripts/moose_conda_env.sh"),
         "run", "--", "python", "scripts/check_equation_traceability.py"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    require(result.returncode == 0, result.stderr.strip() or result.stdout.strip())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-manuscript", action="store_true",
                        help="Report the manuscript audit as skipped during a declared maintenance freeze")
    args = parser.parse_args(argv)
    if args.skip_manuscript:
        manifest = json.loads((ROOT / "research-project.yml").read_text())
        require(manifest["maintenance"]["manuscript_edits"] is False,
                "--skip-manuscript requires a declared manuscript maintenance freeze")
    audits = (
        audit_portability,
        audit_q2_q1_scope,
        audit_conservative_initialization,
        audit_sync,
        audit_equation_traceability,
        audit_curated_data,
        audit_finite_deformation_results,
        audit_implicit_poroplastic_results,
        audit_poroplastic_mandel_results,
        audit_poroplastic_spatial_stability,
        audit_provenance,
        audit_formulation_consistency,
        audit_manuscript
    )
    for audit in audits:
        if audit is audit_manuscript and args.skip_manuscript:
            print("SKIP audit_manuscript: manuscript maintenance freeze")
            continue
        audit()
        print(f"PASS {audit.__name__}")
    print("PASS non-manuscript repository audits" if args.skip_manuscript
          else "PASS standalone nonlinear-Biot repository audit")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        raise SystemExit(1)
