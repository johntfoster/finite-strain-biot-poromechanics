#!/usr/bin/env python3
"""Verify pressure feedback using simultaneous compression and pressure ramps.

The implicit return uses the current mineral state and coefficient. A companion
return substitutes the virgin coefficient in the driving stress. The smooth
solutions must have B greater than virgin B and distention no greater than the
companion value. An independent apex calculation identifies and tests rejection
of a prescribed state outside the manuscript's smooth-cone domain.
"""

import math
import json
from check_stress_trace_derivation import mineral

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


def run_case(axial_target, p0, reference, workdir, tag, outside_smooth_cone=False):
    name = "%s_ax%.2f_p%.0e" % (tag, axial_target, p0)
    deck = os.path.join(workdir, name + ".i")
    with open(DECK, encoding="utf-8") as fh:
        text = fh.read()
    text = text.replace("1.5e8*min(t,1)", "%.6g*min(t,1)" % p0)
    text = text.replace("y = '1 0.8'", "y = '1 %.6g'" % axial_target)
    if reference:
        text = text.replace("dp_cohesion = 0.0",
                            "dp_cohesion = 0.0\n    use_elastic_coefficient_in_trial = true")
    with open(deck, "w", encoding="utf-8") as fh:
        fh.write(text)
    r = subprocess.run([BINARY, "-i", deck, "--no-color"],
                       cwd=workdir, capture_output=True, text=True)
    with open(os.path.join(workdir, name + ".log"), "w") as stream:
        stream.write(r.stdout + r.stderr)
    if outside_smooth_cone:
        if r.returncode == 0 or "local line search failed on smooth cone branch" not in r.stdout + r.stderr:
            raise AssertionError("The independently inadmissible smooth-cone state was not rejected")
        return None
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
        return row, check(row)

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
    domain_rejections = []
    for axial in C_SCAN_AXIAL:
        # On this coaxial path, equal elastic stretches occur at total
        # gamma=-2 log(axial)/3. If the mean stress there is tensile,
        # the cohesionless cone has no admissible smooth return before its apex.
        gamma_apex = -2 * math.log(axial) / 3
        ap_apex = math.exp(.4 * gamma_apex)
        z = mineral(axial, C_SCAN_P, 1e9, 2.5e9, .8, ap_apex)[0]
        mean_apex = -1e9 * (math.log(axial / ap_apex) + C_SCAN_P * z / 2.5e9)
        if mean_apex < 0:
            run_case(axial, C_SCAN_P, False, SCRATCH, "domain", outside_smooth_cone=True)
            domain_rejections.append(dict(axial_stretch=axial, pore_pressure=C_SCAN_P,
                                          mean_stress_at_apex=mean_apex,
                                          outcome="rejected_outside_smooth_cone"))
            print("DOMAIN REJECTION axial=%.2f p=%.0e: tensile apex mean %.6g Pa" %
                  (axial, C_SCAN_P, mean_apex))
            continue
        row, good = add_case(axial, C_SCAN_P, True)
        rows.append(row)
        st = "OK" if good else "FAIL"
        if not good:
            ok = False
        print("[%s] comp=%.2f  B_el=%.5f  B=%.5f  a_p=%.6f  a_p_ref=%.6f  "
              "over-pred=%.2f%%" % (st, 1.0 - axial, row["B_el"],
                                    row["B_coupled"], row["a_p"], row["a_p_ref"],
                                    row["over_prediction_pct"]))

    if not ok:
        raise AssertionError("Pressure feedback acceptance failed; curated data were not replaced")
    with open(os.path.join(ROOT, "validation", "poroplastic_domain_checks.json"), "w") as stream:
        json.dump(domain_rejections, stream, indent=2)
        stream.write("\n")
    fields = ["axial_stretch", "compression", "pore_pressure", "B_el",
              "B_coupled", "a_p", "a_p_ref", "dgamma", "dgamma_ref",
              "over_prediction_pct"]
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow(row)
    print("wrote", OUT)
    print("RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
