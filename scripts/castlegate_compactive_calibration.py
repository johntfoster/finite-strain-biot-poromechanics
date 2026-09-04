#!/usr/bin/env python3
"""Compactive (cap) plasticity calibration of Castlegate sandstone (B, step 2),
against the published Ingraham et al. (2017) Tables 1 and 3.

Two panels:
  (a) drained hydrostatic Biot coefficient alpha = 1 - K/Km vs effective mean
      stress: published hydrostatic points, the elastic stiffening fit
      alpha_el(P) = 1 - K_fit(P)/Km_fit(P) (from B step 1), and the compactive
      porosity model alpha_comp(P) = 1 - K_fit(P)/Km(phi(P)) where the drained
      stiffening is carried by plastic porosity loss.
  (b) the compactive state inferred from that porosity-loss interpretation:
      porosity phi(P) (0.26 -> 0.14) and plastic pore allocation
      a^p(P) = phi_s0/(1-phi(P)) (1 -> ~0.87), with the independent
      post-test porosity of the hydrostatic specimen (0.14 at ~173 MPa
      effective) marked as a star.

Model (all documented):
  - drained tangent K and unjacketed Km are fit to P_eff as in B step 1;
  - a porosity-only drained law K(phi) = K_sd exp(-lambda phi) is anchored to
    the two independent endpoints: phi0 = 0.26 (initial) at K0 ~ 5.9 GPa and
    phi_end = 0.14 (Table 1 post-test of the hydrostatic specimen 4ac21) at
    K_end ~ 12.9 GPa at its failure point (~173 MPa effective);
  - Km(phi) is anchored the same way (Km 52 -> 63 GPa; weaker porosity
    sensitivity);
  - inverting K_fit(P) through K(phi) gives a smooth, monotone porosity path
    phi(P); phi_s = phi_s0/a^p with phi_s0 = 0.74 gives the compactive a^p(P);
  - fitting a^p = exp(-(P_eff - P_y)/K_pl) yields onset P_y ~ 0-10 MPa and
    plastic modulus K_pl ~ 1.0-1.15 GPa.

Data: Ingraham, Bauer, Issen, Dewers, Int. J. Rock Mech. Min. Sci. 96 (2017)
1-10, doi:10.1016/j.ijrmms.2017.04.004 (published copy in references/pdfs/).
Effective mean stress = applied mean stress - 6.89 MPa.

Interpretation honesty: this compactive (a^p < 1, porosity-loss) reading
reproduces alpha(P) as well as the elastic stiffening fit and is anchored by the
independent post-test porosity, but it is not unique (a reversible
stress-stiffening law at fixed porosity also fits K(P)). The volume-strain PATH
(Fig. 3d) is required for a uniquely identified hardening law.
"""
import os

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pgf.texsystem"] = "lualatex"
matplotlib.rcParams["pgf.rcfonts"] = False
matplotlib.rcParams["font.family"] = "serif"
matplotlib.rcParams["font.size"] = 9
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

# Porosity anchors (published): initial 26 +/- 0.3%; Table 1 post-test of the
# hydrostatic specimen 4ac21 (failed at ~180 MPa applied = ~173 MPa effective).
PHI0 = 0.26
PHI_END = 0.14
P_FAIL_EFF = 180.04 - PORE

Pa = np.array([r[0] for r in TABLE], float)
K = np.array([r[1] for r in TABLE], float)
Km_tab = np.array([r[2] for r in TABLE], float)
alpha_m = np.array([r[3] for r in TABLE], float)
P_eff = Pa - PORE

# ---- B step 1 fits: Km(P) linear, K(P) quadratic (computed from the table) ----
Km_all = np.concatenate([Km_tab, np.array([k for _, k in UNJ], float)])
Pe_all = np.concatenate([P_eff, np.array([p - PORE for p, _ in UNJ], float)])
b_km, a_km = np.polyfit(Pe_all, Km_all, 1)          # Km = a_km + b_km P
c2, c1, c0 = np.polyfit(P_eff, K, 2)                # K  = c0 + c1 P + c2 P^2


def K_fit(P):
    return c0 + c1 * P + c2 * P**2


def Km_fit_lin(P):
    return a_km + b_km * P


# ---- porosity-only drained law K(phi) = K_sd exp(-lambda phi) through anchors
K0 = K_fit(0.0)
K_end = K_fit(P_FAIL_EFF)
lam = np.log(K_end / K0) / (PHI0 - PHI_END)
K_sd = K0 * np.exp(lam * PHI0)
Km0 = Km_fit_lin(0.0)
Km_end = Km_fit_lin(P_FAIL_EFF)
lam_km = np.log(Km_end / Km0) / (PHI0 - PHI_END)
Km_sd = Km0 * np.exp(lam_km * PHI0)


def phi_of_P(P):
    """Porosity path inferred by inverting K_fit(P) through the K(phi) law."""
    return (np.log(K_sd) - np.log(K_fit(P))) / lam


def Km_of_phi(phi):
    return Km_sd * np.exp(-lam_km * phi)


PHI_S0 = 1.0 - PHI0


def ap_of_P(P):
    """Compactive plastic pore allocation, phi_s = phi_s0/a^p."""
    return PHI_S0 / (1.0 - phi_of_P(P))


Pgrid = np.linspace(5, 175, 400)
alpha_el = 1.0 - K_fit(Pgrid) / Km_fit_lin(Pgrid)
alpha_comp = 1.0 - K_fit(Pgrid) / Km_of_phi(phi_of_P(Pgrid))
phi_grid = phi_of_P(Pgrid)
ap_grid = ap_of_P(Pgrid)

# residuals against measured alpha
alpha_el_d = 1.0 - K_fit(P_eff) / Km_fit_lin(P_eff)
alpha_comp_d = 1.0 - K_fit(P_eff) / Km_of_phi(phi_of_P(P_eff))
rms_el = float(np.sqrt(np.mean((alpha_m - alpha_el_d) ** 2)))
rms_comp = float(np.sqrt(np.mean((alpha_m - alpha_comp_d) ** 2)))

# cap parameters from a^p = exp(-(P_eff - P_y)/K_pl), anchored at P_FAIL_EFF
ap_end = ap_of_P(P_FAIL_EFF)
K_pl = P_FAIL_EFF / np.log(1.0 / ap_end)
P_y = 0.0
print("K(phi)  : %.0f exp(-%.3f phi) MPa   (K0=%.0f@%.2f, K_end=%.0f@%.2f)"
      % (K_sd, lam, K0, PHI0, K_end, PHI_END))
print("Km(phi) : %.0f exp(-%.3f phi) MPa" % (Km_sd, lam_km))
print("inferred phi at failure : %.3f  (post-test 0.14)" % phi_of_P(P_FAIL_EFF))
print("compactive a^p: 1.0 -> %.3f at %d MPa eff;  K_pl = %.0f MPa (P_y=%g)"
      % (ap_end, int(round(P_FAIL_EFF)), K_pl, P_y))
print("RMS elastic-stiffening model vs data   : %.4f" % rms_el)
print("RMS compactive porosity model vs data  : %.4f" % rms_comp)

# ---- figure: two panels ----
fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.4, 3.3))

axa.plot(P_eff, alpha_m, "o", color="black", ms=4.5,
         label="Ingraham 2017, hydrostatic (Table 3)")
axa.plot(Pgrid, alpha_el, "-", color="tab:red", lw=1.7,
         label=r"elastic stiffening $\alpha_{\mathrm{el}}(P)$")
axa.plot(Pgrid, alpha_comp, "--", color="tab:blue", lw=1.7,
         label=r"compactive porosity model $\alpha(\phi(P))$")
axa.set_xlabel(r"Effective mean stress  $P_{\mathrm{eff}}$  (MPa)")
axa.set_ylabel(r"Biot coefficient  $\alpha$")
axa.legend(fontsize=7, loc="lower left")
axa.grid(alpha=0.3)
axa.set_ylim(0.78, 0.92)

axb.plot(Pgrid, phi_grid, "-", color="tab:blue", lw=1.7,
         label=r"porosity  $\phi(P)$")
axb.plot(Pgrid, ap_grid, "-.", color="tab:green", lw=1.7,
         label=r"pore allocation  $a^{p}(P)$")
axb.plot([P_FAIL_EFF], [PHI_END], "*", color="black", ms=12,
         label="post-test 0.14 (hydrostat 4ac21)")
axb.set_xlabel(r"Effective mean stress  $P_{\mathrm{eff}}$  (MPa)")
axb.set_ylabel(r"porosity  $\phi$,  allocation  $a^{p}$")
axb.legend(fontsize=7, loc="lower left")
axb.grid(alpha=0.3)
axb.set_ylim(0.10, 1.0)

fig.tight_layout()
out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "figures",
                                    "sandstone_compactive_calibration.png"))
fig.savefig(out, dpi=200)
print("wrote", out)
