#!/usr/bin/env python3
"""Plot the published Figure 3c points and implicit-AD MOOSE pressure paths."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
COLORS = {"HT14": "black", "SP14": "#0072B2", "SP30": "#D55E00"}
MARKERS = {"HT14": "o", "SP14": "s", "SP30": "^"}


def main() -> int:
    observed = pd.read_csv(ROOT / "data/processed/lawal_kim_figure3c.csv")
    predicted = pd.read_csv(ROOT / "data/processed/moose_pressure_path_predictions.csv")
    fig, axis = plt.subplots(figsize=(6.5, 4.3))
    for sample in ("HT14", "SP14", "SP30"):
        data = observed[observed["sample"] == sample]
        curve = predicted[predicted["sample"] == sample]
        axis.scatter(
            data["pressure_mpa"],
            data["biot_coefficient_reported"],
            facecolors="white",
            edgecolors=COLORS[sample],
            marker=MARKERS[sample],
            linewidths=1.5,
            label=f"{sample}, Lawal--Kim",
            zorder=3,
        )
        axis.plot(
            curve["pressure_mpa"],
            curve["biot_coefficient_out"],
            color=COLORS[sample],
            linewidth=1.8,
            label=f"{sample}, implicit AD",
        )
    axis.set_xlabel("Pressure [MPa]")
    axis.set_ylabel("Biot coefficient $B$ [-]")
    axis.set_xlim(0.0, 42.0)
    axis.set_ylim(0.3, 1.0)
    axis.grid(alpha=0.2)
    axis.legend(ncol=2, fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(ROOT / "figures/moose_lawal_kim_biot_replication.pdf")
    fig.savefig(ROOT / "figures/moose_lawal_kim_biot_replication.png", dpi=300)
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

