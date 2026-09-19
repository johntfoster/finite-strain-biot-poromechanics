#!/usr/bin/env python3
"""Symbolic (SymPy) check of the closed-form Biot coefficient.

Verifies, symbolically, the fixed-pressure tangent chain that produces the
closed-form Biot coefficient in
``paper/sections/finite_deformation_biot.tex``:

  * implicit differentiation of ``eq:verification-mineral-factors``;
  * the volume tangent in ``eq:solid-density-eos-tangent``;
  * the coefficient in ``eq:poroplastic-biot-correction`` and its
    single-fraction form;
  * the solid-volume-fraction and porosity forms in
    ``eq:biot-solid-volume-fraction-form`` and ``eq:biot-porosity-form``;
  * the reference limit ``B0 = 1 - K/K_s`` and drained path ``B(J,0)``;
  * supplementary mixed-derivative and compatibility identities implied by
    ``eq:verification-mineral-factors`` and ``eq:total-stress-pressure-tangent``.

The numbered check identifiers below retain their original meanings.

This is a symbolic companion to the numerical standard-library check in
``check_stress_trace_derivation.py``.  It requires SymPy, which is provided by
the MOOSE conda environment; run with::

    agent_environment/skills/setup-moose-conda/scripts/moose_conda_env.sh run -- \
        python3 validation/scripts/check_stress_trace_biot_fraction.py
"""

from __future__ import annotations

import json
import sys

import sympy as sp


def require(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(f"{name}: symbolic identity does not hold")


def zero(name: str, expression) -> None:
    require(name, sp.simplify(expression) == 0)


def main() -> int:
    # Symbols. K, K_s, phi_s0, J, Jbar are positive; pore pressure p may be
    # tensile (negative), so no sign assumption is placed on p.
    K, Ks, phi_s0, p, J, Jbar = sp.symbols("K K_s phi_s0 p J Jbar", real=True)
    alpha = 1 - K / (phi_s0 * Ks)  # 1 - K/(phi_s0 K_s)

    # eq:verification-mineral-factors: scalar residual R(Jbar, J, p) = 0.
    R = Ks * sp.log(Jbar) + alpha * p * Jbar - (K / phi_s0) * sp.log(J)

    # eq:solid-pressure-implicit-tangent: differentiation at fixed p.
    #   (dR/dJbar)(dJbar/dJ) + dR/dJ = 0  =>  [K_s/Jbar + alpha p] dJbar/dJ = K/(phi_s0 J)
    dR_dJbar = sp.diff(R, Jbar)
    dR_dJ = sp.diff(R, J)
    zero("eq88_bracket", dR_dJbar - (Ks / Jbar + alpha * p))
    zero("eq88_rhs", -dR_dJ - K / (phi_s0 * J))

    # eq:solid-density-eos-tangent: explicit volume tangent.
    dJbar_dJ = sp.simplify((K / (phi_s0 * J)) / (Ks / Jbar + alpha * p))
    zero("eq89_tangent", dJbar_dJ - K * Jbar / (phi_s0 * J * (Ks + alpha * p * Jbar)))

    # eq:poroplastic-biot-correction: B = 1 - phi_s0 dJbar/dJ.
    B_closed = sp.simplify(1 - phi_s0 * dJbar_dJ)
    zero("eq90_closed_form", B_closed - (1 - K * Jbar / (J * (Ks + alpha * p * Jbar))))

    # Equivalent single quotient; numerator < denominator on the stable branch.
    B_proper = (J * (Ks + alpha * p * Jbar) - K * Jbar) / (J * (Ks + alpha * p * Jbar))
    zero("eq90_proper_fraction", B_closed - B_proper)
    num = sp.expand(J * (Ks + alpha * p * Jbar) - K * Jbar)
    den = sp.expand(J * (Ks + alpha * p * Jbar))
    zero("proper_deficit", sp.expand(den - num) - K * Jbar)

    # Eliminate mineral volume by solid mass, then use current/reference porosity.
    phi_s, phi, phi0 = sp.symbols("phi_s phi phi_0", real=True)
    solid_denominator = phi_s0**2 * Ks**2 + (phi_s0 * Ks - K) * p * J * phi_s
    B_solid = 1 - K * Ks * phi_s0 * phi_s / solid_denominator
    zero("solid_volume_fraction_form", B_closed.subs(Jbar, J * phi_s / phi_s0) - B_solid)
    porosity_denominator = (1 - phi0)**2 * Ks**2 + ((1 - phi0) * Ks - K) * p * J * (1 - phi)
    B_porosity = 1 - K * Ks * (1 - phi0) * (1 - phi) / porosity_denominator
    zero("porosity_form", B_solid.subs({phi_s: 1 - phi, phi_s0: 1 - phi0}) - B_porosity)
    zero("porosity_mineral_volume_equivalence", B_porosity.subs(
        {phi: 1 - phi_s0 * Jbar / J, phi0: 1 - phi_s0}) - B_closed)
    # On the manuscript's branch, denominator scaling is strictly positive.
    zero("fraction_denominator_scaling", solid_denominator.subs(
        phi_s, phi_s0 * Jbar / J) - phi_s0**2 * Ks * (Ks + alpha * p * Jbar))
    zero("porosity_reference_B0", B_porosity.subs({phi: phi0, J: 1, p: 0}) - (1 - K / Ks))
    zero("porosity_drained_form", B_porosity.subs(p, 0)
         - (1 - K * (1 - phi) / (Ks * (1 - phi0))))

    # Reference limit: B(J=1, Jbar=1, p=0) = 1 - K/K_s.
    B0 = sp.simplify(B_closed.subs({J: 1, Jbar: 1, p: 0}))
    zero("reference_B0", B0 - (1 - K / Ks))

    # Drained path: at p = 0, Jbar(J,0) = J^(K/(phi_s0 K_s)).
    exponent = K / (phi_s0 * Ks)
    B_drained = sp.simplify(B_closed.subs({p: 0, Jbar: J**exponent}))
    B_drained_expected = 1 - (K / Ks) * J ** (exponent - 1)
    zero("drained_path", B_drained - B_drained_expected)

    # eq:trace-mineral-pressure-tangent and supplementary Maxwell reciprocity:
    # the implicit-function theorem gives dJbar/dp = -(dR/dp)/(dR/dJbar).
    dR_dp = sp.diff(R, p)
    dJbar_dp = sp.simplify(-dR_dp / dR_dJbar)
    zero("compatible_mineral_pde", J * dJbar_dJ - (p + Ks / Jbar) * dJbar_dp - Jbar)

    mean_single_prime = phi_s0 / J * (p * Jbar + Ks * sp.log(Jbar))  # (1/3) tr sigma'
    d_mean_dp = sp.simplify(sp.diff(mean_single_prime, p) + sp.diff(mean_single_prime, Jbar) * dJbar_dp)
    zero("maxwell_reciprocity", d_mean_dp - phi_s0 * dJbar_dJ)

    # Freeze plastic distention while differentiating with respect to total J.
    ap = sp.symbols("a_p", positive=True)
    R_plastic = Ks * sp.log(Jbar) + alpha * p * Jbar - K / phi_s0 * sp.log(J / ap)
    plastic_tangent = -sp.diff(R_plastic, J) / sp.diff(R_plastic, Jbar)
    zero("fixed_plastic_volume_tangent", plastic_tangent - dJbar_dJ)
    zero("fixed_plastic_biot", 1 - phi_s0 * plastic_tangent - B_closed)

    # Independently invert the physical mass and density-form EOS residuals.
    rho, rho0, mass = sp.symbols("rho rho0 mass", positive=True)
    residuals = sp.Matrix([
        J * rho * phi_s - mass,
        sp.log(rho / rho0) + K / (phi_s0 * Ks) * sp.log(J / ap)
        - alpha * p * rho0 / (Ks * rho),
    ])
    state_tangent = -residuals.jacobian([rho, phi_s]).inv() * residuals.diff(J)
    density_tangent = -K * rho / (phi_s0 * J * (Ks + alpha * p * rho0 / rho))
    fraction_tangent = phi_s / J * (K / (phi_s0 * (Ks + alpha * p * rho0 / rho)) - 1)
    zero("two_state_density_tangent", state_tangent[0] - density_tangent)
    zero("two_state_fraction_tangent", state_tangent[1] - fraction_tangent)
    zero("two_state_biot", (1 + J * phi_s / rho * state_tangent[0]).subs(
        {phi_s: phi_s0 * rho0 / (J * rho)}).subs(rho, rho0 / Jbar) - B_closed)

    print(json.dumps(
        {
            "status": "PASS",
            "checks": [
                "eq88_bracket", "eq88_rhs", "eq89_tangent", "eq90_closed_form",
                "eq90_proper_fraction", "proper_deficit", "reference_B0",
                "solid_volume_fraction_form", "porosity_form",
                "porosity_mineral_volume_equivalence", "fraction_denominator_scaling",
                "porosity_reference_B0", "porosity_drained_form",
                "drained_path", "compatible_mineral_pde", "maxwell_reciprocity",
                "fixed_plastic_volume_tangent", "fixed_plastic_biot",
                "two_state_density_tangent", "two_state_fraction_tangent", "two_state_biot",
            ],
            "proper_fraction": sp.pretty(B_proper, use_unicode=False),
            "solid_volume_fraction_form": sp.sstr(B_solid),
            "porosity_form": sp.sstr(B_porosity),
        },
        indent=2,
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2, sort_keys=True))
        sys.exit(1)
