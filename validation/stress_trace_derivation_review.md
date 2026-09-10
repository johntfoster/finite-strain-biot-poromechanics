# Stress-trace constitutive derivation

The selected elastic construction uses matched logarithmic Cauchy laws: the
drained double-prime mean stress is `K ln(J)/J`, and mechanical grain pressure
is `-K_s ln(barJ)/barJ`. The trace relation, pressure Legendre conjugacies,
and solid mass identity determine its finite-pressure extension. The closed-form result and fixed-plastic-state extension are in
`paper/sections/finite_deformation_biot.tex`; the supporting stress-trace
construction is in `paper/sections/stress_trace_biot_appendix.tex`.

## Constitutive alternatives examined

| Skeleton and mineral choices | Result | Assessment |
| --- | --- | --- |
| Drained `K ln(J)/J`; grain pressure `-K_s ln(barJ)` | Compatible characteristic construction with an implicit scalar closure | Valid near reference, but the exact continuation is cumbersome. The stress forms are not matched. |
| Double-prime mean `K (1 - 1/J)`; grain pressure `K_s (1/barJ - 1)` | Explicit mineral volume and constant `B = 1 - K/K_s` | Compatible baseline, but the stress laws are not logarithmic and the coefficient is constant. |
| Relative-volume logarithmic law; grain pressure `-K_s ln(barJ)` | Explicit tangent from a scalar mineral residual | Compatible, but its natural starting point is a single-prime stress law. |
| Rational packing law; grain pressure `K_s (1/barJ - 1)` | Explicit state and `B = 1 - (K/K_s)(barJ/J)^2` | Compatible and nonlinear, but less readily motivated and not logarithmic. |
| Drained `K ln(J)/J`; grain pressure `K_s (1/barJ - 1)` | Explicit state and `B = 1 - K/[J(K_s+p)]` | Clear compatible alternative, but it fails the requirement for matched logarithmic stress laws. |
| Drained `K ln(J)/J`; grain pressure `-K_s ln(barJ)/barJ` | Scalar mineral residual, implicit tangent, and reconstructed double-prime stress | Selected. Both stress laws have the same logarithmic Cauchy form, and the state fits the existing two-unknown implicit formulation. |

Three independent derivation reviews examined the trace, stress measures,
constitutive alternatives, and energy compatibility. Their common conclusion
supports the selected construction on a local admissible elastic branch.

## Verified identities

The reference data are `barJ(1,0)=1` and the entire drained skeleton stress
curve. The reference tangent is `B_0=1-K/K_s`; it is not an independently
prescribed boundary value for every pressure. The finite-pressure skeleton
law contains a derived correction that is quadratic near reference; the
prescribed drained law remains exact at every admissible drained volume.

The scalar residual is

```text
K_s ln(barJ) + (1-K/(phi_s0 K_s)) p barJ - (K/phi_s0) ln(J) = 0.
```

Its derivative gives the same coefficient as the two-state density/fraction
Jacobian. The reduced energy generates the double-prime stress. Adding
`phi_s0 p barJ` gives the pressure Legendre potential, which generates the
single-prime stress and the mineral volume. Symbolic differentiation verified
these conjugacies, the reciprocal relation, the grain trace, and the
characteristic invariant relation. No term involving changes in `B` or the
solid fraction was suppressed.

Run the independent numerical verification with:

```sh
python3 validation/scripts/check_stress_trace_derivation.py
```

Run the symbolic verification (requires the MOOSE conda environment, which
provides SymPy):

```sh
agent_environment/skills/setup-moose-conda/scripts/moose_conda_env.sh run -- \
    python3 validation/scripts/check_stress_trace_biot_fraction.py
```

It verifies the fixed-pressure tangent chain from the scalar residual to the
closed-form coefficient, the
proper-fraction rewrite of the closed-form coefficient, the reference limit
`B_0 = 1 - K/K_s`, the drained path, and the Maxwell reciprocity.

The standard-library verifier brackets the stable scalar root in logarithmic
mineral volume. It checks 48 elastic states with two parameter sets, positive
and negative pore pressure, nonisotropic and sheared deformation, and superposed
rotations. It compares every Cauchy stress component with finite differences of
the corresponding energy, checks the Biot coefficient by finite differences
of the solved mineral volume, and verifies both rows of the implicit state
Jacobian. It also checks the phase stress trace, mass identity, reciprocity,
pressure conjugacies, drained law, and reference storage. Separate unjacketed
paths verify equal grain/fluid pressure, constant solid fraction, and
hydrostatic total stress. All checks passed; the largest normalized discrepancy
was below `3e-12` in the development run.

## Scope and material restrictions

`K_s` is the reference grain modulus. Its current value for this EOS is
`K_s (1-ln(barJ))/barJ`. Physical states require positive skeleton/mineral
volume and a solid fraction strictly between zero and one. Positive mineral
stiffness requires `barJ < exp(1)`. The stable density-elimination branch requires
`K_s + (1-K/(phi_s0 K_s)) p barJ > 0`, with `0<K<phi_s0 K_s`.
For nonnegative pore pressure the positive root is unique. Tensile pressure
requires continuation on the branch connected to the drained state; global
existence is not asserted.

The fixed-plastic-state extension replaces `ln(J)` in the mineral residual
by `ln(J/a_p)`, while the closed coefficient retains total `J` in its
denominator. The numerical verifier also checks 36 such states. Production
MOOSE materials now solve the scalar root and evaluate the closed coefficient;
the general implicit material remains an independent diagnostic. Implementation
and benchmark evidence is recorded separately in the curated validation reports.
These checks do not establish global finite-strain stability or physical
calibration.
