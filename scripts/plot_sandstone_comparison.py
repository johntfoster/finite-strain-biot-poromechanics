#!/usr/bin/env python3
"""Manuscript figure: drained sandstone hydrostatics as a compactive target
(Ingraham et al. 2017, Castlegate), positioned against this paper's model.

Panel (a): measured drained hydrostatic Biot coefficient alpha = 1 - K/Km vs
effective mean stress (published Table 3), the constant-modulus finite-strain
elastic coefficient of THIS paper's model over the same nominal hydrostatic
path (flat: it cannot reproduce the decline), and the drained-modulus
stiffening alpha(P) = 1 - K_fit(P)/Km_fit(P) calibrated to the same data -
i.e. the constitutive ingredient (a pressure-/porosity-dependent drained
modulus) that a quantitative compactive match requires.

Panel (b): the compactive (porosity-loss) reading of the same data: porosity
phi(P) inferred by inverting the measured drained K(P) through a porosity-only
law K(phi) anchored at the initial porosity (0.26) and the measured post-test
porosity of the hydrostatic specimen (0.14), and the corresponding plastic pore
allocation a^p(P) = phi_s0/(1 - phi(P)) with phi_s0 = 0.74.  The star marks the
independent post-test measurement.  a^p < 1 is the compactive branch of the
manuscript's volumetric mechanism (Sec. 2.4), which lowers
B = 1 - (1 - B_el)/a^p.

Honesty: panel (a)'s red curve and all of panel (b) are calibrations of
ingredients NOT in the current model (constant drained modulus); they identify
the required extension.  Data provenance: published copy in references/pdfs/
(IJRMSS 96 (2017) 1-10, doi:10.1016/j.ijrmms.2017.04.004); effective mean
stress = applied minus 6.89 MPa.
"""
import os

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams.update(
    {
        "pgf.texsystem": "lualatex",
        "pgf.rcfonts": False,
        "font.family": "serif",
        "font.size": 9.0,
        "axes.labelsize": 9.0,
        "axes.titlesize": 9.0,
        "xtick.labelsize": 8.0,
        "ytick.labelsize": 8.0,
        "legend.fontsize": 7.5,
    }
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pgf import FigureCanvasPgf  # noqa: E402
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORE = 6.89
PHI0 = 0.26
PHI_END = 0.14
P_FAIL_EFF = 180.04 - PORE

TABLE = [
    (22, 6856, 52278, 0.868), (44, 7802, 53796, 0.854), (94, 10716, 57246, 0.812),
    (144, 11864, 60696, 0.804), (32, 7162, 52950, 0.864), (51, 7991, 54265, 0.852),
    (76, 8938, 55995, 0.840), (101, 9730, 57717, 0.831), (121, 10489, 59093, 0.822),
    (50, 8246, 54210, 0.847), (100, 10610, 57660, 0.815), (33, 7342, 53037, 0.861),
    (73, 9025, 55810, 0.838), (24, 6541, 52436, 0.875), (43, 8148, 53713, 0.848),
    (63, 8998, 55107, 0.836), (35, 6723, 53140, 0.873), (73, 7899, 55797, 0.858),
]
UNJ = [(51, 53410), (76, 57769), (100, 56420), (125, 60953), (150, 59077), (177, 63781)]

Pa = np.array([r[0] for r in TABLE], float)
K = np.array([r[1] for r in TABLE], float)
Km_tab = np.array([r[2] for r in TABLE], float)
alpha_m = np.array([r[3] for r in TABLE], float)
P_eff = Pa - PORE

Km_all = np.concatenate([Km_tab, np.array([k for _, k in UNJ], float)])
Pe_all = np.concatenate([P_eff, np.array([p - PORE for p, _ in UNJ], float)])
b_km, a_km = np.polyfit(Pe_all, Km_all, 1)
c2, c1, c0 = np.polyfit(P_eff, K, 2)


def K_fit(P):
    return c0 + c1 * P + c2 * P**2


def Km_lin(P):
    return a_km + b_km * P


# --- calibrated drained-stiffening alpha(P) ---
Pgrid = np.linspace(5, 175, 400)
alpha_el = 1.0 - K_fit(Pgrid) / Km_lin(Pgrid)

# --- THIS model: constant-modulus finite-strain elastic B_el(J) over the same
# nominal drained hydrostatic path J = exp(-P_eff/K0) ---
phi_s0 = 1.0 - PHI0
K0 = c0          # drained modulus at P_eff -> 0 (MPa)
Ks = a_km        # grain/unjacketed modulus at P_eff -> 0 (MPa)


def bel_const(J):
    qs = -K0 * np.log(J) / (phi_s0 * J)
    rho = np.exp(qs / Ks)
    return 1.0 - K0 * (1.0 - np.log(J)) / (Ks * J * J * rho)


B_model = bel_const(np.exp(-Pgrid / K0))

# --- compactive porosity-loss reading (panel b) ---
K0e = K_fit(0.0)
K_end = K_fit(P_FAIL_EFF)
lam = np.log(K_end / K0e) / (PHI0 - PHI_END)
K_sd = K0e * np.exp(lam * PHI0)


def phi_of_P(P):
    return (np.log(K_sd) - np.log(K_fit(P))) / lam


def ap_of_P(P):
    return phi_s0 / (1.0 - phi_of_P(P))


phi_g = phi_of_P(Pgrid)
ap_g = ap_of_P(Pgrid)

fig, (axa, axb) = plt.subplots(1, 2, figsize=(6.6, 3.1))
axa.plot(P_eff, alpha_m, "o", color="black", ms=4.5,
         label="Castlegate, drained hydrostatic (Table 3)")
axa.plot(Pgrid, B_model, "--", color="tab:gray", lw=1.8,
         label=r"this model: constant-modulus $B_{\mathrm{el}}(J)$")
axa.plot(Pgrid, alpha_el, "-", color="tab:red", lw=1.8,
         label=r"drained-stiffening modulus (calibration)")
axa.set_xlabel(r"Effective mean stress  $P_{\mathrm{eff}}$  (MPa)")
axa.set_ylabel(r"Biot coefficient  $\alpha$")
axa.legend(loc="lower left")
axa.grid(alpha=0.3)
axa.set_ylim(0.78, 0.92)

axb.plot(Pgrid, phi_g, "-", color="tab:blue", lw=1.8, label=r"porosity  $\phi(P)$")
axb.plot(Pgrid, ap_g, "-.", color="tab:green", lw=1.8,
         label=r"compactive  $a^{p}(P)$")
axb.plot([P_FAIL_EFF], [PHI_END], "*", color="black", ms=12,
         label="post-test porosity 0.14")
axb.set_xlabel(r"Effective mean stress  $P_{\mathrm{eff}}$  (MPa)")
axb.set_ylabel(r"$\phi$ ,  $a^{p}$")
axb.legend(loc="lower left")
axb.grid(alpha=0.3)
axb.set_ylim(0.10, 1.02)

fig.tight_layout()
png_path = os.path.join(ROOT, "figures", "sandstone_comparison.png")
fig.savefig(png_path, dpi=200)
print("wrote", png_path)
pgf_path = os.path.join(ROOT, "figures", "sandstone_comparison.pgf")
FigureCanvasPgf(fig).print_pgf(pgf_path)
print("wrote", pgf_path)
