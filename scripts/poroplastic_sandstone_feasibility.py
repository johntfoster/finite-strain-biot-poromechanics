#!/usr/bin/env python3
"""Calibrated material-point model of the drained hydrostatic Biot-coefficient
response of Castlegate sandstone (B, step 1), compared against the authoritative
published Ingraham et al. (2017) Table 3.

Finding quantified here: over the drained hydrostatic path the measured
alpha = 1 - K/Km decline (~0.87 -> ~0.80 over 15 -> 140 MPa effective) is
reproduced, within specimen scatter (RMS ~0.008), by an ELASTIC pressure
stiffening model alone:

    Km(P) = a_km + b_km P             (unjacketed, 52.3 -> 63 GPa)
    K(P)  = c0 + c1 P + c2 P^2        (drained tangent, 5.9 -> ~12 GPa)
    alpha_el(P) = 1 - K(P)/Km(P)

with P the effective mean stress in MPa and moduli in MPa.  Fits are computed
inside this script from the authoritative hydrostatic rows of Table 3.

For contrast the figure also shows the constant-modulus finite-deformation
elastic coefficient of the repository (B_el(J) with fixed K0, Ks): that curve is
essentially flat and does NOT capture the measured decline, because the drained
bulk modulus in that model does not stiffen with pressure.  Matching Castlegate
hydrostatics therefore requires a pressure/state-dependent drained modulus, a
distinct constitutive ingredient from the poroplastic pore allocation a^p.

Data: Ingraham, Bauer, Issen, Dewers, Int. J. Rock Mech. Min. Sci. 96 (2017)
1-10, doi:10.1016/j.ijrmms.2017.04.004 (published copy in references/pdfs/).
Effective mean stress = applied mean stress - 6.89 MPa (pore pressure).
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pgf.texsystem"] = "lualatex"
import matplotlib.pyplot as plt
import numpy as np

PORE = 6.89  # MPa, held pore pressure during drained loops

# (applied mean MPa, drained K MPa, Km MPa, alpha) - hydrostatic rows (Table 3)
TABLE = [
    (22, 6856, 52278, 0.868), (44, 7802, 53796, 0.854), (94, 10716, 57246, 0.812),
    (144, 11864, 60696, 0.804), (32, 7162, 52950, 0.864), (51, 7991, 54265, 0.852),
    (76, 8938, 55995, 0.840), (101, 9730, 57717, 0.831), (121, 10489, 59093, 0.822),
    (50, 8246, 54210, 0.847), (100, 10610, 57660, 0.815), (33, 7342, 53037, 0.861),
    (73, 9025, 55810, 0.838), (24, 6541, 52436, 0.875), (43, 8148, 53713, 0.848),
    (63, 8998, 55107, 0.836), (35, 6723, 53140, 0.873), (73, 7899, 55797, 0.858),
]
# Unjacketed 4ac37 Km vs applied mean MPa (Table 3)
UNJ = [(51, 53410), (76, 57769), (100, 56420), (125, 60953), (150, 59077), (177, 63781)]

Pa = np.array([r[0] for r in TABLE], float)
K = np.array([r[1] for r in TABLE], float)
Km_tab = np.array([r[2] for r in TABLE], float)
alpha_m = np.array([r[3] for r in TABLE], float)
P_eff = Pa - PORE

# --- fits (derived from the table inside this script) ---
Km_all = np.concatenate([Km_tab, np.array([k for _, k in UNJ], float)])
Pe_all = np.concatenate([P_eff, np.array([p - PORE for p, _ in UNJ], float)])
b_km, a_km = np.polyfit(Pe_all, Km_all, 1)  # Km = a_km + b_km P
c2, c1, c0 = np.polyfit(P_eff, K, 2)         # K  = c0 + c1 P + c2 P^2

# --- elastic stiffening model and residual ---
Pgrid = np.linspace(5, 175, 400)
Km_fit = a_km + b_km * Pgrid
K_fit = c0 + c1 * Pgrid + c2 * Pgrid**2
alpha_el = 1.0 - K_fit / Km_fit

Km_d = a_km + b_km * P_eff
K_d = c0 + c1 * P_eff + c2 * P_eff**2
alpha_el_d = 1.0 - K_d / Km_d
rms_el = float(np.sqrt(np.mean((alpha_m - alpha_el_d) ** 2)))

# --- constant-modulus repo finite-deformation elastic B_el(J) reference ---
phi0 = 0.74
K0 = c0 * 1e6           # drained modulus at P_eff -> 0, Pa
Ks = a_km * 1e6         # unjacketed modulus at P_eff -> 0 (grain reference), Pa


def qs(J):
    return -K0 * math.log(J) / (phi0 * J)


def bel_const(J):
    rho = math.exp(qs(J) / Ks)
    return 1.0 - K0 * (1.0 - math.log(J)) / (Ks * J * J * rho)


B0_const = 1.0 - K0 / Ks
B_flat = []
for P in Pgrid:
    Pe = P * 1e6
    J = math.exp(-Pe / K0)           # drained hydrostatic, fixed K0
    B_flat.append(bel_const(J))
B_flat = np.array(B_flat)
# RMS of the constant-modulus model against the measured alpha (evaluated at data P)
B_flat_d = np.array([bel_const(math.exp(-p * 1e6 / K0)) for p in P_eff])
rms_const = float(np.sqrt(np.mean((alpha_m - B_flat_d) ** 2)))

print("Km(P) fit  : Km = %.0f + %.2f P  (MPa)" % (a_km, b_km))
print("K(P) fit   : K  = %.0f + %.2f P %.4f P^2 (MPa)" % (c0, c1, c2))
print("alpha0 (P->0, elastic stiffening model): %.4f" % (1.0 - c0 / a_km))
print("constant-modulus repo B0                : %.4f" % B0_const)
print("RMS elastic stiffening model vs data    : %.4f" % rms_el)
print("RMS constant-modulus repo model vs data : %.4f" % rms_const)

# --- figure ---
fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.plot(P_eff, alpha_m, "o", color="black", ms=5,
        label="Ingraham 2017, hydrostatic (Table 3)")
ax.plot(Pgrid, alpha_el, "-", color="tab:red", lw=1.8,
        label=r"elastic stiffening  $\alpha=1-K(P)/K_{\mathrm{m}}(P)$")
ax.plot(Pgrid, B_flat, "--", color="tab:gray", lw=1.5,
        label=r"constant-modulus repo $B_{\mathrm{el}}(J)$")
ax.set_xlabel(r"Effective mean stress  $P_{\mathrm{eff}}$  (MPa)")
ax.set_ylabel(r"Biot coefficient  $\alpha$")
ax.legend(fontsize=8, loc="upper right")
ax.grid(alpha=0.3)
ax.set_ylim(0.60, 0.95)
fig.tight_layout()
out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "figures", "sandstone_feasibility_overlay.png"))
fig.savefig(out, dpi=200)
print("wrote", out)
