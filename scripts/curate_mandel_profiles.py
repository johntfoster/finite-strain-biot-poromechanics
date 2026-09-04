#!/usr/bin/env python3
"""Curate publication profile CSV files from MOOSE line-sampler output."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_TIMES = (0.014, 0.046, 0.094, 0.206, 0.398)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def sampler_path(file_base: Path, sampler: str, index: int) -> Path:
    return Path(f"{file_base}_{sampler}_{index:04d}.csv")


def sample_indices(file_base: Path) -> dict[float, int]:
    history = read_rows(Path(f"{file_base}.csv"))
    indices: dict[float, int] = {}
    for selected_time in SAMPLE_TIMES:
        for index, row in enumerate(history, start=1):
            if math.isclose(float(row["time"]), selected_time, abs_tol=1.0e-12):
                indices[selected_time] = index
                break
        else:
            raise ValueError(f"profile history does not contain t={selected_time:g}")
    return indices


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file_base", type=Path)
    parser.add_argument(
        "--pressure-output",
        type=Path,
        default=ROOT / "validation/mandel_pressure_profiles.csv",
    )
    parser.add_argument(
        "--displacement-output",
        type=Path,
        default=ROOT / "validation/mandel_displacement_profiles.csv",
    )
    parser.add_argument("--large-source", type=Path)
    parser.add_argument(
        "--large-output",
        type=Path,
        default=ROOT / "validation/mandel_large_deformation.csv",
    )
    args = parser.parse_args()

    pressure_rows: list[dict[str, float]] = []
    displacement_rows: list[dict[str, float | str]] = []
    for time, index in sample_indices(args.file_base).items():
        for row in read_rows(sampler_path(args.file_base, "pressure_profile", index)):
            pressure_rows.append(
                {
                    "time": time,
                    "x": float(row["x"]),
                    "y": float(row["y"]),
                    "pressure": float(row["p"]),
                }
            )
        for component, coordinate, value in (
            ("ux", "x", "ux"),
            ("uy", "y", "uy"),
        ):
            for row in read_rows(sampler_path(args.file_base, f"{component}_profile", index)):
                displacement_rows.append(
                    {
                        "time": time,
                        "component": component,
                        "coordinate": float(row[coordinate]),
                        "displacement": float(row[value]),
                    }
                )

    args.pressure_output.parent.mkdir(parents=True, exist_ok=True)
    with args.pressure_output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("time", "x", "y", "pressure"))
        writer.writeheader()
        writer.writerows(pressure_rows)
    with args.displacement_output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=("time", "component", "coordinate", "displacement"),
        )
        writer.writeheader()
        writer.writerows(displacement_rows)

    if args.large_source is not None:
        fieldnames = (
            "time",
            "biot_minimum",
            "biot_average",
            "biot_maximum",
            "side_displacement",
            "top_displacement",
            "pressure_x0",
            "vertical_nominal_stress",
            "solid_material_mass_constraint_l2",
            "solid_mineral_eos_constraint_l2",
            "biot_analytic_error_l2",
        )
        source_rows = read_rows(args.large_source)
        with args.large_output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(
                {name: row[name] for name in fieldnames} for row in source_rows
            )

    print(args.pressure_output.relative_to(ROOT))
    print(args.displacement_output.relative_to(ROOT))
    if args.large_source is not None:
        print(args.large_output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
