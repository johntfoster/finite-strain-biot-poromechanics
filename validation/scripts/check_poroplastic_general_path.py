#!/usr/bin/env python3
"""Canonical general-path oracle check (pure AD, no finite differences).

Runs the single-element deck moose_app/test/tests/poroplastic_biot/
poroplastic_general_path.i over a drained axial-compression sweep.  The plastic
pore allocation is frozen at the accumulated a^p of the canonical stateful
tensorial engine (ADTensorialPoroplasticBiotMaterial) at the same compression,
read from validation/poroplastic_delta_b.csv.  The check verifies that

    B_reduced = 1 - (1 - B_el)/a^p

equals the coefficient returned by the general fixed-history, fixed-pressure
tangent of the active plastic local system (assembled with AD by
ADConstrainedSkeletonBiotMaterial from the route-A residuals of
ADPlasticStateBiotMaterial with a^p frozen) to machine precision at every
compression, and that both equal the coefficient the canonical stateful engine
reports at the same state.  Curates validation/poroplastic_general_path.csv.

Run inside the moose conda environment:
  agent_environment/skills/setup-moose-conda/scripts/moose_conda_env.sh run -- \
      python3 validation/scripts/check_poroplastic_general_path.py
"""

import csv
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DECK = os.path.join(ROOT, "moose_app", "test", "tests", "poroplastic_biot",
                    "poroplastic_general_path.i")
BINARY = os.path.join(ROOT, "moose_app", "nonlinear_biot_ad-opt")
CANON = os.path.join(ROOT, "validation", "poroplastic_delta_b.csv")
OUT = os.path.join(ROOT, "validation", "poroplastic_general_path.csv")
SCRATCH = os.path.join(ROOT, ".agent-runtime", "poroplastic_general_path")
TOL = 1.0e-9          # AD oracle vs reduced closed form (within-run)
CROSS_TOL = 1.0e-6    # vs the canonical stateful coefficient (cross-run a^p)

# Drained axial-compression sweep (elastic B_el stays positive over the range).
AXIAL = [0.95, 0.90, 0.85, 0.80, 0.75, 0.70]


def load_canonical():
    by_axial = {}
    with open(CANON, newline="") as fh:
        for r in csv.DictReader(fh):
            ax = float(r["axial_stretch"])
            by_axial[ax] = {"a_p": float(r["a_p"]), "B_pl": float(r["B_pl"])}
    return by_axial


def run_case(axial, a_p, workdir):
    name = "general_path_%.2f" % axial
    deck = os.path.join(workdir, name + ".i")
    with open(DECK, encoding="utf-8") as fh:
        text = fh.read()
    text = text.replace("axial_stretch = 0.9", "axial_stretch = %.6g" % axial)
    text = text.replace("prop_values = 1.015137", "prop_values = %.9g" % a_p)
    with open(deck, "w", encoding="utf-8") as fh:
        fh.write(text)
    r = subprocess.run([BINARY, "-i", deck, "--no-color"],
                       cwd=workdir, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("run failed for axial=%g:\n%s\n%s"
                           % (axial, r.stdout[-1200:], r.stderr[-1200:]))
    csv_path = os.path.join(workdir, name + "_out.csv")
    with open(csv_path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise RuntimeError("empty csv for %s" % deck)
    row = rows[-1]
    return {
        "axial_stretch": axial,
        "compression": 1.0 - axial,
        "a_p": float(row["a_p_avg"]),
        "B_el": float(row["b_el_avg"]),
        "B_general": float(row["b_general_avg"]),
        "B_reduced": float(row["b_reduced_avg"]),
        "oracle_error": float(row["oracle_error_avg"]),
    }


def main():
    if not os.path.exists(BINARY):
        sys.exit("binary not found: %s (build the app first)" % BINARY)
    canon = load_canonical()
    if os.path.exists(SCRATCH):
        shutil.rmtree(SCRATCH)
    os.makedirs(SCRATCH)

    rows = []
    ok = True
    for axial in AXIAL:
        a_p_canon = canon[axial]["a_p"]
        row = run_case(axial, a_p_canon, SCRATCH)
        rows.append(row)
        err = abs(row["oracle_error"])
        cross = abs(row["B_reduced"] - canon[axial]["B_pl"])
        status = "OK"
        if err > TOL or cross > CROSS_TOL:
            status = "FAIL"
            ok = False
        print("[%s] axial=%.2f a_p=%.6f B_el=%.6f B_general=%.6f B_reduced=%.6f "
              "oracle_error=%.3e cross_vs_stateful=%.3e"
              % (status, axial, row["a_p"], row["B_el"], row["B_general"],
                 row["B_reduced"], row["oracle_error"], cross))

    worst = max(abs(r["oracle_error"]) for r in rows)
    fields = ["axial_stretch", "compression", "a_p", "B_el", "B_general",
              "B_reduced", "oracle_error"]
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    print("wrote", OUT)
    print("RESULT: %s (max |B_general - B_reduced| = %.3e, tolerance %.0e)"
          % ("PASS" if ok else "FAIL", worst, TOL))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
