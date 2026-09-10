# Reconciliation with the multicomponent theory

This derivation supersedes the unresolved reduction in
`constitutive_reevaluation_2026-09-09.md`. It establishes a sufficient
specialization of the source theory, not a new claim that the source uniquely
selects an elastic energy. No numerical material or manuscript result is
changed by this audit.

## Source and assumptions

Source: *A thermodynamically consistent theory of multicomponent porous media:
finite-deformation mechanics, compositional flow, electrostatics, reactions,
and phase transformations*, canonical `main.tex`, `defs.tex`, and
`sections/multicomponent_solids.tex`, inspected September 9, 2026.
The source's available PDF confirms the pressure, stress, and tensor
distention restrictions in (165b), (166), and (168). The scalar-distention
specialization is essential: use its trace restriction, not a tensor equality
for arbitrary distention rates after restricting distention to spherical motion.

Retain one solid and one fluid; fix composition and temperature; set reaction,
electrical, and interfacial contributions to zero. Set the stress-free factors
to identity. Assume spherical elastic and plastic distention and isochoric
true-plastic flow. These choices are contained in the source's scalar
distention and nonreacting specializations.

Source anchors:

| Role | Source label in `sections/multicomponent_solids.tex` |
| --- | --- |
| Independent energy arguments | `eq:MC_state_sets`, `eq:MC_solid_general_free_energy` |
| True mass and distention | `eq:MC_solid_true_mass_conservation`, `eq:MC_solid_distension_mass_relation` |
| Pressure | `eq:MC_solid_pressure_definition` |
| Partial material stress | `eq:MC_scalar_distension_solid_stress` |
| Elastic distention | `eq:MC_scalar_distension_stress_restriction` |
| Equivalent pressure | `eq:MC_solid_volume_fraction_restriction`, `eq:MC_fluid_volume_fraction_restriction` |
| Legendre transformation | `eq:MC_phase_pressure_specific_volume`, `eq:MC_phase_legendre_transform` |
| Plastic powers | `eq:MC_residual_dissipation`, `eq:MC_scalar_plastic_distension_power` |

## 1. A sufficient energy specialization

Let b denote the source's true elastic deformation Fbar_e in this note,
and a_e its scalar elastic distention. The source state retains b, a_e,
and intrinsic density r as distinct constitutive arguments. Introduce
F_e = a_e^(1/3) b and j = rho_bar_s0/r as dependent arguments and choose

\[
\psi_s(b,a_e,r)=\rho_{s0}^{-1}W(F_e,j),\qquad
\rho_{s0}=\phi_{s0}\bar\rho_{s0}.
\tag{R1}
\]

This product dependence is a constitutive specialization inside the source
state space. It does not eliminate a_e or r before taking the source
derivatives. On physical states, true mass conservation gives j = det(b),
so J_e = a_e j and J = a_p J_e. The equation j = det(b) is imposed on states,
not used to replace independent constitutive arguments before differentiation.
All energies W are per reference mixture volume.

## 2. Pressure follows with the correct held-fixed arguments

At fixed b and a_e, F_e is fixed and dj/dr = -j/r. Therefore the source
pressure restriction gives

\[
p=\bar p_s=\bar p_f
=r^2\psi_{s,r}\big|_{b,a_e}
=-\frac{1}{\phi_{s0}}W_{,j}\big|_{F_e}.
\tag{R2}
\]

The pressure equality follows from the source volume-fraction restrictions
after electrical and interfacial terms are suppressed. This establishes the
present paper's density conjugacy under R1. It is not a general license to
exchange held-fixed arguments for arbitrary source energies.

## 3. Material stress and elastic distention agree identically

The deformation chain rule gives

\[
\psi_{s,b}=\rho_{s0}^{-1}a_e^{1/3}W_{,F_e},\qquad
\sigma_s'=\frac{1}{J}W_{,F_e}F_e^T,
\tag{R3}
\]

where rho_s = rho_s0/J. The scalar distention derivative, evaluated at fixed
b and r, gives

\[
a_e\psi_{s,a_e}=\frac{1}{3\rho_{s0}}W_{,F_e}:F_e,
\qquad
\rho_s a_e\psi_{s,a_e}=\frac13\operatorname{tr}\sigma_s'.
\tag{R4}
\]

Thus the source's two mechanical restrictions give the same stress and its
mean. No additional distention residual is required for this product-dependent
energy. This also applies to the current manuscript energy: its unusual form
is optional, but the reduced coordinates themselves can be reconciled.

Why direct substitution previously looked inconsistent: at fixed aggregate
F_e, changing j changes both b and a_e, with
db/dj = b/(3j) and da_e/dj = -a_e/j. For a generic source energy,

\[
\frac{\partial(\rho_{s0}\psi_s)}{\partial j}\bigg|_{F_e}
=\frac{\rho_{s0}}{j}
 \left[\frac13\psi_{s,b}:b-a_e\psi_{s,a_e}-r\psi_{s,r}\right].
\tag{R5}
\]

The first two terms cancel by the scalar mechanical restrictions. For R1,
they cancel identically by the product chain rule. Omitting one term or
replacing j with det(b) before taking the source partial derivatives changes
the pressure relation.

## 4. Legendre transform and mixture stress

At fixed plastic state, solve R2 for j(F_e,p). Define W'' as W evaluated on
that state and W' = W'' + phi_s0 p j. Then

\[
P'=W_{,F_e}(F^p)^{-T},\qquad
P'=P''+\phi_{s0}p\,j_{,F}\big|_p.
\tag{R6}
\]

If the pressure law depends on deformation only through J at fixed plastic
state, j_,F = j_,J J F^(-T), and

\[
B=1-\phi_{s0}j_{,J}\big|_{p,F^p},\qquad
\sigma=\sigma_s'-pI=\sigma_s''-BpI.
\tag{R7}
\]

These are the current paper's definitions, now connected explicitly to the
source energy and scalar-distention restriction. If a chosen energy makes
the pressure depend on distortional invariants as well, a scalar B is not
generally sufficient; that extra isotropy assumption must be checked.

## 5. Plastic power

Write Fp = (a_p)^(1/3) Fbar_p, det(Fbar_p)=1, and tau' = J sigma_s'.
Multiplying the source's plastic power per current volume by J gives

\[
\mathcal D^p
=M:\left[\dot F^p(F^p)^{-1}\right],\qquad
M=(F^e)^T W_{,F_e}.
\tag{R8}
\]

The deviatoric true-plastic part is the contraction with dev(M), and the
scalar distention part is (tr(tau')/3) dot(a_p)/a_p. For an isotropic energy,
M is symmetric, tr(M)=tr(tau'), and
dev(M) = (F_e)^T dev(tau') (F_e)^(-T), matching the paper's S.
Consequently the existing smooth Drucker--Prager choice gives
D_p = dot(gamma)(q-beta p'), with p' = -tr(tau')/3, exactly as in the paper.
The source explicitly permits coupled nonassociated laws subject to combined
nonnegative plastic power; it does not uniquely prescribe this yield law.
The current parameter restrictions and smooth-branch qualification remain
necessary. This reconciliation does not establish apex or cap behavior.

## 6. Reconciled simple candidate

The candidate from the preceding note can be inserted into R1 as

\[
W(F_e,j)=\frac G2[(J_e)^{-2/3}I_1^e-3]
+\frac{k_a}{2}[\ln(J_e/j)]^2
+\frac{\phi_{s0}K_s}{2}(\ln j)^2.
\tag{R9}
\]

Here J_e means det(a_e^(1/3)b), while j means rho_bar_s0/r when taking source
partial derivatives. Only on physical states does J_e/j equal a_e.
Thus the middle term is a logarithmic distention energy on physical states,
but its full constitutive dependence must be retained to compute pressure.
A native-state energy written naively as a function of a_e alone in that term
would have different source partial derivatives and is not equivalent.

R2--R4 give

\[
p=\frac{k_a\ln(J_e/j)-\phi_{s0}K_s\ln j}{\phi_{s0}j},\qquad
\tau'=G(J_e)^{-2/3}\operatorname{dev}(F_eF_e^T)
+k_a\ln(J_e/j)I.
\tag{R10}
\]

Together with phase mass, these equations are a complete elastic local
specialization in the reduced variables; R8 supplies its plastic work
conjugacy. For this energy the pressure is purely volumetric, and

\[
j_{,J}\big|_{p,F^p}=\frac{k_a j}
 {J[k_a+\phi_{s0}K_s+\phi_{s0}pj]}.
\tag{R11}
\]

At the undeformed, virgin, zero-pressure state,

\[
K=\frac{k_a\phi_{s0}K_s}{k_a+\phi_{s0}K_s},\qquad
B_0=1-K/K_s.
\tag{R12}
\]

The fluid-storage linearization also changes. Since
j_,p = -phi_s0/(k_a+phi_s0 K_s) at the reference state,

\[
\left.\frac{\partial(J-\phi_{s0}j)}{\partial p}\right|_J
=\frac{\phi_{s0}^2}{k_a+\phi_{s0}K_s}
=\frac{B_0-\phi_{f0}}{K_s}.
\tag{R13}
\]

Adding water compressibility gives the classical single-mineral storage
combination (B0-phi_f0)/Ks + phi_f0/Kf as an algebraic reference limit.
This differs from the old manuscript's storage phi_s0/Ks + phi_f0/Kf.
Therefore Mandel timescales and the plotted solutions must be recomputed if
R9 replaces the present energy.

## Conclusion and remaining scope

Numerical verification differentiated the native-state energy in R1 and R9
with respect to all three principal true-elastic stretches, scalar elastic
distention, and intrinsic density. Three unequal-stretch states, using a
centered step of 1e-6, agreed with R2--R4 and R10 to a maximum absolute
discrepancy of 1.65e-10 in the chosen GPa normalization. The storage identity
R13 was also checked numerically. The tensor chain-rule derivation above
establishes the mapping; these scalar and principal-stretch checks are
independent arithmetic checks, not substitutes for a global Jacobian test.

The reduced energy, pressure, material stress, scalar-distention restriction,
Biot transform, and plastic power can be reconciled directly with the source
under the explicit product-dependence specialization R1. The candidate R9 is
one compatible constitutive choice, not a uniquely derived neo-Hookean model
from the source. No reference-volume function is required for it.

The mathematical reconciliation is complete for this scalar, isotropic,
nonreacting specialization. Numerical implementation, finite-deformation
admissibility over the intended loading range, and replacement of publication
results remain separate work. The source manuscript itself has not been
edited or audited outside the restrictions used here.
