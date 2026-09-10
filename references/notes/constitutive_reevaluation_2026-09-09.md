# Constitutive reevaluation

The open reduction identified below is resolved in
`mixture_reduction_reconciliation_2026-09-09.md`. That derivation also corrects
the tensor-versus-scalar distention distinction in item 3 below.

Scope: reassess the solid energy and its connection to mixture theory. This
record proposes a candidate for further derivation; it does not replace the
manuscript model or validate new numerical results.

## Source findings

The current multicomponent reactive-flow manuscript, *A thermodynamically
consistent theory of multicomponent porous media: finite-deformation mechanics,
compositional flow, electrostatics, reactions, and phase transformations*, uses
the solid state `(Fbar_e, A_e, rho_bar, composition, temperature)`.
Source: `sections/multicomponent_solids.tex`, labels
`eq:MC_state_sets`, `eq:MC_solid_general_free_energy`,
`eq:MC_solid_density_rate`, `eq:MC_solid_pressure_definition`,
`eq:MC_solid_stress_definition`, and `eq:MC_distension_force_definition`.
The available compiled PDF confirms pressure, material stress, and distention
restrictions in equations (165b), (166), and (168), respectively.

Without electrical effects, pressure is the density derivative with the other
members of that state fixed. Material stress and the distention derivative
must also satisfy the reversible restrictions. The theory does not prescribe
a neo-Hookean model or determine a numerical mineral law without an energy
closure. Its density derivative at fixed true deformation and distention must
not be identified without a chain rule with the present manuscript's derivative
at fixed aggregate deformation.

The separate local PDF `references/pdfs/reacting-mixture-main.pdf`, dated
June 1, 2026, assumes incompressible minerals. Section 3, equations (16)--(18),
sets true volume to unity and separates isochoric and distention energy.
Section 3.1, equations (24)--(25), prescribes a neo-Hookean isochoric part and
a porosity-dependent distention energy. Its conclusions explicitly restrict
the model to B = 1. This is not the general multicomponent manuscript above,
and is not a compressible-mineral replacement for the present model.

Foster and Xu, local PDF
`references/pdfs/foster-xu-2025-revisiting-finite-deformation-poromechanics.pdf`,
equations (27c) and (32)--(36), supports the density conjugacy and Legendre
transformation in aggregate deformation/specific-volume coordinates. Those
identities do not select a constitutive energy.

## Consequences for the proposed simplification

1. A density-independent neo-Hookean energy of aggregate elastic deformation
   alone gives zero density-conjugate pressure under the current manuscript's
   independent-variable convention.
2. Appending a density-only mineral energy permits nonzero pressure, but makes
   mineral volume independent of aggregate volume at fixed pressure, yielding
   B = 1 under the current definition.
3. A neo-Hookean energy of true elastic deformation alone cannot simply be
   inserted into the multicomponent restrictions: it has neither explicit
   density dependence nor distention dependence, and the latter restriction
   would eliminate the material stress if imposed for arbitrary tensor
   distention rates. For spherical distention only its trace restriction
   applies, so a density- and distention-independent isochoric energy can
   carry deviatoric stress. It still supplies no pore-pressure or volumetric
   closure. A constrained reduction requires explicit justification.
4. The existing reference-volume construction is optional. It enforces a
   selected pressure law and a selected drained energy; it is not forced by
   mixture theory.

## Candidate in the current reduced coordinates

For spherical elastic distention, set a_e = J_e/Jbar and retain the existing
isochoric plastic assumption. Consider, per reference mixture volume,

\[
W_s=\frac{G}{2}[(J^e)^{-2/3}I_1^e-3]
 +\frac{k_a}{2}[\ln(J^e/\bar J)]^2
 +\frac{\phi_{s0}K_s}{2}(\ln\bar J)^2.
\]

Here k_a is a proposed elastic distention modulus, not the drained bulk
modulus K. These are familiar isochoric and logarithmic volume energy forms,
but their assembly is a proposed closure, not a verified literature model.
The energy has its reference at J_e = Jbar = 1 without a deformation-dependent
reference-volume function.

Using the present reduced density conjugacy at fixed F_e gives

\[
p=\frac{k_a\ln(J^e/\bar J)-\phi_{s0}K_s\ln\bar J}
        {\phi_{s0}\bar J}.
\]

At fixed plastic state, J_e = J/a_p. The implicit mineral-volume tangent is

\[
\left.\frac{\partial\bar J}{\partial J}\right|_{p,a_p}
=\frac{k_a\bar J}{J[k_a+\phi_{s0}K_s+\phi_{s0}p\bar J]}.
\]

The coefficient is one minus phi_s0 times this derivative. The denominator
must remain nonzero; positivity is immediate for positive moduli and p >= 0,
but global admissibility at tensile pore pressure has not been established.
The reference drained bulk modulus and coefficient are

\[
K=\frac{k_a\phi_{s0}K_s}{k_a+\phi_{s0}K_s},\qquad
B_0=1-\frac{K}{K_s}.
\]

To retain a prescribed K, choose
`k_a = K phi_s0 K_s / (phi_s0 K_s - K)`, requiring K < phi_s0 K_s.
With the existing K = 1 GPa, K_s = 2.5 GPa, phi_s0 = 0.9,
k_a = 1.8 GPa and B_0 = 0.6. This agreement is a reference-limit check;
the finite-deformation response differs from the current model.

A numerical centered-difference check at J = 0.92, a_p = 1.04,
p = 0.12 GPa, using these moduli, returned pressure
0.120000000009 GPa from the energy derivative and a mineral-volume tangent
0.435606598792 versus analytical 0.435606598737, with step 1e-6.
This checks the scalar algebra only, not a MOOSE implementation or the full
multicomponent reduction.

## Required work before adoption

Derive the constrained change of constitutive arguments from the multicomponent
state to `(F_e, Jbar)` and account for both reversible deformation and
distention restrictions. Then derive total stress, the plastic driving force,
and dissipation from the same potential. In particular, do not assume that
retaining the present yield law guarantees the same thermodynamic meaning
after changing the energy.

If adopted, the new pressure residual, its implicit tangent, material stress,
water storage linearization, and Mandel analytical parameters must be updated
together. Recompute the constitutive, Jacobian, Mandel, and plastic-history
checks and their publication figures. The old results cannot support the new
closure merely because its reference Biot coefficient agrees.

Recommendation: remove the reference-volume construction only as part of this
constitutive replacement. A standard neo-Hookean shear model with explicit
mineral and distention volume energies is a clearer candidate, but a complete
mixture-theory specialization remains to be demonstrated. If incompressible
minerals are intended instead, the simpler B = 1 model changes the paper's
central objective of evaluating an evolving compressible-mineral coefficient.
