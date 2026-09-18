#!/usr/bin/env python3
"""Regenerate content hashes for the public nonlinear-Biot package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "validation/provenance.yml"

FILES = [
    "validation/poroplastic_mandel_numerical_notes.md",
    "validation/poroplastic_spatial_stability.md",
    "validation/poroplastic_spatial_stability.json",
    "validation/scripts/check_poroplastic_spatial_stability.py",
    "validation/scripts/check_poroplastic_acoustic.py",
    "validation/scripts/check_poroplastic_hardening.py",
    "moose_app/include/materials/ADPoroplasticPoreVolumeMaterial.h",
    "moose_app/src/materials/ADPoroplasticPoreVolumeMaterial.C",
    "moose_app/include/postprocessors/NodalDofSum.h",
    "moose_app/src/postprocessors/NodalDofSum.C",
    "moose_app/test/tests/poroplastic_mandel/compression.i",
    "moose_app/test/tests/poroplastic_mandel/storage_samples.i",
    "moose_app/test/tests/poroplastic_mandel/tests",
    "validation/scripts/check_poroplastic_mandel.py",
    "validation/poroplastic_mandel_verification.json",
    "validation/poroplastic_mandel_history.csv",
    "validation/poroplastic_mandel_contours.csv",
    "scripts/plot_poroplastic_mandel.py",
    "figures/poroplastic_mandel_biot_ratio.png",
    "figures/poroplastic_mandel_biot_ratio.pgf",
    "figures/poroplastic_mandel_history.png",
    "figures/poroplastic_mandel_history.pgf",
    "docs/assets/img/poroplastic_mandel_biot_ratio.png",
    "docs/assets/img/poroplastic_mandel_history.png",
    "scripts/reproduce_mandel_publication.py",
    "validation/formulation_consistency_2026-09-14.md",
    "validation/poroplastic_domain_checks.json",
    "validation/scripts/check_stress_trace_derivation.py",
    "validation/scripts/check_stress_trace_biot_fraction.py",
    "validation/stress_trace_derivation_review.md",
    "moose_app/include/utils/MatchedLogMineralState.h",
    "moose_app/src/materials/ADLocalElasticMineralBiotMaterial.C",
    "moose_app/include/materials/ADLocalElasticMineralBiotMaterial.h",
    "moose_app/src/materials/ADVolumetricBarotropicSkeletonStressMaterial.C",
    "moose_app/src/materials/ADConstrainedSkeletonBiotMaterial.C",
    "moose_app/test/tests/mandel_implicit_biot/mandel_water_q2_q1.i",
    "moose_app/test/tests/mandel_implicit_biot/implicit_biot_q2_q1_jacobian.i",
    "moose_app/test/tests/mandel_implicit_biot/tests",
    "validation/scripts/check_mandel_implicit_biot.py",
    "all.bib",
    "validation/equation_to_moose_map.yml",
    "validation/theory_traceability.yml",
    "validation/acceptance.yml",
    "validation/manuscript_constitutive_audit_2026-09-08.md",
    "references/notes/manuscript_reference_audit_2026-09-08.md",
    "paper/sections/poroplastic_results.tex",
    "paper/sections/mandel_analytical_appendix.tex",
    "moose_app/src/materials/ADImplicitPoroplasticBiotMaterial.C",
    "moose_app/include/materials/ADImplicitPoroplasticBiotMaterial.h",
    "moose_app/src/materials/ADConstantDeformationGradientMaterial.C",
    "moose_app/include/materials/ADConstantDeformationGradientMaterial.h",
    "moose_app/test/tests/implicit_poroplastic/material_path.i",
    "moose_app/test/tests/implicit_poroplastic/active_jacobian.i",
    "moose_app/test/tests/implicit_poroplastic/tests",
    "validation/scripts/check_implicit_poroplastic.py",
    "validation/implicit_poroplastic_history.csv",
    "validation/implicit_poroplastic_feedback.csv",
    "validation/implicit_poroplastic_verification.json",
    "scripts/plot_implicit_poroplastic.py",
    "figures/implicit_poroplastic_history.pgf",
    "figures/implicit_poroplastic_feedback.pgf",
    "docs/poroplastic.html",
    "docs/assets/img/implicit_poroplastic_history.png",
    "docs/assets/img/implicit_poroplastic_feedback.png",
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
    "validation/poroplastic_delta_b.csv",
    "validation/poroplastic_b_feedback.csv",
    "validation/poroplastic_general_path.csv",
    "validation/poroplastic_load_unload.csv",
    "validation/tensorial_load_unload.csv",
    "figures/mandel_pressure_profiles.pgf",
    "figures/mandel_displacements.pgf",
    "figures/mandel_finite_deformation.pgf",
    "figures/mandel_normalized_biot_contours.pgf",
    "figures/poroplastic_delta_b.pgf",
    "figures/poroplastic_b_feedback.pgf",
    "figures/poroplastic_load_unload.pgf",
    "figures/tensorial_load_unload.pgf",
    "scripts/curate_mandel_profiles.py",
    "scripts/extract_mandel_density_contours.py",
    "scripts/plot_mandel_extended_results.py",
    "scripts/plot_poroplastic_delta_b.py",
    "scripts/plot_poroplastic_b_feedback.py",
    "scripts/plot_poroplastic_load_unload.py",
    "scripts/plot_tensorial_load_unload.py",
    "validation/scripts/check_poroplastic_general_path.py",
    "validation/scripts/check_poroplastic_load_unload.py",
    "validation/scripts/check_poroplastic_b_feedback.py",
    "validation/scripts/curate_poroplastic_delta_b.py",
    "scripts/validate_repository.py",
    "scripts/update_validation_provenance.py",
    "moose/sync_manifest.json",
    "moose/sync_state.json"
]


FILES = sorted(set(FILES) | {
    str(path.relative_to(ROOT))
    for pattern in (
        "moose_app/src/**/*.C", "moose_app/include/**/*.h",
        "moose_app/test/tests/**/*.i", "moose_app/test/tests/**/tests",
        "validation/scripts/*.py", "figures/*.png", "figures/*.pgf", "figures/*.pdf",
        "docs/assets/img/*.png", "docs/*.html",
    )
    for path in ROOT.glob(pattern)
})


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
            "derivation": "make derivation",
            "plastic": "make plastic",
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
