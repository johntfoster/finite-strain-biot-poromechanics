#!/usr/bin/env python3
"""Verify the water-filled Mandel problem with an implicit-AD Biot coefficient."""

from __future__ import annotations

import argparse
import csv
import functools
import hashlib
import json
import math
import shlex
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP_DIR = ROOT / "moose_app"
APP_CANDIDATES = (
    APP_DIR / "nonlinear_biot_ad-opt",
    APP_DIR / "multicomponent_reactive_flow-opt",
)
APP = next((candidate for candidate in APP_CANDIDATES if candidate.is_file()), APP_CANDIDATES[0])
DECK = APP_DIR / "test/tests/mandel_implicit_biot/mandel_water_q2_q1.i"

ROOT_COUNT = 12
REFERENCE_ROOT_COUNT = 128
PROFILE_POINT_COUNT = 401
REPORTED_TIME_STEP = 0.002
REPORTED_END_TIME = 0.702
REPORTED_TIMES = tuple(
    round(index * REPORTED_TIME_STEP, 12)
    for index in range(1, round(REPORTED_END_TIME / REPORTED_TIME_STEP) + 1)
)

LOAD = 1.0e5
SKELETON_BULK_MODULUS = 1.0e9
SHEAR_MODULUS = 0.75e9
MINERAL_BULK_MODULUS = 2.5e9
WATER_BULK_MODULUS = 8.0e9
POROSITY = 0.1
BIOT_COEFFICIENT = 1.0 - SKELETON_BULK_MODULUS / MINERAL_BULK_MODULUS
HYDRAULIC_MOBILITY = 1.5e-9
HEIGHT = 0.1

PRESSURE_ERROR_LIMIT = 4.0e-2
DISPLACEMENT_ERROR_LIMIT = 8.0e-3
LOAD_ERROR_LIMIT = 3.0e-3
BIOT_REFERENCE_LIMIT = 1.0e-4
BIOT_IDENTITY_LIMIT = 1.0e-12
BIOT_CENTERED_DIFFERENCE_LIMIT = 1.0e-7
CONSTRAINT_LIMIT = 1.0e-9
SPATIAL_REFINEMENT_DIFFERENCE_LIMIT = 1.0e-2
TEMPORAL_REFINEMENT_DIFFERENCE_LIMIT = 3.0e-2
FINER_TEMPORAL_REFINEMENT_DIFFERENCE_LIMIT = 2.0e-2
ROOT_TRUNCATION_PRESSURE_DIFFERENCE_LIMIT = 2.0e-5
ROOT_TRUNCATION_DISPLACEMENT_DIFFERENCE_LIMIT = 6.0e-12


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parameters() -> dict[str, float]:
    storage_modulus = 1.0 / (
        (1.0 - POROSITY) / MINERAL_BULK_MODULUS
        - SKELETON_BULK_MODULUS / MINERAL_BULK_MODULUS**2
        + POROSITY / WATER_BULK_MODULUS
    )
    undrained_bulk_modulus = (
        SKELETON_BULK_MODULUS + BIOT_COEFFICIENT**2 * storage_modulus
    )
    skempton = BIOT_COEFFICIENT * storage_modulus / undrained_bulk_modulus
    poisson = (3.0 * SKELETON_BULK_MODULUS - 2.0 * SHEAR_MODULUS) / (
        2.0 * (3.0 * SKELETON_BULK_MODULUS + SHEAR_MODULUS)
    )
    undrained_poisson = (3.0 * undrained_bulk_modulus - 2.0 * SHEAR_MODULUS) / (
        2.0 * (3.0 * undrained_bulk_modulus + SHEAR_MODULUS)
    )
    diffusivity = (
        2.0
        * SHEAR_MODULUS
        * (1.0 - poisson)
        * (undrained_poisson - poisson)
        * HYDRAULIC_MOBILITY
        / (
            BIOT_COEFFICIENT**2
            * (1.0 - undrained_poisson)
            * (1.0 - 2.0 * poisson) ** 2
        )
    )
    return {
        "storage_modulus": storage_modulus,
        "undrained_bulk_modulus": undrained_bulk_modulus,
        "skempton_coefficient": skempton,
        "poisson_ratio": poisson,
        "undrained_poisson_ratio": undrained_poisson,
        "diffusivity": diffusivity,
        "pressure_scale": LOAD * skempton * (1.0 + undrained_poisson) / 3.0,
    }


@functools.cache
def mandel_roots(root_count: int = ROOT_COUNT) -> tuple[float, ...]:
    """Return the positive roots of tan(alpha)=c alpha for current parameters."""
    values = parameters()
    coefficient = (1.0 - values["poisson_ratio"]) / (
        values["undrained_poisson_ratio"] - values["poisson_ratio"]
    )
    roots = []
    for index in range(root_count):
        lower = index * math.pi + 1.0e-12
        upper = index * math.pi + 0.5 * math.pi - 1.0e-12
        for _ in range(80):
            midpoint = 0.5 * (lower + upper)
            if math.tan(midpoint) - coefficient * midpoint > 0.0:
                upper = midpoint
            else:
                lower = midpoint
        roots.append(0.5 * (lower + upper))
    return tuple(roots)


def analytical_solution(
    time: float, x: float, root_count: int = ROOT_COUNT
) -> tuple[float, float, float]:
    values = parameters()
    poisson = values["poisson_ratio"]
    undrained_poisson = values["undrained_poisson_ratio"]
    pressure_sum = 0.0
    displacement_sum = 0.0
    for root in mandel_roots(root_count):
        denominator = root - math.sin(root) * math.cos(root)
        exponential = math.exp(-root**2 * values["diffusivity"] * time)
        pressure_sum += (
            math.sin(root) / denominator * math.cos(root * x)
            - math.sin(root) * math.cos(root) / denominator
        ) * exponential
        displacement_sum += (
            math.sin(root) * math.cos(root) / denominator * exponential
        )
    pressure = (
        2.0
        * LOAD
        * values["skempton_coefficient"]
        * (1.0 + undrained_poisson)
        / 3.0
        * pressure_sum
    )
    side_displacement = LOAD * poisson / (2.0 * SHEAR_MODULUS) + (
        LOAD * (1.0 - undrained_poisson) / SHEAR_MODULUS * displacement_sum
    )
    top_displacement = -LOAD * (1.0 - poisson) * HEIGHT / (
        2.0 * SHEAR_MODULUS
    ) + (
        LOAD
        * (1.0 - undrained_poisson)
        * HEIGHT
        / SHEAR_MODULUS
        * displacement_sum
    )
    return pressure, side_displacement, top_displacement


def analytical_displacement(
    component: str, coordinate: float, time: float, root_count: int
) -> float:
    values = parameters()
    poisson = values["poisson_ratio"]
    undrained_poisson = values["undrained_poisson_ratio"]
    uniform_sum = 0.0
    spatial_sum = 0.0
    for root in mandel_roots(root_count):
        denominator = root - math.sin(root) * math.cos(root)
        exponential = math.exp(-root**2 * values["diffusivity"] * time)
        uniform_sum += (
            math.sin(root) * math.cos(root) / denominator * exponential
        )
        spatial_sum += (
            math.cos(root)
            * math.sin(root * coordinate)
            / denominator
            * exponential
        )
    if component == "ux":
        return (
            LOAD * poisson / (2.0 * SHEAR_MODULUS)
            - LOAD * undrained_poisson / SHEAR_MODULUS * uniform_sum
        ) * coordinate + LOAD / SHEAR_MODULUS * spatial_sum
    if component == "uy":
        return (
            -LOAD * (1.0 - poisson) / (2.0 * SHEAR_MODULUS)
            + LOAD * (1.0 - undrained_poisson) / SHEAR_MODULUS * uniform_sum
        ) * coordinate
    raise ValueError(f"unknown displacement component: {component}")


def root_truncation_audit() -> dict[str, float | int | list[float]]:
    values = parameters()
    pressure_scale = values["pressure_scale"]
    undrained_poisson = values["undrained_poisson_ratio"]
    tail_roots = mandel_roots(REFERENCE_ROOT_COUNT)[ROOT_COUNT:]
    maximum_pressure_difference = 0.0
    maximum_displacement_difference = 0.0
    evaluated_time_count = 0
    for time in REPORTED_TIMES:
        terms = []
        for root in tail_roots:
            denominator = root - math.sin(root) * math.cos(root)
            exponential = math.exp(-root**2 * values["diffusivity"] * time)
            terms.append((root, denominator, exponential))
        uniform_tail = sum(
            math.sin(root) * math.cos(root) / denominator * exponential
            for root, denominator, exponential in terms
        )
        for index in range(PROFILE_POINT_COUNT):
            x = index / (PROFILE_POINT_COUNT - 1)
            pressure_tail = (
                2.0
                * LOAD
                * values["skempton_coefficient"]
                * (1.0 + undrained_poisson)
                / 3.0
                * sum(
                    math.sin(root)
                    * (math.cos(root * x) - math.cos(root))
                    / denominator
                    * exponential
                    for root, denominator, exponential in terms
                )
            )
            maximum_pressure_difference = max(
                maximum_pressure_difference,
                abs(pressure_tail) / pressure_scale,
            )
            spatial_tail = sum(
                math.cos(root)
                * math.sin(root * x)
                / denominator
                * exponential
                for root, denominator, exponential in terms
            )
            ux_tail = (
                -LOAD * undrained_poisson / SHEAR_MODULUS * uniform_tail * x
                + LOAD / SHEAR_MODULUS * spatial_tail
            )
            maximum_displacement_difference = max(
                maximum_displacement_difference, abs(ux_tail)
            )
            y = HEIGHT * x
            uy_tail = (
                LOAD
                * (1.0 - undrained_poisson)
                / SHEAR_MODULUS
                * uniform_tail
                * y
            )
            maximum_displacement_difference = max(
                maximum_displacement_difference, abs(uy_tail)
            )
        evaluated_time_count += 1
        uniform_bound = sum(
            abs(math.sin(root) * math.cos(root) / denominator) * exponential
            for root, denominator, exponential in terms
        )
        pressure_bound = 2.0 * sum(
            abs(math.sin(root))
            * (1.0 + abs(math.cos(root)))
            / abs(denominator)
            * exponential
            for root, denominator, exponential in terms
        )
        spatial_bound = sum(
            abs(math.cos(root) / denominator) * exponential
            for root, denominator, exponential in terms
        )
        displacement_bound = max(
            LOAD
            / SHEAR_MODULUS
            * (undrained_poisson * uniform_bound + spatial_bound),
            LOAD
            * (1.0 - undrained_poisson)
            / SHEAR_MODULUS
            * HEIGHT
            * uniform_bound,
        )
        if (
            pressure_bound <= maximum_pressure_difference
            and displacement_bound <= maximum_displacement_difference
        ):
            break
    return {
        "retained_root_count": ROOT_COUNT,
        "reference_root_count": REFERENCE_ROOT_COUNT,
        "profile_point_count": PROFILE_POINT_COUNT,
        "reported_time_count": len(REPORTED_TIMES),
        "first_reported_time_seconds": REPORTED_TIMES[0],
        "last_reported_time_seconds": REPORTED_TIMES[-1],
        "directly_evaluated_time_count": evaluated_time_count,
        "remaining_times_certified_by_monotone_tail_bound": (
            len(REPORTED_TIMES) - evaluated_time_count
        ),
        "maximum_pressure_difference_over_pressure_scale": maximum_pressure_difference,
        "maximum_displacement_difference_m": maximum_displacement_difference,
    }


def time_sequence(step: float, end_time: float) -> str:
    count = math.floor(end_time / step)
    times = [index * step for index in range(count + 1)]
    if not math.isclose(times[-1], end_time, rel_tol=0.0, abs_tol=1.0e-12):
        times.append(end_time)
    return " ".join(f"{time:.12g}" for time in times)


def run_case(
    executable: Path,
    output_base: Path,
    mesh_nx: int,
    mesh_ny: int,
    step: float,
    end_time: float,
) -> tuple[list[dict[str, float]], str]:
    command = [
        str(executable),
        "-i",
        str(DECK),
        f"mesh_nx={mesh_nx}",
        f"mesh_ny={mesh_ny}",
        f"time_sequence={time_sequence(step, end_time)}",
        f"Executioner/end_time={end_time:.12g}",
        f"Outputs/file_base={output_base}",
        "--disable-perf-graph-live",
        "--color",
        "off",
    ]
    completed = subprocess.run(
        command,
        cwd=APP_DIR,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    log_path = Path(str(output_base) + ".log")
    log_path.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode or "*** ERROR ***" in completed.stdout:
        raise SystemExit(f"Mandel solve failed; see {log_path}")
    csv_path = Path(str(output_base) + ".csv")
    with csv_path.open(newline="", encoding="utf-8") as stream:
        rows = [
            {name: float(value) for name, value in row.items()}
            for row in csv.DictReader(stream)
        ]
    if not rows or not math.isclose(rows[-1]["time"], end_time, abs_tol=1.0e-12):
        raise SystemExit(f"Mandel solve did not reach t={end_time}; see {log_path}")
    recorded_command = list(command)
    for index, argument in enumerate(recorded_command):
        if index == 0:
            recorded_command[index] = str(executable.resolve().relative_to(ROOT))
        elif index > 0 and recorded_command[index - 1] == "-i":
            recorded_command[index] = str(DECK.relative_to(ROOT))
        elif argument.startswith("Outputs/file_base="):
            output_path = Path(argument.split("=", 1)[1]).resolve()
            try:
                output_text = str(output_path.relative_to(ROOT))
            except ValueError:
                output_text = "<temporary-output>/" + output_path.name
            recorded_command[index] = "Outputs/file_base=" + output_text
    return rows, shlex.join(recorded_command)


def evaluate(rows: list[dict[str, float]]) -> dict[str, object]:
    values = parameters()
    pressure_columns = ((0.0, "pressure_x0"), (0.3, "pressure_x03"), (0.8, "pressure_x08"))
    pressure_records = []
    displacement_records = []
    for row in rows:
        time = row["time"]
        exact_side = analytical_solution(time, 1.0)[1]
        exact_top = analytical_solution(time, 1.0)[2]
        displacement_records.append(
            {
                "time": time,
                "side_relative_error": abs(row["side_displacement"] - exact_side)
                / max(abs(exact_side), 1.0e-30),
                "top_relative_error": abs(row["top_displacement"] - exact_top)
                / max(abs(exact_top), 1.0e-30),
            }
        )
        for x, column in pressure_columns:
            exact_pressure = analytical_solution(time, x)[0]
            pressure_records.append(
                {
                    "time": time,
                    "x": x,
                    "computed": row[column],
                    "analytical": exact_pressure,
                    "normalized_error": abs(row[column] - exact_pressure)
                    / values["pressure_scale"],
                }
            )
    first_pressure = rows[0]["pressure_x0"]
    maximum_pressure = max(row["pressure_x0"] for row in rows)
    return {
        "maximum_pressure_normalized_error": max(
            record["normalized_error"] for record in pressure_records
        ),
        "maximum_side_displacement_relative_error": max(
            record["side_relative_error"] for record in displacement_records
        ),
        "maximum_top_displacement_relative_error": max(
            record["top_relative_error"] for record in displacement_records
        ),
        "maximum_load_relative_error": max(
            abs(row["vertical_nominal_stress"] + LOAD) / LOAD for row in rows
        ),
        "maximum_biot_reference_error": max(
            max(abs(row["biot_minimum"] - BIOT_COEFFICIENT),
                abs(row["biot_maximum"] - BIOT_COEFFICIENT))
            for row in rows
        ),
        "maximum_biot_identity_l2": max(row["biot_analytic_error_l2"] for row in rows),
        "maximum_biot_centered_difference_l2": max(
            row["biot_fixed_pressure_fd_error_l2"] for row in rows
        ),
        "maximum_referential_solid_mass_drift_l2": max(
            row["solid_material_mass_constraint_l2"] for row in rows
        ),
        "maximum_mineral_eos_residual_l2": max(
            row["solid_mineral_eos_constraint_l2"] for row in rows
        ),
        "mandel_cryer_pressure_increase": maximum_pressure / first_pressure - 1.0,
        "mandel_cryer_peak_time": rows[
            max(range(len(rows)), key=lambda index: rows[index]["pressure_x0"])
        ]["time"],
        "pressure_records": pressure_records,
        "displacement_records": displacement_records,
    }


def refinement_difference(
    coarse: list[dict[str, float]], fine: list[dict[str, float]]
) -> float:
    fine_by_time = {row["time"]: row for row in fine}
    scale = parameters()["pressure_scale"]
    differences = []
    for row in coarse:
        match = fine_by_time.get(row["time"])
        if match is None:
            continue
        for column in ("pressure_x0", "pressure_x03", "pressure_x08"):
            differences.append(abs(row[column] - match[column]) / scale)
    if not differences:
        raise SystemExit("coarse and fine Mandel histories have no common comparison times")
    return max(differences)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", type=Path, default=APP)
    parser.add_argument("--artifacts-dir", type=Path)
    parser.add_argument(
        "--quick",
        action="store_true",
        help="run the smoke horizon without claiming benchmark acceptance",
    )
    args = parser.parse_args()
    for path in (args.executable, DECK):
        if not path.is_file():
            raise SystemExit(f"required Mandel resource not found: {path}")

    temporary = None
    if args.artifacts_dir is None:
        temporary = tempfile.TemporaryDirectory(prefix="mandel_implicit_biot_")
        artifacts = Path(temporary.name)
    else:
        artifacts = args.artifacts_dir.resolve()
        artifacts.mkdir(parents=True, exist_ok=False)

    end_time = 0.014 if args.quick else 0.702
    coarse_step = 0.004 if not args.quick else 0.002
    fine_step = 0.002
    finer_step = 0.001
    spatial_coarse, spatial_coarse_command = run_case(
        args.executable.resolve(), artifacts / "spatial_coarse", 20, 2, fine_step, end_time
    )
    temporal_coarse, temporal_coarse_command = run_case(
        args.executable.resolve(), artifacts / "temporal_coarse", 40, 4, coarse_step, end_time
    )
    fine, fine_command = run_case(
        args.executable.resolve(), artifacts / "fine", 40, 4, fine_step, end_time
    )
    if args.quick:
        finer = None
        finer_command = None
    else:
        finer, finer_command = run_case(
            args.executable.resolve(), artifacts / "finer", 40, 4, finer_step, end_time
        )
    fine_metrics = evaluate(fine)
    spatial_convergence = refinement_difference(spatial_coarse, fine)
    temporal_convergence = refinement_difference(temporal_coarse, fine)
    finer_temporal_convergence = (
        None if finer is None else refinement_difference(fine, finer)
    )
    truncation = root_truncation_audit()

    gates = {
        "analytical_pressure": fine_metrics["maximum_pressure_normalized_error"]
        <= PRESSURE_ERROR_LIMIT,
        "analytical_side_displacement": fine_metrics[
            "maximum_side_displacement_relative_error"
        ]
        <= DISPLACEMENT_ERROR_LIMIT,
        "analytical_top_displacement_input": fine_metrics[
            "maximum_top_displacement_relative_error"
        ] <= 2.0e-3,
        "applied_load": fine_metrics["maximum_load_relative_error"] <= LOAD_ERROR_LIMIT,
        "implicit_biot_reference": fine_metrics["maximum_biot_reference_error"]
        <= BIOT_REFERENCE_LIMIT,
        "implicit_biot_identity": fine_metrics["maximum_biot_identity_l2"]
        <= BIOT_IDENTITY_LIMIT,
        "implicit_biot_centered_difference": fine_metrics[
            "maximum_biot_centered_difference_l2"
        ]
        <= BIOT_CENTERED_DIFFERENCE_LIMIT,
        "referential_solid_mass_drift": fine_metrics[
            "maximum_referential_solid_mass_drift_l2"
        ]
        <= CONSTRAINT_LIMIT,
        "mineral_eos_residual": fine_metrics["maximum_mineral_eos_residual_l2"]
        <= CONSTRAINT_LIMIT,
        "mandel_cryer_effect": fine_metrics["mandel_cryer_pressure_increase"] >= 1.0e-2,
        "spatial_refinement": spatial_convergence
        <= SPATIAL_REFINEMENT_DIFFERENCE_LIMIT,
        "temporal_refinement": temporal_convergence
        <= TEMPORAL_REFINEMENT_DIFFERENCE_LIMIT,
        "analytical_root_truncation_pressure": truncation[
            "maximum_pressure_difference_over_pressure_scale"
        ]
        <= ROOT_TRUNCATION_PRESSURE_DIFFERENCE_LIMIT,
        "analytical_root_truncation_displacement": truncation[
            "maximum_displacement_difference_m"
        ]
        <= ROOT_TRUNCATION_DISPLACEMENT_DIFFERENCE_LIMIT,
    }
    if finer_temporal_convergence is not None:
        gates["finer_temporal_refinement"] = (
            finer_temporal_convergence <= FINER_TEMPORAL_REFINEMENT_DIFFERENCE_LIMIT
        )
        gates["temporal_refinement_reduction"] = (
            finer_temporal_convergence < temporal_convergence
        )
    accepted = not args.quick and all(gates.values())
    summary = {
        "benchmark": "water-filled plane-strain Mandel consolidation",
        "discretization": {
            "displacement": "Q2 continuous Lagrange",
            "pressure": "Q1 continuous Lagrange",
            "pressure_enrichment": False,
            "spatial_coarse": {"nx": 20, "ny": 2, "dt": fine_step},
            "temporal_coarse": {"nx": 40, "ny": 4, "dt": coarse_step},
            "fine": {"nx": 40, "ny": 4, "dt": fine_step},
            "finer": None if args.quick else {"nx": 40, "ny": 4, "dt": finer_step},
        },
        "analytical_parameters": parameters(),
        "limits": {
            "pressure_error": PRESSURE_ERROR_LIMIT,
            "side_displacement_error": DISPLACEMENT_ERROR_LIMIT,
            "load_error": LOAD_ERROR_LIMIT,
            "biot_reference_error": BIOT_REFERENCE_LIMIT,
            "biot_identity_l2": BIOT_IDENTITY_LIMIT,
            "biot_centered_difference_l2": BIOT_CENTERED_DIFFERENCE_LIMIT,
            "constraint_l2": CONSTRAINT_LIMIT,
            "spatial_refinement_difference": SPATIAL_REFINEMENT_DIFFERENCE_LIMIT,
            "temporal_refinement_difference": TEMPORAL_REFINEMENT_DIFFERENCE_LIMIT,
            "finer_temporal_refinement_difference": FINER_TEMPORAL_REFINEMENT_DIFFERENCE_LIMIT,
            "root_truncation_pressure_difference": ROOT_TRUNCATION_PRESSURE_DIFFERENCE_LIMIT,
            "root_truncation_displacement_difference_m": ROOT_TRUNCATION_DISPLACEMENT_DIFFERENCE_LIMIT,
        },
        "metrics": fine_metrics,
        "maximum_spatial_refinement_pressure_difference": spatial_convergence,
        "maximum_temporal_refinement_pressure_difference": temporal_convergence,
        "maximum_finer_temporal_refinement_pressure_difference": finer_temporal_convergence,
        "analytical_root_truncation": truncation,
        "gates": gates,
        "quick_mode": args.quick,
        "accepted": accepted,
        "provenance": {
            "deck": str(DECK.relative_to(ROOT)),
            "deck_sha256": sha256(DECK),
            "executable": str(args.executable.resolve().relative_to(ROOT)),
            "executable_sha256": sha256(args.executable),
            "verifier": str(Path(__file__).resolve().relative_to(ROOT)),
            "verifier_sha256": sha256(Path(__file__).resolve()),
            "spatial_coarse_command": spatial_coarse_command,
            "temporal_coarse_command": temporal_coarse_command,
            "fine_command": fine_command,
            "finer_command": finer_command,
        },
    }
    (artifacts / "verification_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "mandel_implicit_biot: "
        f"pressure_error={fine_metrics['maximum_pressure_normalized_error']:.6e}, "
        f"side_displacement_error={fine_metrics['maximum_side_displacement_relative_error']:.6e}, "
        f"spatial_refinement_difference={spatial_convergence:.6e}, "
        f"temporal_refinement_difference={temporal_convergence:.6e}, "
        f"finer_temporal_refinement_difference={finer_temporal_convergence if finer_temporal_convergence is not None else float('nan'):.6e}, "
        f"root_truncation_pressure_difference={truncation['maximum_pressure_difference_over_pressure_scale']:.6e}, "
        f"biot_identity_l2={fine_metrics['maximum_biot_identity_l2']:.6e}, "
        f"biot_centered_difference_l2={fine_metrics['maximum_biot_centered_difference_l2']:.6e}, "
        f"accepted={accepted}"
    )
    if args.quick:
        return 0 if all(gates.values()) else 1
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
