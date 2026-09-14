#!/usr/bin/env python3
"""Plot the canonical implicit-coefficient feedback at nonzero pore pressure.

Reads validation/poroplastic_b_feedback.csv (curated by
validation/scripts/check_poroplastic_b_feedback.py from the stateful tensorial
engine at M = 0.6, beta = 0.4) and writes figures/poroplastic_b_feedback.png
and .pgf.

Two panels: the left is the pore-pressure scan at 20% axial compression, the
right the axial-compression scan at 200 MPa pore pressure.  In each panel the
left axis gives the pore-allocation-corrected coefficient
B = 1 - K*Jbar/(J*(Ks + (1-K/(phi0*Ks))*p*Jbar)) (solid) and the elastic coefficient B_el (dashed); the
right (secondary) axis gives the percent by which the frozen-elastic (B = B_el)
reference over-predicts the plastic increment Delta_gamma (markers).  Because
both panels show the same quantities, a single shared legend is drawn above
the panels rather than a legend in each panel.
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
csv_path = os.path.join(ROOT, "validation", "poroplastic_b_feedback.csv")
png_path = os.path.join(ROOT, "figures", "poroplastic_b_feedback.png")
pgf_path = os.path.join(ROOT, "figures", "poroplastic_b_feedback.pgf")

rows = []
with open(csv_path, newline="") as fh:
    for r in csv.DictReader(fh):
        rows.append({k: float(v) for k, v in r.items()})

# De-duplicate (compression, pore_pressure) keeping first occurrence.
seen = set()
uniq = []
for r in rows:
    key = (round(r["compression"], 4), round(r["pore_pressure"], 6))
    if key not in seen:
        seen.add(key)
        uniq.append(r)
rows = uniq

p_scan = sorted([r for r in rows if abs(r["compression"] - 0.20) < 1e-9],
                key=lambda r: r["pore_pressure"])
c_scan = sorted([r for r in rows if abs(r["pore_pressure"] - 2.0e8) < 1e6],
                key=lambda r: r["compression"])

fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(8.0, 3.6))


def panel(ax, data, xkey, xlabel):
    x = [r[xkey] / (1e6 if xkey == "pore_pressure" else 1) for r in data]
    ax.plot(x, [r["B_coupled"] for r in data], "-", color="tab:red",
            label=r"$B$ (current plastic state)")
    ax.plot(x, [r["B_el"] for r in data], "--", color="tab:gray",
            label=r"$B_{\mathrm{el}}$")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Biot coefficient  $B$")
    ax.grid(alpha=0.3)
    axr = ax.twinx()
    axr.plot(x, [r["over_prediction_pct"] for r in data], "s",
             color="tab:blue", ms=3.5,
             label="frozen-elastic over-prediction")
    axr.set_ylabel(r"over-prediction of $\Delta\gamma$ (%)")
    return ax, axr


ax_l, ax_lr = panel(ax_l, p_scan, "pore_pressure", "Final pore pressure (MPa)")
_, ax_rr = panel(ax_r, c_scan, "compression", "Axial compression  $1-\\lambda_a$")

# Single shared legend above the panels (identical entries in both panels).
handles = [ax_l.get_lines()[0], ax_l.get_lines()[1], ax_lr.get_lines()[0]]
labels = [ln.get_label() for ln in handles]
fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.98),
           ncol=3, framealpha=0.9)
fig.subplots_adjust(top=0.78, bottom=0.14, left=0.10, right=0.90,
                    wspace=0.85)

fig.savefig(png_path, dpi=200)
print("wrote", png_path)

from matplotlib.backends.backend_pgf import FigureCanvasPgf  # noqa: E402

FigureCanvasPgf(fig).print_pgf(pgf_path)
print("wrote", pgf_path)

# Publish the same image used by the repository figure set.
import shutil
shutil.copyfile(png_path, os.path.join(ROOT, "docs/assets/img", os.path.basename(png_path)))
