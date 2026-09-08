#!/usr/bin/env python3
"""Plot the canonical stateful tensorial load-unload-reload loop.

Reads validation/tensorial_load_unload.csv (curated by
validation/scripts/check_tensorial_load_unload.py) and writes
figures/tensorial_load_unload.png and .pgf.

The stateful multiplicative ideal Drucker-Prager return mapping stores F^p and
a^p; the elastic trial is formed on F^e = F (F^p_n)^-1, so unloading inside the
yield surface is immediately elastic (a^p frozen, Delta_gamma = 0) and
reloading re-yields at the stored peak.  Left axis: plastic pore allocation
a^p; right axis: the coefficient B.  Shaded bands mark the load, elastic-unload,
and reload stages.
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
        "legend.fontsize": 7.5,
    }
)
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(ROOT, "validation", "tensorial_load_unload.csv")

rows = []
with open(csv_path, newline="") as fh:
    for r in csv.DictReader(fh):
        rows.append({k: float(v) for k, v in r.items()})
rows.sort(key=lambda r: r["time"])

t = [r["time"] for r in rows]
ap = [r["a_p"] for r in rows]
b = [r["B"] for r in rows]

fig, ax1 = plt.subplots(figsize=(5.4, 3.2))
ax1.axvspan(0, 1, color="tab:blue", alpha=0.08)
ax1.axvspan(1, 2, color="tab:red", alpha=0.08)
ax1.axvspan(2, 3, color="tab:blue", alpha=0.08)
ax1.plot(t, ap, "-", color="tab:blue", lw=1.8, label=r"$a^p$ (plastic allocation)")
ax1.set_xlabel("Time  (load $\\to$ unload $\\to$ reload)")
ax1.set_ylabel(r"Plastic pore allocation  $a^p$")
ax1.set_ylim(1.0, 1.045)
ax1.grid(alpha=0.3)

ax2 = ax1.twinx()
ax2.plot(t, b, "-", color="tab:red", lw=1.6, label=r"$B$")
ax2.set_ylabel("Biot coefficient  $B$")

ax1.annotate("load", xy=(0.5, 1.031), fontsize=8, color="tab:blue", ha="center")
ax1.annotate("unload\n(elastic, $a^p$ frozen)", xy=(1.5, 1.003), fontsize=7.5,
             color="tab:red", ha="center")
ax1.annotate("reload", xy=(2.5, 1.031), fontsize=8, color="tab:blue", ha="center")

lines = ax1.get_lines() + ax2.get_lines()
ax1.legend(lines, [ln.get_label() for ln in lines], loc="upper left", framealpha=0.9)
fig.tight_layout()

png_path = os.path.join(ROOT, "figures", "tensorial_load_unload.png")
fig.savefig(png_path, dpi=200)
print("wrote", png_path)

from matplotlib.backends.backend_pgf import FigureCanvasPgf  # noqa: E402

pgf_path = os.path.join(ROOT, "figures", "tensorial_load_unload.pgf")
FigureCanvasPgf(fig).print_pgf(pgf_path)
print("wrote", pgf_path)
