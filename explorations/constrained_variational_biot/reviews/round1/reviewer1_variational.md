# Reviewer 1: variational and constitutive audit

## Recommendation

**Major revision.**  The central conclusion is promising and, at the level of
the locally condensed mineral state, essentially correct.  However, the paper
does not yet give a mathematically closed variational statement for the
two-field problem, and its asserted Darcy dissipation potential is not
consistent with the usual mass-flux/chemical-potential power pairing.

## Major findings

1. **The role of pressure in the mixed potential is incomplete.**  Equations
   (9)--(11), source lines 165--187, correctly use the envelope argument for
   differentiation with respect to `F` *if pressure is prescribed*.  But `p`
   is subsequently a global unknown in the claimed two-field problem
   (lines 199--229).  A free variation of the displayed `G` with respect to
   `p` gives `-(J-phi_s0 bar J)`, which is not the fluid mass balance and would
   incorrectly impose zero fluid volume.  Thus `G` alone is not a mixed
   variational principle for `(u,p)`.  The paper must either state precisely
   that (9) is a fixed-pressure mechanical potential only, or supply the
   time-incremental/saddle formulation in which mass balance (and the fluid
   free energy or chemical potential) makes pressure a legitimate multiplier
   or state variable.

2. **The Darcy claim needs the correct work conjugacy and density factor.**
   Lines 275--290 say that stationarity of (18) plus ``pressure-driven virtual
   power'' yields (15), but that virtual-power term is never written.  With
   mass flux `W_f`, physical dissipation is paired with the gradient of the
   chemical potential, `grad_X mu_f`; for a barotropic fluid at fixed
   temperature, `grad_X mu_f = F^{-T} grad_X p / bar rho_f` in the present
   convention.  The corresponding reference dissipation potential has
   coefficient `mu_f/(2 bar rho_f^2 kappa J)`, not the
   `mu_f/(2 bar rho_f kappa J)` in line 282.  Alternatively, the proposed
   coefficient produces (15) only if the added term is `W_f dot grad_X p`,
   which is not an energy-rate pairing for a *mass* flux.  Write the complete
   Onsager functional, state the force convention, and then vary it to recover
   (15).  Until then, the statement that (18) is a dissipation density is not
   supported.

3. **Stationarity, local minimum, and branch selection are conflated.**
   Lines 110--118 and 158--163 call `D>0` the ``stable mineral response.''
   At a root, the actual second variation is
   `Pi_s,barJbarJ = (phi_s0/c)(D/barJ)`, with
   `c=1-K/(phi_s0 K_s)>0`; the derivation must be shown.  Therefore `D>0`
   establishes a *strict local* minimum/nondegenerate implicit branch, not a
   global minimum or uniqueness at negative pressure.  The manuscript should
   specify continuation from the drained root (or another selection rule) and
   avoid calling every positive-`D` root ``the stable response.''

4. **The energy equivalence is asserted but not derivable from this paper.**
   The abstract and lines 139--163 say the matched logarithmic mineral residual
   is the stationarity equation of `Pi_s`, yet no matched `W_s(F,bar J)` is
   given.  Starting with an arbitrary `W_s` in line 139 cannot establish the
   claimed equivalence in lines 159--160.  Include the relevant volumetric
   energy, identify which deformation is held fixed (`F`, `F^e`, and the
   plastic state are currently interchanged; see lines 98--100, 123, and
   139--160), and show the one-line calculation from pressure conjugacy to
   `R=0`.  This is necessary for an exploratory paper whose purpose is the
   variational interpretation.

## Minor findings

1. In lines 172--186, say explicitly that the derivative along
   `bar J(F,p)` is a total derivative and invoke the envelope theorem.  The
   notation `partial G/partial F|_p` otherwise appears to hold `bar J` fixed,
   while the accompanying text says it is stationary.

2. The terminology around the stresses is imprecise in lines 175--183.
   `partial W_s/partial F|_barJ` is `P'`; `P''` is the derivative after
   solving the pressure relation at fixed `p`.  The equality to the total
   stress requires the explicitly stated identity
   `P' = P'' + (1-B)p J F^{-T}`, not merely the definition of `B`.

3. Equation (14), lines 223--225, retains a gravity body force, whereas the
   weak residual in lines 242--252 omits it while stating only that boundary
   terms are omitted.  Either set body force to zero before both equations or
   include its weak contribution.

## Required revisions

1. Distinguish fixed-pressure local condensation from a variational principle
   in which pressure is also varied; provide the latter or narrow the claim.
2. Replace (18) by a fully specified Onsager/virtual-power functional with
   correct flux-force pairing, and demonstrate its variation yields (15).
3. Provide the matched volumetric energy and derive `R=0`, its curvature, and
   the local branch-selection qualification.
4. Repair the stress definitions/transformation and the body-force mismatch.
