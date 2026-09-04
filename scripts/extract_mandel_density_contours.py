#!/usr/bin/env python3
"""Extract the solved Mandel intrinsic-solid density ratio at element centers."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

from netCDF4 import Dataset


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TIMES = (0.0, 0.046, 0.094, 0.206, 0.398, 0.702)
REFERENCE_SOLID_VOLUME_FRACTION = 0.9
SKELETON_TO_MINERAL_BULK_MODULUS_RATIO = 0.4


def decode_names(values) -> list[str]:
    return [row.tobytes().decode(errors="ignore").strip("\x00 ") for row in values]


def find_time_index(times, selected_time: float) -> int:
    for index, time in enumerate(times):
        if math.isclose(float(time), selected_time, rel_tol=0.0, abs_tol=1.0e-10):
            return index
    available = ", ".join(f"{float(time):g}" for time in times)
    raise ValueError(f"time {selected_time:g} is absent; available times: {available}")


def extract_rows(
    exodus: Path, selected_times: tuple[float, ...]
) -> tuple[list[dict[str, float]], list[dict[str, float]]]:
    density_rows: list[dict[str, float]] = []
    biot_rows: list[dict[str, float]] = []
    with Dataset(exodus) as dataset:
        names = decode_names(dataset.variables["name_elem_var"][:])
        density_matches = [
            index
            for index, name in enumerate(names, start=1)
            if name.startswith("solid_intrinsic_density_ratio")
        ]
        volume_fraction_matches = [
            index
            for index, name in enumerate(names, start=1)
            if name == "solid_volume_fraction_state"
        ]
        if len(density_matches) != 1 or len(volume_fraction_matches) != 1:
            raise ValueError(
                "expected one elemental intrinsic-density and volume-fraction variable; "
                f"found density={density_matches}, volume_fraction={volume_fraction_matches} "
                f"in {names}"
            )
        density_values = dataset.variables[f"vals_elem_var{density_matches[0]}eb1"]
        volume_fraction_values = dataset.variables[
            f"vals_elem_var{volume_fraction_matches[0]}eb1"
        ]
        times = dataset.variables["time_whole"][:]
        x_coordinates = dataset.variables["coordx"][:]
        y_coordinates = dataset.variables["coordy"][:]
        connectivity = dataset.variables["connect1"][:]

        centers = []
        for element_index, element_nodes in enumerate(connectivity):
            center_node = int(element_nodes[-1]) - 1
            centers.append(
                (
                    element_index,
                    float(x_coordinates[center_node]),
                    float(y_coordinates[center_node]),
                )
            )
        centers.sort(key=lambda item: (item[2], item[1]))

        for selected_time in selected_times:
            if math.isclose(selected_time, 0.0, rel_tol=0.0, abs_tol=1.0e-14):
                for _, x_coordinate, y_coordinate in centers:
                    density_rows.append(
                        {
                            "time": 0.0,
                            "X": x_coordinate,
                            "Y": y_coordinate,
                            "intrinsic_solid_density_ratio": 1.0,
                        }
                    )
                    biot_rows.append(
                        {
                            "time": 0.0,
                            "X": x_coordinate,
                            "Y": y_coordinate,
                            "biot_coefficient": 0.6,
                        }
                    )
                continue
            time_index = find_time_index(times, selected_time)
            for element_index, x_coordinate, y_coordinate in centers:
                density_ratio = float(density_values[time_index, element_index])
                solid_volume_fraction = float(
                    volume_fraction_values[time_index, element_index]
                )
                jacobian = REFERENCE_SOLID_VOLUME_FRACTION / (
                    solid_volume_fraction * density_ratio
                )
                biot_coefficient = 1.0 - (
                    SKELETON_TO_MINERAL_BULK_MODULUS_RATIO
                    * (1.0 - math.log(jacobian))
                    / (density_ratio * jacobian**2)
                )
                density_rows.append(
                    {
                        "time": selected_time,
                        "X": x_coordinate,
                        "Y": y_coordinate,
                        "intrinsic_solid_density_ratio": density_ratio,
                    }
                )
                biot_rows.append(
                    {
                        "time": selected_time,
                        "X": x_coordinate,
                        "Y": y_coordinate,
                        "biot_coefficient": biot_coefficient,
                    }
                )
    return density_rows, biot_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exodus", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "validation/mandel_density_contours.csv",
    )
    parser.add_argument(
        "--biot-output",
        type=Path,
        default=ROOT / "validation/mandel_biot_contours.csv",
    )
    parser.add_argument(
        "--times",
        default=",".join(f"{time:g}" for time in DEFAULT_TIMES),
    )
    args = parser.parse_args()

    selected_times = tuple(float(value) for value in args.times.split(","))
    rows, biot_rows = extract_rows(args.exodus, selected_times)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with args.biot_output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(biot_rows[0]))
        writer.writeheader()
        writer.writerows(biot_rows)

    values = [row["intrinsic_solid_density_ratio"] for row in rows]
    print(args.output)
    print(args.biot_output)
    print(f"intrinsic solid density ratio range: [{min(values):.9f}, {max(values):.9f}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
