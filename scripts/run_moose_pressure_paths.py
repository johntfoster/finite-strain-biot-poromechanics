#!/usr/bin/env python3
"""Run the implicit-AD MOOSE pressure path for all three Lawal--Kim samples."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--app",
        type=Path,
        default=Path(
            "/home/jfoster/projects/research/reactive_transport/"
            "multicomponent_reactive_flow/moose_app/multicomponent_reactive_flow-opt"
        ),
    )
    args = parser.parse_args()
    repo = args.repo.resolve()
    parameters = json.loads((repo / "data/processed/crack_closure_fit.json").read_text())
    observations = pd.read_csv(repo / "data/processed/lawal_kim_figure3c.csv")
    build = repo / "build/moose_pressure_paths"
    build.mkdir(parents=True, exist_ok=True)
    curves: list[pd.DataFrame] = []
    metrics: dict[str, dict[str, float]] = {}

    for sample, values in parameters.items():
        file_base = build / sample.lower()
        command = [
            str(args.app),
            "-i",
            str(repo / "moose/input/pressure_path_biot.i"),
            f"k_infinity_gpa:={values['k_infinity_gpa']:.17g}",
            f"crack_compliance_per_gpa:={values['crack_compliance_per_gpa']:.17g}",
            f"closure_pressure_gpa:={values['closure_pressure_mpa']/1000.0:.17g}",
            f"unjacketed_bulk_modulus_gpa:={values['unjacketed_bulk_modulus_gpa']:.17g}",
            f"Outputs/file_base={file_base}",
            "--allow-test-objects",
        ]
        completed = subprocess.run(
            command,
            cwd=repo,
            env=os.environ,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if completed.returncode:
            raise SystemExit(f"{sample} MOOSE run failed:\n{completed.stdout}")

        files = sorted(build.glob(f"{sample.lower()}_pressure_path_*.csv"))
        if len(files) != 1:
            raise SystemExit(f"{sample}: expected one pressure-path CSV, found {files}")
        curve = pd.read_csv(files[0]).sort_values("mean_effective_pressure_state")
        curve["sample"] = sample
        curve["pressure_mpa"] = 1000.0 * curve["mean_effective_pressure_state"]

        pressure_gpa = curve["mean_effective_pressure_state"].to_numpy(float)
        k_inf = values["k_infinity_gpa"]
        compliance = values["crack_compliance_per_gpa"]
        p_close = values["closure_pressure_mpa"] / 1000.0
        k_s = values["unjacketed_bulk_modulus_gpa"]
        integral = pressure_gpa / k_inf + compliance * p_close * (
            1.0 - np.exp(-pressure_gpa / p_close)
        )
        jacobian = np.exp(-integral)
        intrinsic_volume = np.exp(-pressure_gpa / k_s)
        analytic_biot = 1.0 - (
            intrinsic_volume
            / jacobian
            * curve["drained_bulk_modulus_out"].to_numpy(float)
            / k_s
        )
        tangent_error = curve["biot_coefficient_out"].to_numpy(float) - analytic_biot
        maximum_tangent_error = float(np.abs(tangent_error).max())
        maximum_constraint = float(np.abs(curve["constraint_norm_out"]).max())
        if maximum_tangent_error > 2.0e-6:
            raise SystemExit(f"{sample}: implicit tangent error={maximum_tangent_error:.3e}")
        if maximum_constraint > 2.0e-8:
            raise SystemExit(f"{sample}: constraint norm={maximum_constraint:.3e}")

        observed = observations[observations["sample"] == sample]
        predicted = np.interp(
            observed["pressure_mpa"], curve["pressure_mpa"], curve["biot_coefficient_out"]
        )
        error = predicted - observed["biot_coefficient_reported"].to_numpy(float)
        metrics[sample] = {
            "number_of_points": int(len(observed)),
            "biot_rmse": float(np.sqrt(np.mean(error**2))),
            "biot_max_abs_error": float(np.abs(error).max()),
            "biot_bias": float(error.mean()),
            "maximum_implicit_tangent_error": maximum_tangent_error,
            "maximum_constraint_norm": maximum_constraint,
        }
        curves.append(
            curve[
                [
                    "sample",
                    "pressure_mpa",
                    "drained_bulk_modulus_out",
                    "biot_coefficient_out",
                    "biot_classical_out",
                    "constraint_norm_out",
                ]
            ]
        )

    pd.concat(curves, ignore_index=True).to_csv(
        repo / "data/processed/moose_pressure_path_predictions.csv", index=False
    )
    (repo / "validation/moose_pressure_path_metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n"
    )
    for sample, values in metrics.items():
        print(
            f"{sample}: RMSE={values['biot_rmse']:.4e}, "
            f"max={values['biot_max_abs_error']:.4e}, "
            f"tangent={values['maximum_implicit_tangent_error']:.3e}, "
            f"constraint={values['maximum_constraint_norm']:.3e}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

