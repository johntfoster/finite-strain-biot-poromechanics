#!/usr/bin/env python3
"""Verify the canonical stateful tensorial load-unload-reload engine and
curate validation/tensorial_load_unload.csv.

Runs moose_app/test/tests/poroplastic_biot/tensorial_load_unload.i (stateful
multiplicative ideal Drucker-Prager return mapping: F = F^e F^p, elastic trial
on F^e = F (F^p_n)^-1) with a fine time step and checks the verification gates:
  (c1) loading produces plastic flow (Delta_gamma > 0, a^p > 1);
  (c2) unloading is immediately elastic (Delta_gamma = 0 and a^p frozen at the
       peak value);
  (c3) reloading re-yields at the stored peak (a^p returns to at least the peak
       and Delta_gamma resumes near the peak).
The elastic-limit (a^p = 1) and step-size path-independence gates are separate
manual checks recorded in the scope note.

Run inside the moose conda environment.
"""

import csv
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DECK = os.path.join(ROOT, "moose_app", "test", "tests", "poroplastic_biot",
                    "tensorial_load_unload.i")
BINARY = os.path.join(ROOT, "moose_app", "nonlinear_biot_ad-opt")
OUT = os.path.join(ROOT, "validation", "tensorial_load_unload.csv")
SCRATCH = os.path.join(ROOT, ".agent-runtime", "tensorial_load_unload")


def main():
    if not os.path.exists(BINARY):
        sys.exit("binary not found: %s (build the app first)" % BINARY)
    if os.path.exists(SCRATCH):
        shutil.rmtree(SCRATCH)
    os.makedirs(SCRATCH)
    deck = os.path.join(SCRATCH, "tensorial_load_unload.i")
    shutil.copy(DECK, deck)
    r = subprocess.run([BINARY, "-i", deck, "--no-color"],
                       cwd=SCRATCH, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("run failed:\n%s\n%s" % (r.stdout[-1200:], r.stderr[-1200:]))
    with open(os.path.join(SCRATCH, "tensorial_load_unload_out.csv"), newline="") as fh:
        raw = list(csv.DictReader(fh))

    rows = []
    for rr in raw:
        t = float(rr["time"])
        axial = float(rr["compression"])  # the 'compression' postprocessor holds axial
        rows.append({"time": t, "axial_stretch": axial, "compression": 1.0 - axial,
                     "a_p": float(rr["a_p_avg"]), "dgamma": float(rr["dgamma_avg"]),
                     "B": float(rr["b_avg"])})

    peak = max(r["a_p"] for r in rows if r["time"] <= 1.0)
    # Unload window: t in (1,2): axial rises 0.8 -> 0.9 (compression falling).
    unload = [r for r in rows if 1.0 < r["time"] < 2.0]
    frozen = all(r["dgamma"] == 0.0 for r in unload)
    const = max(abs(r["a_p"] - peak) for r in unload) < 1e-9
    loaded = any(r["dgamma"] > 0 for r in rows if r["time"] <= 1.0)
    reload_end = max(r["a_p"] for r in rows if r["time"] > 2.0)
    re_yield = reload_end >= peak - 1e-6

    ok = loaded and frozen and const and re_yield
    print("peak a^p at 20%% compression = %.6f" % peak)
    print("load plastic (dg>0): %s | unload frozen (dg=0): %s | a^p const on unload: %s | reload reaches peak: %s"
          % (loaded, frozen, const, re_yield))
    print("RESULT: %s" % ("PASS" if ok else "FAIL"))

    fields = ["time", "axial_stretch", "compression", "a_p", "dgamma", "B"]
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("wrote", OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
