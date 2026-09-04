#!/usr/bin/env python3
"""Plot the poroplastic Delta-B vs compression curve (single-element, drained,
prescribed uniaxial-strain compression; ideal Drucker-Prager, M=0.2, beta=0.4).

Reads validation/poroplastic_delta_b.csv and writes figures/poroplastic_delta_b.png.
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
# The matplotlib PGF backend needs a TeX engine; the repository toolchain has
# lualatex (no xelatex/dvipng), so select it explicitly for .pgf emission.
matplotlib.rcParams["pgf.texsystem"] = "lualatex"
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(ROOT, "validation", "poroplastic_delta_b.csv")
png_path = os.path.join(ROOT, "figures", "poroplastic_delta_b.png")

rows = []
with open(csv_path, newline="") as fh:
    for r in csv.DictReader(fh):
        v = {k: float(val) for k, val in r.items()}
        # Restrict to the physically meaningful range (elastic B_el >= 0);
        # the single-element uniaxial-strain closed form leaves the physical
        # regime beyond ~30% compression.
        if v["compression"] <= 0.30:
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
ax2.set_title("Plastic pore-allocation correction to $B$")
ax2.grid(alpha=0.3)

fig.tight_layout()
fig.savefig(png_path, dpi=200)
print("wrote", png_path)

# Manuscript-convention .pgf (matplotlib PGF backend), consumed with \input{...}.
from matplotlib.backends.backend_pgf import FigureCanvasPgf  # noqa: E402

pgf_path = os.path.join(ROOT, "figures", "poroplastic_delta_b.pgf")
FigureCanvasPgf(fig).print_pgf(pgf_path)
print("wrote", pgf_path)
