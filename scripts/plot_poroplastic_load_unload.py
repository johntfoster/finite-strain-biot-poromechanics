#!/usr/bin/env python3
"""Plot the V3 load-unload branch coefficients.

Reads validation/poroplastic_load_unload.csv (curated by
validation/scripts/check_poroplastic_load_unload.py) and writes
figures/poroplastic_load_unload.png and .pgf.

After monotonic plastic (dilative) loading to a peak compression the plastic
pore allocation a^p is frozen, so the coefficient on the unloading branch is
the fixed-history, fixed-pressure tangent (the unload/reload reading of alpha
in the literature).  The figure shows the virgin elastic coefficient B_el
(dashed), the monotonic-loading coefficient (solid, a^p = a^p(compression)),
and the unload-branch coefficient (markers, a^p frozen at the peak): the
unload coefficient lies above both the elastic and the monotonic-loading
values at the same compression.
"""

import csv
import os

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams.update(
    {
        "pgf.texsystem": "lualatex",
        "pgf.rcfonts": False,
        "font.family": "serif",
        "font.size": 9.0,
        "axes.labelsize": 9.0,
        "axes.titlesize": 9.0,
        "xtick.labelsize": 8.0,
        "ytick.labelsize": 8.0,
        "legend.fontsize": 8.0,
    }
)
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(ROOT, "validation", "poroplastic_load_unload.csv")

mono = []
unload = []
with open(csv_path, newline="") as fh:
    for r in csv.DictReader(fh):
        branch = r["branch"]
        row = {"branch": branch}
        for k, v in r.items():
            if k != "branch":
                row[k] = float(v)
        (mono if row["branch"] == "monotonic" else unload).append(row)
mono.sort(key=lambda r: r["compression"])
unload.sort(key=lambda r: r["compression"])

fig, ax = plt.subplots(figsize=(4.6, 3.2))
x_el = [r["compression"] for r in mono]
ax.plot(x_el, [r["B_el"] for r in mono], "--", color="tab:gray", lw=1.6,
        label=r"$B_{\mathrm{el}}$ (virgin elastic)")
ax.plot(x_el, [r["B"] for r in mono], "-", color="tab:blue", lw=1.8,
        label=r"monotonic loading  $B=1-(1-B_{\mathrm{el}})/a^p$")
ax.plot([r["compression"] for r in unload], [r["B"] for r in unload],
        "-o", color="tab:red", lw=1.5, ms=4,
        label=r"unload branch ($a^p$ frozen at peak)")
ax.annotate("load", xy=(0.10, 0.489), xytext=(0.065, 0.41),
            arrowprops=dict(arrowstyle="->", lw=0.9),
            fontsize=8, color="tab:blue")
ax.annotate("unload", xy=(0.10, 0.505), xytext=(0.125, 0.545),
            arrowprops=dict(arrowstyle="->", lw=0.9),
            fontsize=8, color="tab:red")
ax.set_xlabel("Axial compression  $1-\\lambda_a$")
ax.set_ylabel("Biot coefficient  $B$")
ax.set_title("Unload-loop coefficient (frozen plastic history)")
ax.grid(alpha=0.3)
ax.legend(loc="lower left", framealpha=0.9)

fig.tight_layout()
png_path = os.path.join(ROOT, "figures", "poroplastic_load_unload.png")
fig.savefig(png_path, dpi=200)
print("wrote", png_path)

from matplotlib.backends.backend_pgf import FigureCanvasPgf  # noqa: E402

pgf_path = os.path.join(ROOT, "figures", "poroplastic_load_unload.pgf")
FigureCanvasPgf(fig).print_pgf(pgf_path)
print("wrote", pgf_path)
