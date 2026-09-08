#!/usr/bin/env python3
"""Sweep the single-element B-feedback demonstration deck
(moose_app/test/tests/poroplastic_biot/poroplastic_b_feedback.i) over axial
compression and uniform pore pressure, and curate
validation/poroplastic_b_feedback.csv.

The deck reports, in one steady single-element solve:
  coupled  : a^p, Delta_gamma, returned p' and q', and the coefficient B_used
             (implicit poroplastic B = 1 - (1 - B_el)/a^p, solved consistently
             with the return map), and
  reference: a_p_ref, dgamma_ref, p'_ref, q'_ref from the same return with the
             elastic coefficient B_el frozen in the driving stress.
The sweep therefore isolates the feedback of the inelastic correction into the
plastic response at nonzero pore pressure.

Run inside the moose conda environment:
  agent_environment/skills/setup-moose-conda/scripts/moose_conda_env.sh run -- \
      python3 scripts/sweep_poroplastic_b_feedback.py
"""

import csv
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECK = os.path.join(ROOT, "moose_app", "test", "tests", "poroplastic_biot",
                    "poroplastic_b_feedback.i")
BINARY = os.path.join(ROOT, "moose_app", "nonlinear_biot_ad-opt")
OUT = os.path.join(ROOT, "validation", "poroplastic_b_feedback.csv")
SCRATCH = os.path.join(ROOT, ".agent-runtime", "poroplastic_b_feedback_sweep")

# (axial_stretch, pore_pressure[Pa]) grid.  Physical regime: elastic B_el >= 0
# (compression <= ~30%) with the yield active.
GRID = [
    # Pore-pressure scan at 20% compression.
    (0.80, 0.0e0), (0.80, 2.5e7), (0.80, 5.0e7), (0.80, 7.5e7),
    (0.80, 1.0e8), (0.80, 1.5e8), (0.80, 2.0e8), (0.80, 2.5e8),
    (0.80, 3.0e8), (0.80, 4.0e8),
    # Compression scan at fixed pore pressure 2e8 Pa.
    (0.95, 2.0e8), (0.90, 2.0e8), (0.85, 2.0e8), (0.80, 2.0e8),
    (0.75, 2.0e8), (0.70, 2.0e8), (0.65, 2.0e8),
]


def make_deck(axial, p0, path):
    """Substitute the two sweep anchors in the canonical deck."""
    with open(DECK, encoding="utf-8") as fh:
        text = fh.read()
    text = text.replace("axial_stretch = 0.8", "axial_stretch = %.6g" % axial)
    text = text.replace("value = 1.5e8", "value = %.6g" % p0)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def run_case(axial, p0, workdir):
    name = "case_a%.4f_p%.4g" % (axial, p0)
    deck = os.path.join(workdir, name + ".i")
    make_deck(axial, p0, deck)
    r = subprocess.run([BINARY, "-i", deck, "--no-color"],
                       cwd=workdir, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("run failed for axial=%g p0=%g:\n%s\n%s"
                           % (axial, p0, r.stdout[-1500:], r.stderr[-1500:]))
    csv_path = os.path.join(workdir, name + "_out.csv")
    # MOOSE names the output csv after the deck base name.
    if not os.path.exists(csv_path):
        cand = os.path.join(workdir, name + ".csv")
        if os.path.exists(cand):
            csv_path = cand
        else:
            raise RuntimeError("no csv produced for %s" % deck)
    with open(csv_path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise RuntimeError("empty csv for %s" % deck)
    row = rows[-1]
    return {
        "axial_stretch": axial,
        "compression": 1.0 - axial,
        "pore_pressure": p0,
        "B_el": float(row["b_el_avg"]),
        "B_used": float(row["b_used_avg"]),
        "a_p": float(row["a_p_avg"]),
        "a_p_ref": float(row["a_p_ref_avg"]),
        "dgamma": float(row["dgamma_avg"]),
        "dgamma_ref": float(row["dgamma_ref_avg"]),
        "mean_p": float(row["mean_p_avg"]),
        "mean_p_ref": float(row["mean_p_ref_avg"]),
        "q": float(row["q_avg"]),
        "q_ref": float(row["q_ref_avg"]),
    }


def main():
    if not os.path.exists(BINARY):
        sys.exit("binary not found: %s (build the app first)" % BINARY)
    if os.path.exists(SCRATCH):
        shutil.rmtree(SCRATCH)
    os.makedirs(SCRATCH)

    results = []
    for i, (axial, p0) in enumerate(GRID, start=1):
        print("[%d/%d] axial=%.2f p0=%.3g Pa" % (i, len(GRID), axial, p0))
        results.append(run_case(axial, p0, SCRATCH))

    fields = ["axial_stretch", "compression", "pore_pressure", "B_el", "B_used",
              "a_p", "a_p_ref", "dgamma", "dgamma_ref", "mean_p", "mean_p_ref",
              "q", "q_ref"]
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in results:
            w.writerow(row)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
