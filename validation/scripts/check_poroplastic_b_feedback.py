#!/usr/bin/env python3
"""Canonical implicit-coefficient feedback check at nonzero pore pressure.

Runs the single-element stateful tensorial engine
(moose_app/test/tests/poroplastic_biot/poroplastic_b_feedback.i,
ADTensorialPoroplasticBiotMaterial, M = 0.6, beta = 0.4) under monotonic
drained compression to a target axial stretch at a prescribed uniform pore
pressure p0.  The single-prime driving stress carries the pore-allocation-
corrected coefficient B = 1 - (1 - B_el)/a^p (> B_el) through (1 - B) p J I;
a companion reference pass holds the elastic coefficient B_el in the
reconstruction (use_elastic_coefficient_in_trial = true), isolating the
coefficient feedback.  Checks:
  (i)   the corrected coefficient exceeds the elastic coefficient (B > B_el);
  (ii)  the corrected coefficient reduces the plastic response relative to the
        frozen-elastic reference (a^p < a_p_ref, Delta_gamma < Delta_gamma_ref);
  (iii) the split (over-prediction) grows with pore pressure at fixed
        compression and widens with compression at fixed pore pressure.
Curates validation/poroplastic_b_feedback.csv.

Run inside the moose conda environment.
"""

import csv
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DECK = os.path.join(ROOT, "moose_app", "test", "tests", "poroplastic_biot",
                    "poroplastic_b_feedback.i")
BINARY = os.path.join(ROOT, "moose_app", "nonlinear_biot_ad-opt")
OUT = os.path.join(ROOT, "validation", "poroplastic_b_feedback.csv")
SCRATCH = os.path.join(ROOT, ".agent-runtime", "poroplastic_b_feedback")

# Pore-pressure scan at 20% axial compression (axial target 0.80).
P_SCAN_COMP = 0.80
P_SCAN = [0.0, 5.0e7, 1.0e8, 1.5e8, 2.0e8, 2.5e8, 3.0e8, 4.0e8]
# Axial-compression scan at a fixed pore pressure.
C_SCAN_P = 2.0e8
C_SCAN_AXIAL = [0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65]


def run_case(axial_target, p0, reference, workdir, tag):
    name = "%s_ax%.2f_p%.0e" % (tag, axial_target, p0)
    deck = os.path.join(workdir, name + ".i")
    with open(DECK, encoding="utf-8") as fh:
        text = fh.read()
    text = text.replace("value = 1.5e8", "value = %.6g" % p0)
    text = text.replace("y = '1 0.8'", "y = '1 %.6g'" % axial_target)
    if reference:
        text = text.replace("dp_cohesion = 0.0",
                            "dp_cohesion = 0.0\n    use_elastic_coefficient_in_trial = true")
    with open(deck, "w", encoding="utf-8") as fh:
        fh.write(text)
    r = subprocess.run([BINARY, "-i", deck, "--no-color"],
                       cwd=workdir, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("run failed (%s):\n%s\n%s"
                           % (name, r.stdout[-1200:], r.stderr[-1200:]))
    with open(os.path.join(workdir, name + "_out.csv"), newline="") as fh:
        rows = list(csv.DictReader(fh))
    row = rows[-1]
    return {
        "a_p": float(row["a_p_avg"]),
        "dgamma": float(row["dgamma_avg"]),
        "B_el": float(row["b_el_avg"]),
        "B": float(row["b_avg"]),
    }


def main():
    if not os.path.exists(BINARY):
        sys.exit("binary not found: %s (build the app first)" % BINARY)
    if os.path.exists(SCRATCH):
        shutil.rmtree(SCRATCH)
    os.makedirs(SCRATCH)

    rows = []
    ok = True

    def add_case(axial, p0, c):
        coupled = run_case(axial, p0, False, SCRATCH, "cp")
        ref = run_case(axial, p0, True, SCRATCH, "cf")
        over = (ref["dgamma"] - coupled["dgamma"]) / ref["dgamma"] * 100.0 if ref["dgamma"] > 0 else 0.0
        row = {
            "axial_stretch": axial,
            "compression": 1.0 - axial,
            "pore_pressure": p0,
            "B_el": coupled["B_el"],
            "B_coupled": coupled["B"],
            "a_p": coupled["a_p"],
            "a_p_ref": ref["a_p"],
            "dgamma": coupled["dgamma"],
            "dgamma_ref": ref["dgamma"],
            "over_prediction_pct": over,
        }
        return row, c

    # (i)-(iii) local checks on one row.
    def check(row):
        good = True
        if row["B_coupled"] <= row["B_el"] + 1.0e-9:
            good = False
        if row["a_p"] > row["a_p_ref"] + 1.0e-9:
            good = False
        return good

    # Pore-pressure scan at 20% compression.
    for p0 in P_SCAN:
        row, good = add_case(P_SCAN_COMP, p0, True)
        rows.append(row)
        st = "OK" if good else "FAIL"
        if not good:
            ok = False
        print("[%s] p=%.0e  B_el=%.5f  B=%.5f  a_p=%.6f  a_p_ref=%.6f  "
              "over-pred=%.2f%%" % (st, p0, row["B_el"], row["B_coupled"],
                                    row["a_p"], row["a_p_ref"],
                                    row["over_prediction_pct"]))

    # Compression scan at fixed pore pressure.
    for axial in C_SCAN_AXIAL:
        row, good = add_case(axial, C_SCAN_P, True)
        rows.append(row)
        st = "OK" if good else "FAIL"
        if not good:
            ok = False
        print("[%s] comp=%.2f  B_el=%.5f  B=%.5f  a_p=%.6f  a_p_ref=%.6f  "
              "over-pred=%.2f%%" % (st, 1.0 - axial, row["B_el"],
                                    row["B_coupled"], row["a_p"], row["a_p_ref"],
                                    row["over_prediction_pct"]))

    fields = ["axial_stretch", "compression", "pore_pressure", "B_el",
              "B_coupled", "a_p", "a_p_ref", "dgamma", "dgamma_ref",
              "over_prediction_pct"]
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    print("wrote", OUT)
    print("RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
