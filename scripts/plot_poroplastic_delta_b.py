#!/usr/bin/env python3
"""Plot the poroplastic Delta-B vs compression curve (single-element, drained,
prescribed uniaxial-strain compression; ideal Drucker-Prager, M=0.6, beta=0.4).

Reads validation/poroplastic_delta_b.csv and writes figures/poroplastic_delta_b.png.
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
# Match the repository's manuscript-figure PGF conventions (see
# plot_mandel_extended_results.py): rcfonts=False lets the \input'ed pgf inherit
# the document fonts (lmodern), and lualatex is the installed TeX engine.
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
csv_path = os.path.join(ROOT, "validation", "poroplastic_delta_b.csv")
png_path = os.path.join(ROOT, "figures", "poroplastic_delta_b.png")

rows = []
with open(csv_path, newline="") as fh:
    for r in csv.DictReader(fh):
        v = {k: float(val) for k, val in r.items()}
        rows.append(v)

comp = [r["compression"] for r in rows]
b_el = [r["B_el"] for r in rows]
b_pl = [r["B_pl"] for r in rows]
db = [r["delta_B"] for r in rows]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.4, 3.0))
ax1.plot(comp, b_el, "-o", color="tab:gray", label=r"$B_{\mathrm{el}}$ (elastic)")
ax1.plot(comp, b_pl, "-s", color="tab:red", label=r"$B_{\mathrm{pl}}$ (poroplastic)")
ax1.axhline(0.6, color="black", lw=0.8, ls=":", label=r"$B_0$ (small-strain limit)")
ax1.set_xlabel("Axial compression  $1-\\lambda_a$")
ax1.set_ylabel("Biot coefficient  $B$")
ax1.set_title("Biot coefficient under compression")
ax1.legend()
ax1.grid(alpha=0.3)

ax2.plot(comp, db, "-^", color="tab:blue")
ax2.set_xlabel("Axial compression  $1-\\lambda_a$")
ax2.set_ylabel(r"$\Delta B = B_{\mathrm{pl}} - B_{\mathrm{el}}$")
ax2.set_title("Plastic history contribution to $B$")
ax2.grid(alpha=0.3)

fig.tight_layout()
fig.savefig(png_path, dpi=200)
print("wrote", png_path)

# Manuscript-convention .pgf (matplotlib PGF backend), consumed with \input{...}.
from matplotlib.backends.backend_pgf import FigureCanvasPgf  # noqa: E402

pgf_path = os.path.join(ROOT, "figures", "poroplastic_delta_b.pgf")
FigureCanvasPgf(fig).print_pgf(pgf_path)
print("wrote", pgf_path)

# Publish the same image used by the repository figure set.
import shutil
shutil.copyfile(png_path, os.path.join(ROOT, "docs/assets/img", os.path.basename(png_path)))
