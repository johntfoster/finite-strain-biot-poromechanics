#!/usr/bin/env python3
"""Feasibility (uncalibrated) material-point model of the drained hydrostatic
Biot-coefficient response, intended as a shape check against Ingraham et al.
(2017) Castle-gate sandstone.

Assumptions (all documented, feasibility only, to be replaced by the coupled
MOOSE cap implementation and calibration):
  - drained, hydrostatic loading; compressive effective mean P_eff;
  - elastic drained hydrostatic relation P_eff = -K0 ln(J);
  - repo finite-deformation elastic Biot coefficient B_el(J) with
    q_s = -K0 ln(J)/(phi0 J), rho = exp(q_s/K_s),
    B_el = 1 - K0 (1-ln J)/(K_s J^2 rho);
  - idealized compactive (cap) mechanism: for P_eff > P_c the plastic pore
    allocation compacts, a^p = exp(-(P_eff-P_c)/K_pl), with an equal extra
    volumetric collapse reducing J; B_pl = 1 - (1-B_el)/a^p.
Approximate Castle-gate parameters from Ingraham 2017 (Table 3 / Fig. 5):
  phi0=0.74, drained bulk K0~7.5 GPa, grain modulus K_s~55 GPa.  P_c and K_pl
  are placeholders for the calibration step.
"""
import math
import os

phi0 = 0.74
K0 = 7.5e9
Ks = 55.0e9
Pc = 80.0e6
Kpl = 1.5e9
pore = 6.91  # downstream pore pressure (MPa) subtracted in the data

Ps = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 225, 250, 275]


def qs(J):
    return -K0 * math.log(J) / (phi0 * J)


def bel(J):
    rho = math.exp(qs(J) / Ks)
    return 1.0 - K0 * (1.0 - math.log(J)) / (Ks * J * J * rho)


print("P_eff(MPa)  J      B_el    a_p     B_pl      dB")
rows = []
for P in Ps:
    Pe = (P - pore) * 1e6
    over = max(Pe - Pc, 0.0)
    ap = math.exp(-over / Kpl)
    J = math.exp(-Pe / K0) * math.exp(-over / Kpl)
    B_el = bel(J)
    B_pl = 1.0 - (1.0 - B_el) / ap
    rows.append((Pe / 1e6, J, B_el, ap, B_pl, B_pl - B_el))
    print(f"{Pe/1e6:7.1f}  {J:6.4f}  {B_el:6.4f}  {ap:6.4f}  {B_pl:6.4f}   {B_pl-B_el:+.4f}")

# Ingraham 2017 hydrostatic unload points (effective mean vs B), Table 3.
data = [
    (15.1, 0.868), (37.1, 0.869), (77.1, 0.812), (137.1, 0.804),
    (25.1, 0.860), (44.1, 0.852), (69.1, 0.849), (94.1, 0.831), (114.1, 0.823),
    (24.1, 0.861), (43.1, 0.847), (66.1, 0.838), (93.1, 0.815),
    (17.1, 0.875), (36.1, 0.848), (56.1, 0.836),
    (28.1, 0.873), (66.1, 0.858), (124.1, 0.853),
]
print(f"\nexperimental points: {len(data)}")

# Minimal overlay plot (Agg) for inspection.
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pgf.texsystem"] = "lualatex"
import matplotlib.pyplot as plt

pe = [r[0] for r in rows]
bb = [r[4] for r in rows]
be_ = [r[2] for r in rows]
dx = [d[0] for d in data]
dy = [d[1] for d in data]
fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.plot(dx, dy, "o", color="black", ms=4, label="Ingraham 2017 (hydrostatic, drained)")
ax.plot(pe, be_, "--", color="tab:gray", label=r"$B$ elastic only")
ax.plot(pe, bb, "-", color="tab:red", label=r"$B$ with compactive cap (feasibility)")
ax.set_xlabel(r"Effective mean stress  $P_{\mathrm{eff}}$  (MPa)")
ax.set_ylabel(r"Biot coefficient  $B$")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
ax.set_ylim(0.55, 0.95)
fig.tight_layout()
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                   "sandstone_feasibility_overlay.png")
fig.savefig(os.path.normpath(out), dpi=200)
print("wrote", os.path.normpath(out))
