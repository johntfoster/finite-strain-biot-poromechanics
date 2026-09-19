#!/usr/bin/env python3
"""Generate the verified plastic figures for the manuscript and website."""

import csv
import json
from pathlib import Path
import shutil
import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams.update(
    {
        "pgf.texsystem": "lualatex",
        "pgf.rcfonts": False,
        "font.family": "serif",
        "font.size": 9,
        "legend.fontsize": 8,
    }
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pgf import FigureCanvasPgf

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    with (ROOT / "validation" / name).open() as stream:
        return [{k: float(v) for k, v in r.items()} for r in csv.DictReader(stream)]


def save(fig, name):
    fig.tight_layout()
    png = ROOT / "figures" / f"{name}.png"
    fig.savefig(png, dpi=220)
    FigureCanvasPgf(fig).print_pgf(ROOT / "figures" / f"{name}.pgf")
    shutil.copyfile(png, ROOT / "docs/assets/img" / png.name)
    plt.close(fig)


record = json.loads((ROOT / 'validation/implicit_poroplastic_verification.json').read_text())
if not record.get('accepted') or record['parameters']['hardening_modulus_Pa'] != 1e8:
    raise ValueError('Publication figures require verified isotropic-hardening results')
history = read("implicit_poroplastic_history.csv")
fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.7))
for lo, hi, label, color, linestyle in [
    (0, 1, "loading", "#356e9d", "-"),
    (1, 2, "unloading", "#c57a26", "-"),
    (2, 3, "reloading", "#3c8b68", "--"),
]:
    rows = [r for r in history if lo - 1e-8 <= r["time"] <= hi + 1e-8]
    axes[0].plot(
        [1 - r["compression"] for r in rows],
        [r["b_avg"] for r in rows],
        color=color,
        linestyle=linestyle,
        label=label,
    )
    axes[1].plot(
        [r["time"] for r in rows],
        [r["a_p_avg"] for r in rows],
        color=color,
        linestyle=linestyle,
    )
virgin = sorted(history, key=lambda r: 1 - r["compression"])
axes[0].plot(
    [1 - r["compression"] for r in virgin],
    [r["b_el"] for r in virgin],
    "--",
    color=".35",
    label="virgin elastic",
)
axes[0].set(xlabel="Axial compression", ylabel=r"Biot coefficient, $B$")
axes[1].set(xlabel="Load-path parameter", ylabel=r"Plastic distention, $a^p$")
axes[0].legend(frameon=False)
for ax in axes:
    ax.grid(alpha=0.2)
save(fig, "implicit_poroplastic_history")

rows = read("implicit_poroplastic_feedback.csv")
p = [r["pressure"] / 1e6 for r in rows]
fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.7))
axes[0].plot(
    p,
    [r["B"] for r in rows],
    "-o",
    color="#356e9d",
    label="current plastic state",
    ms=3,
)
axes[0].plot(
    p, [r["B_virgin"] for r in rows], "--", color=".35", label="virgin elastic state"
)
axes[1].plot(
    p,
    [r["a_p"] for r in rows],
    "-o",
    color="#356e9d",
    label="consistent transform",
    ms=3,
)
axes[1].plot(
    p,
    [r["a_p_reference"] for r in rows],
    "--",
    color=".35",
    label=r"virgin $B$ in transform",
)
axes[0].set_ylabel(r"Biot coefficient, $B$")
axes[1].set_ylabel(r"Plastic distention, $a^p$")
for ax in axes:
    ax.set_xlabel("Final pore pressure [MPa]")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False)
save(fig, "implicit_poroplastic_feedback")
