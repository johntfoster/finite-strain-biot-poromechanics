#!/usr/bin/env python3
"""V3 unload-branch (frozen-history) coefficient demonstration.

After monotonic plastic (dilative) loading to a peak compression, the plastic
pore allocation a^p is frozen; along an unloading branch the coefficient is the
fixed-history, fixed-pressure tangent at the reduced compression.  This driver
evaluates that unload coefficient by pure AD (deck
poroplastic_unload_tangent.i: ADPlasticStateBiotMaterial residuals + the dense
AD solve of ADConstrainedSkeletonBiotMaterial with a^p frozen), verifies it
equals the reduced closed form B = 1 - (1 - B_el)/a^p to machine precision at
every unload point, and shows it exceeds the virgin elastic coefficient B_el at
the same compression (the unload/reload-tangent reading of alpha in the
literature).  Curates validation/poroplastic_load_unload.csv.

Peak state and the monotonic loading branch are read from
validation/poroplastic_general_path.csv (V2); the unload branch is computed
here.  Run inside the moose conda environment.
"""

import csv
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DECK = os.path.join(ROOT, "moose_app", "test", "tests", "poroplastic_biot",
                    "poroplastic_unload_tangent.i")
BINARY = os.path.join(ROOT, "moose_app", "nonlinear_biot_ad-opt")
GENERAL = os.path.join(ROOT, "validation", "poroplastic_general_path.csv")
OUT = os.path.join(ROOT, "validation", "poroplastic_load_unload.csv")
SCRATCH = os.path.join(ROOT, ".agent-runtime", "poroplastic_load_unload")
TOL = 1.0e-7  # AD-vs-reduced agreement at CSV precision (within-run oracle ~1e-16)
PEAK_COMPRESSION = 0.20  # monotonic peak load (axial stretch 0.80)


def load_general():
    rows = {}
    with open(GENERAL, newline="") as fh:
        for r in csv.DictReader(fh):
            c = round(float(r["compression"]), 6)
            rows[c] = {
                "compression": c,
                "axial_stretch": float(r["axial_stretch"]),
                "a_p": float(r["a_p"]),
                "B_el": float(r["B_el"]),
                "B_mono": float(r["B_reduced"]),
            }
    return rows


def run_unload(axial, a_p_frozen, workdir):
    name = "unload_%.3f_ap%.6f" % (axial, a_p_frozen)
    deck = os.path.join(workdir, name + ".i")
    with open(DECK, encoding="utf-8") as fh:
        text = fh.read()
    text = text.replace("axial_stretch = 0.9", "axial_stretch = %.6g" % axial)
    text = text.replace("prop_values = 1.031877", "prop_values = %.9g" % a_p_frozen)
    with open(deck, "w", encoding="utf-8") as fh:
        fh.write(text)
    r = subprocess.run([BINARY, "-i", deck, "--no-color"],
                       cwd=workdir, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("run failed axial=%g:\n%s\n%s"
                           % (axial, r.stdout[-1200:], r.stderr[-1200:]))
    with open(os.path.join(workdir, name + "_out.csv"), newline="") as fh:
        rows = list(csv.DictReader(fh))
    row = rows[-1]
    return {
        "B_el": float(row["b_el_avg"]),
        "B_general": float(row["b_general_avg"]),
        "B_reduced": float(row["b_reduced_avg"]),
        "oracle_error": float(row["oracle_error_avg"]),
        "a_p": float(row["a_p_avg"]),
    }


def main():
    if not os.path.exists(BINARY):
        sys.exit("binary not found: %s (build the app first)" % BINARY)
    general = load_general()
    peak = general[PEAK_COMPRESSION]
    a_p_peak = peak["a_p"]
    print("peak: compression=%.2f  a^p=%.6f  B_mono=%.6f"
          % (PEAK_COMPRESSION, a_p_peak, peak["B_mono"]))

    if os.path.exists(SCRATCH):
        shutil.rmtree(SCRATCH)
    os.makedirs(SCRATCH)

    # Unload branch: axial stretches from near-reference up to the peak.
    unload_axials = [0.95, 0.90, 0.85, 0.80]
    unload_rows = []
    ok = True
    for axial in unload_axials:
        comp = round(1.0 - axial, 4)
        res = run_unload(axial, a_p_peak, SCRATCH)
        err = abs(res["oracle_error"])
        # pure-AD cross-check against the reduced closed form at the frozen state
        reduced_check = 1.0 - (1.0 - res["B_el"]) / a_p_peak
        ad_err = abs(res["B_general"] - reduced_check)
        delta = res["B_general"] - res["B_el"]
        status = "OK"
        if err > TOL or ad_err > TOL or delta <= 0.0:
            status = "FAIL"
            ok = False
        row = {
            "axial_stretch": axial,
            "compression": comp,
            "B_el_virgin": res["B_el"],
            "B_monotonic_load": general[comp]["B_mono"],
            "a_p_frozen": a_p_peak,
            "B_unload_frozen": res["B_general"],
            "delta_unload_vs_elastic": delta,
            "ad_vs_reduced_error": ad_err,
        }
        unload_rows.append(row)
        print("[%s] comp=%.2f  B_el=%.6f  B_mono=%.6f  B_unload=%.6f  "
              "B_unload-B_el=%.6f  ad_vs_reduced=%.2e"
              % (status, comp, row["B_el_virgin"], row["B_monotonic_load"],
                 row["B_unload_frozen"], row["delta_unload_vs_elastic"], ad_err))

    # Curate: monotonic load branch (from V2) + unload branch.
    fields = ["axial_stretch", "compression", "branch", "B_el", "a_p", "B"]
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for comp in [0.05, 0.10, 0.15, 0.20]:
            g = general[comp]
            w.writerow({"axial_stretch": g["axial_stretch"], "compression": comp,
                        "branch": "monotonic", "B_el": g["B_el"], "a_p": g["a_p"],
                        "B": g["B_mono"]})
        for row in unload_rows:
            w.writerow({"axial_stretch": row["axial_stretch"],
                        "compression": row["compression"], "branch": "unload",
                        "B_el": row["B_el_virgin"], "a_p": a_p_peak,
                        "B": row["B_unload_frozen"]})
    print("wrote", OUT)
    print("RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
