#!/usr/bin/env python3
"""Quantitative integrity checks for the extracted Lawal--Kim Figure 3c data."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


EXPECTED_COUNTS = {"HT14": 16, "SP14": 15, "SP30": 15}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    args = parser.parse_args()
    data = pd.read_csv(args.csv)

    counts = data.groupby("sample").size().to_dict()
    if counts != EXPECTED_COUNTS:
        raise SystemExit(f"unexpected series counts: {counts}")

    maximum_formula_error = float(np.abs(data["recompute_error"]).max())
    if maximum_formula_error > 5.0e-15:
        raise SystemExit(f"alpha != 1-K/K_s': max error={maximum_formula_error:.3e}")

    for sample, group in data.groupby("sample"):
        pressure = group["pressure_mpa"].to_numpy()
        if np.any(np.diff(pressure) <= 0.0):
            raise SystemExit(f"{sample}: pressure is not strictly increasing")
        first = float(group["biot_coefficient_reported"].iloc[0])
        last = float(group["biot_coefficient_reported"].iloc[-1])
        if not last < first:
            raise SystemExit(f"{sample}: Biot coefficient does not decrease overall")

    print(
        "PASS Lawal--Kim Figure 3c extraction: "
        f"{len(data)} points, max |alpha-(1-K/K_s')|={maximum_formula_error:.3e}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

