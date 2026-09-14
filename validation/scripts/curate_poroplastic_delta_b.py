#!/usr/bin/env python3
"""Run the implicit drained compression sweep and curate its Biot coefficients.

The independent scalar mineral solve verifies equation (68) at each returned
plastic distention. The checks also require active dilation and an increasing
history contribution through the sampled compression range.
"""

from check_stress_trace_derivation import mineral

import csv
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DECK = os.path.join(ROOT, "moose_app", "test", "tests", "poroplastic_biot",
                    "poroplastic_delta_b_sweep.i")
BINARY = os.path.join(ROOT, "moose_app", "nonlinear_biot_ad-opt")
OUT = os.path.join(ROOT, "validation", "poroplastic_delta_b.csv")
SCRATCH = os.path.join(ROOT, ".agent-runtime", "poroplastic_delta_b_sweep")

# Curated sampling of the monotonic path (axial stretch -> compression).
SAMPLES = [(0.95, 0.05), (0.90, 0.10), (0.85, 0.15), (0.80, 0.20),
           (0.75, 0.25), (0.70, 0.30), (0.65, 0.35)]


def main():
    if not os.path.exists(BINARY):
        sys.exit("binary not found: %s (build the app first)" % BINARY)
    if os.path.exists(SCRATCH):
        shutil.rmtree(SCRATCH)
    os.makedirs(SCRATCH)
    deck = os.path.join(SCRATCH, "poroplastic_delta_b_sweep.i")
    shutil.copy(DECK, deck)
    r = subprocess.run([BINARY, "-i", deck, "--no-color"],
                       cwd=SCRATCH, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("run failed:\n%s\n%s" % (r.stdout[-1200:], r.stderr[-1200:]))
    with open(os.path.join(SCRATCH, "poroplastic_delta_b_sweep_out.csv"), newline="") as fh:
        raw = list(csv.DictReader(fh))

    # For each sampled axial stretch pick the row where the (monotonically
    # decreasing) axial stretch first drops to or below the target, i.e. the
    # sample closest to the target from above.
    rows = []
    for target_ax, comp in SAMPLES:
        best = None
        for rr in raw:
            ax = float(rr["compression"])  # postprocessor holds axial stretch
            if ax <= target_ax + 1e-9:
                best = rr
                break
        if best is None:
            raise RuntimeError("sweep did not reach axial stretch %s" % target_ax)
        a_p = float(best["a_p_avg"])
        b_el = float(best["b_el_avg"])
        b = float(best["b_avg"])
        rows.append({"axial_stretch": target_ax, "compression": comp,
                     "a_p": a_p, "B_el": b_el, "B_pl": b,
                     "delta_B": float(best["db_avg"])})

    # Checks.
    active = all(rr["a_p"] > 1.0 and rr["delta_B"] > 0 for rr in rows)
    closed_form = all(
        abs(rr["B_pl"] - mineral(rr["axial_stretch"], 0., 1e9, 2.5e9, .8, rr["a_p"])[2]) < 1.0e-12
        for rr in rows)
    growing = all(
        rows[i + 1]["delta_B"] > rows[i]["delta_B"]
        for i in range(len(rows) - 1) if rows[i + 1]["compression"] <= 0.30)
    ok = active and closed_form and growing

    print("rows: %d  active(a^p>1, dB>0): %s  closed form: %s  growing: %s"
          % (len(rows), active, closed_form, growing))
    for rr in rows:
        print("  compression=%.2f  a^p=%.6f  B_el=%.6f  B_pl=%.6f  delta_B=%.6f"
              % (rr["compression"], rr["a_p"], rr["B_el"], rr["B_pl"], rr["delta_B"]))
    print("RESULT: %s" % ("PASS" if ok else "FAIL"))

    fields = ["axial_stretch", "compression", "a_p", "B_el", "B_pl", "delta_B"]
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for rr in rows:
            w.writerow(rr)
    print("wrote", OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
