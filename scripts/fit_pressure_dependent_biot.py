#!/usr/bin/env python3
"""Fit a positive crack-closure compliance law and plot Biot predictions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import least_squares


COLORS = {"HT14": "black", "SP14": "#0072B2", "SP30": "#D55E00"}
MARKERS = {"HT14": "o", "SP14": "s", "SP30": "^"}


def modulus(pressure: np.ndarray, k_infinity: float, crack_compliance: float,
            closure_pressure: float) -> np.ndarray:
    return 1.0 / (1.0 / k_infinity + crack_compliance * np.exp(-pressure / closure_pressure))


def fit_sample(group: pd.DataFrame) -> dict[str, float]:
    pressure = group["pressure_mpa"].to_numpy(float)
    measured = group["drained_bulk_modulus_gpa"].to_numpy(float)
    k_s = float(group["unjacketed_bulk_modulus_gpa"].iloc[0])

    def residual(log_parameters: np.ndarray) -> np.ndarray:
        k_inf, compliance, p_close = np.exp(log_parameters)
        return modulus(pressure, k_inf, compliance, p_close) - measured

    guess = np.log([min(0.95 * k_s, 1.15 * measured.max()), 1.0 / measured.min(), 10.0])
    solution = least_squares(residual, guess, max_nfev=50000)
    k_inf, compliance, p_close = np.exp(solution.x)
    predicted_k = modulus(pressure, k_inf, compliance, p_close)
    predicted_b = 1.0 - predicted_k / k_s
    observed_b = group["biot_coefficient_reported"].to_numpy(float)
    error = predicted_b - observed_b
    return {
        "k_infinity_gpa": float(k_inf),
        "crack_compliance_per_gpa": float(compliance),
        "closure_pressure_mpa": float(p_close),
        "unjacketed_bulk_modulus_gpa": k_s,
        "biot_rmse": float(np.sqrt(np.mean(error**2))),
        "biot_max_abs_error": float(np.abs(error).max()),
        "biot_bias": float(error.mean()),
        "modulus_rmse_gpa": float(np.sqrt(np.mean((predicted_k - measured) ** 2))),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("parameters", type=Path)
    parser.add_argument("predictions", type=Path)
    parser.add_argument("figure", type=Path)
    args = parser.parse_args()
    data = pd.read_csv(args.csv)
    fitted: dict[str, dict[str, float]] = {}
    predicted_records: list[dict[str, float | str]] = []

    fig, axis = plt.subplots(figsize=(6.5, 4.3))
    for sample, group in data.groupby("sample", sort=False):
        group = group.sort_values("pressure_mpa")
        parameters = fit_sample(group)
        fitted[sample] = parameters
        pressure = group["pressure_mpa"].to_numpy(float)
        dense_pressure = np.linspace(pressure.min(), pressure.max(), 300)
        dense_k = modulus(
            dense_pressure,
            parameters["k_infinity_gpa"],
            parameters["crack_compliance_per_gpa"],
            parameters["closure_pressure_mpa"],
        )
        dense_b = 1.0 - dense_k / parameters["unjacketed_bulk_modulus_gpa"]
        axis.scatter(
            pressure,
            group["biot_coefficient_reported"],
            facecolors="none",
            edgecolors=COLORS[sample],
            marker=MARKERS[sample],
            label=f"{sample} data",
        )
        axis.plot(dense_pressure, dense_b, color=COLORS[sample], label=f"{sample} fit")
        for p, k, b in zip(dense_pressure, dense_k, dense_b):
            predicted_records.append(
                {
                    "sample": sample,
                    "pressure_mpa": float(p),
                    "drained_bulk_modulus_gpa": float(k),
                    "biot_coefficient": float(b),
                }
            )

    axis.set_xlabel("Pressure [MPa]")
    axis.set_ylabel("Biot coefficient $B$ [-]")
    axis.set_xlim(0.0, 42.0)
    axis.set_ylim(0.3, 1.0)
    axis.grid(alpha=0.2)
    axis.legend(ncol=2, fontsize=8)
    fig.tight_layout()

    args.parameters.parent.mkdir(parents=True, exist_ok=True)
    args.parameters.write_text(json.dumps(fitted, indent=2) + "\n")
    pd.DataFrame(predicted_records).to_csv(args.predictions, index=False)
    args.figure.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.figure, dpi=300)
    plt.close(fig)

    for sample, values in fitted.items():
        print(
            f"{sample}: B_RMSE={values['biot_rmse']:.4e}, "
            f"B_max={values['biot_max_abs_error']:.4e}, "
            f"K_RMSE={values['modulus_rmse_gpa']:.4e} GPa"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

