# Spatial oscillations in coupled poroplastic compression

## Diagnosis

The original synthetic test uses a Drucker–Prager law with friction slope 0.6,
dilation slope 0.4, constant cohesion 20 MPa, and no hardening. Its late-time
oscillations occur in the plastic state as well as in the Biot-coefficient
contrast. They are present in the raw element averages, before plotting.

The mineral root is selected correctly. `matchedLogMineralVolume` brackets the
root connected to the zero-pressure state and rejects nonpositive mineral
stiffness or tangent. Combining the original run's pressure minimum with the
enforced mineral-volume bound gives a conservative normalized mineral tangent
above 0.982766 throughout that run. This scalar stability condition does not
ensure stability of the plastic mechanical response.

`validation/scripts/check_poroplastic_acoustic.py` independently reconstructs
central quadrature-point deformation gradients and pressures from Q2/Q1 Exodus
histories. It replays the plastic history using a Lambert-W mineral solution,
a symmetric matrix exponential, and a seven-variable return mapping. On the
original material-sampling run, the maximum differences from MOOSE are below
5.1e-14 for the mineral-related coefficient, plastic volume, and total volume,
and below 6e-16 for the plastic increment. The replay also passes with positive
hardening. This comparison uses pointwise samples, not constitutive evaluation
of element-averaged inputs.

At a returned active state, the diagnostic differentiates the local equations
with previous history and pressure fixed. It uses the vanishing-increment
loading tangent, including the dependence of the plastic increment on total
deformation. For the first Piola stress P and deformation gradient F, write
A_iJkL = dP_iJ/dF_kL. An in-plane rank-one disturbance has acoustic tensor
Q_ik(n) = A_iJkL n_J n_L. The diagnostic scans reference normals at 0.25-degree
intervals. A change of sign of det(Q) between directions implies a singular
acoustic tensor at an intervening direction and loss of ellipticity. The
minimum eigenvalue of the symmetric part is recorded separately.

At the original fine-grid central sample (X = 0.5125 m, Y = 0.0375 m), the
minimum determinant changes from 0.0126832 GPa^2 at 0.2 s to −0.00787990 GPa^2
at 0.3 s. It reaches −0.00891130 GPa^2 at 0.4 s. Other directions retain
positive determinants. Halving the finite-difference perturbation changes
these minima by less than 2e-10 GPa^2. Thus the original constitutive response
loses ellipticity before the prominent 0.5 s and 0.7 s contour pattern.
The wider three-point scan gives a minimum of −0.00903897 GPa^2.

The original final-time transverse RMS variation of B − B_el is 4.58671e-4
on the 40 × 4 grid. Its unscaled second difference along X has RMS 6.93293e-4,
compared with 6.87334e-6 on the 20 × 2 grid at the same time step. Smooth
specimen averages and a correct residual Jacobian do not rule out this local
constitutive instability. The grid can select the spatial structure once the
homogeneous branch loses stability; the original contour pattern should not
be interpreted as a resolved physical localization band.

Halving the zero-hardening time step from 0.0025 s to 0.00125 s leaves
the maximum transverse RMS coefficient contrast at 4.48327e-4 and the final
X-direction second-difference RMS at 6.72205e-4. The minimum sampled acoustic
determinant remains negative, at −0.00913836 GPa^2. Time-step reduction alone
therefore does not remove the observed spatial instability.

## Constitutive change

The approved correction retains nonassociated flow and adds dissipative linear
isotropic hardening. Cohesion is c = c0 + H kappa^p, where kappa^p is the accumulated
plastic multiplier and dot(kappa^p) = gamma_dot. The current step uses
kappa^p_new = kappa^p_old + Delta_gamma inside the same implicit return mapping.
The stored energy and flow direction are unchanged. A zero hardening modulus
recovers the original perfect-plasticity model.

`ADImplicitPoroplasticBiotMaterial` stores the converged accumulated multiplier
as previous-step history and retains its current AD dependence through the
local consistency solve. The new parameter is `dp_hardening_modulus`, defaulting
to zero. The coupled compression deck selects H = 100 MPa, or 0.1 K, while the
publication material-point examples use the same cohesion and hardening
parameters. Separate zero-hardening regressions retain the limiting case. The
hardening modulus is a synthetic constitutive choice, not a numerical pressure
stabilization or a parameter calibrated from material data. It was selected
using the measured plastic-tangent deficit and is checked along the corrected
loading path.

No smoothing, pressure enrichment, artificial pressure diffusion, change of
finite-element spaces, or relaxation of existing verification tolerances is
part of this correction. The fixed-history Biot formula remains unchanged.

## Verification

The original material-point consistency and active AD Jacobian regressions pass.
Two additional regressions verify hardening under loading, unloading, reloading,
nonzero pressure, and an active AD Jacobian. Accumulated-multiplier errors are
below 1e-15. The coupled storage check passes its original tolerances; its
53 assembled Jacobian comparisons have maximum relative error 2.22086e-8 and
absolute error 2.71333e-6, below the unchanged 1e-7 and 1e-5 limits.

The corrected 20 × 2, 40 × 4, and half-time-step 40 × 4 runs are complete.
Their minimum sampled acoustic determinants are respectively 0.0380591,
0.0379669, and 0.0379504 GPa^2. On the 40 × 4 mesh, the maximum transverse RMS
variation of B − B_el is 2.34e-16 at the 0.0025 s step and 7.36e-16 at the
0.00125 s step. The largest local coefficient-contrast difference between these
time steps is 3.85e-6 across the six snapshots; the final-time maximum is
6.53e-7. Pressure and solved solid-density fields also retain transverse
uniformity to their numerical precision. The independent full publication
verification also passes. All six diagnostic histories reach 0.7 s, and the
complete comparison matrix passes its acceptance checks. The curated record
`validation/poroplastic_spatial_stability.json` contains the acoustic samples,
spatial metrics, refinement differences, configurations, and source hashes.

The associated-flow control sets beta = M = 0.6 with H = 0. Its minimum
sampled acoustic determinant is −0.00636518 GPa^2, with positive values in
other directions. Its maximum transverse RMS coefficient contrast is
2.48155e-4, and its final X-direction second-difference RMS is 3.98679e-4.
Changing the flow direction alone therefore does not remove the instability
on this coupled loading path. These controls identify the loss of ellipticity
of the tested perfectly plastic response; they do not attribute it solely to
nonassociation.

| Case | Minimum sampled det(Q), GPa^2 | Maximum transverse RMS of B − B_el |
| --- | ---: | ---: |
| Original, H = 0 | −0.00903897 | 4.58671e-4 |
| H = 0, half time step | −0.00913836 | 4.48327e-4 |
| H = 0, associated flow | −0.00636518 | 2.48155e-4 |
| H = 100 MPa, 20 × 2 | 0.0380591 | 3.70e-16 |
| H = 100 MPa, 40 × 4 | 0.0379669 | 2.34e-16 |
| H = 100 MPa, 40 × 4, half time step | 0.0379504 | 7.36e-16 |

The corrected fine/coarse final second-difference RMS ratio is 0.283, below
the 0.6 acceptance limit. The publication plots show B/B0, where B includes
plasticity and B0 = 1 − K/Ks = 0.6; B − B_el remains a diagnostic of plastic
history. Both six-panel figures use the same colors, limits, and panel sizes.
Runtime outputs remain under `.agent-runtime/poroplastic-mandel/`. Only
completed histories enter the accepted record.

## Reproduction

From the repository root, after building and verifying the MOOSE environment,
run the full comparison matrix with:

```sh
POROPLASTIC_MPI_RANKS=8 .agent/shared/skills/setup-moose-conda/scripts/moose_conda_env.sh run -- \
  python validation/scripts/check_poroplastic_spatial_stability.py --run --reuse --curate
```

This command runs the original zero-hardening model, its half-time-step and
associated-flow controls, and the corrected coarse, fine, and half-time-step
cases. Reuse requires a matching run signature and a completed history.
A separate publication regeneration uses:

```sh
POROPLASTIC_MPI_RANKS=8 make plastic-flow
make figures
make paper
make provenance
make validate
```

The ordinary material-point regressions retain zero-hardening controls; the
publication examples use H = 100 MPa. The additional
`implicit_plastic_hardening_history` and `implicit_plastic_hardening_jacobian`
regressions exercise the new constitutive option. The heavy
`poroplastic_spatial_stability` regression runs the comparison matrix without
changing the curated publication files.
