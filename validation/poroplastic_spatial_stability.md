# Constitutive stability in coupled poroplastic compression

The coupled calculations use Q2 displacement and continuous Q1 pressure, with
solid partial density determined by `rho_s = rho_s0/J`. Backward Euler
differences the complete reference water mass, including the converged plastic
state. The six histories in the [curated record](poroplastic_spatial_stability.json)
use this conservative formulation and reach 0.7 s. Their execution records
identify the input, executable, MPI command, and output hashes.

## Independent constitutive replay

[The acoustic diagnostic](scripts/check_poroplastic_acoustic.py) reconstructs
central quadrature-point deformation gradients and pressures from Q2/Q1 Exodus
histories. It replays plastic evolution with a Lambert-W mineral solution,
a symmetric matrix exponential, and a seven-variable return mapping.
A separate comparison against the fresh material samples in the storage run
checks this replay: maximum differences are 4.88e-15
for the Biot coefficient, 5.02e-14 for plastic
volume, 4.22e-14 for total volume, and
5.13e-16 for the plastic multiplier increment.
These are pointwise comparisons, rather than evaluations at averaged inputs.

At a returned active state, the diagnostic differentiates the constitutive
update while holding pressure and previous history fixed. Its vanishing-increment
loading tangent includes the plastic increment induced by further deformation.
For first Piola stress P and deformation gradient F, the tangent is
A_iJkL = dP_iJ/dF_kL. The in-plane acoustic tensor is
Q_ik(n) = A_iJkL n_J n_L. Reference normal directions are sampled every
0.25 degrees at three positions along the specimen. A change of sign of
det(Q) implies a singular acoustic tensor at an intervening direction.
Positive sampled values characterize this loading path, rather than establishing
stability at every possible state and direction. The diagnostic also repeats
the derivative calculation at half the finite-difference increment.

## Perfect plasticity and hardening

The perfectly plastic control has friction slope 0.6, dilation slope 0.4,
and cohesion 20 MPa. Its sampled determinant first changes sign at
0.2 s. The minimum is -0.00904082 GPa² at
0.5 s and (X, Y) = (0.1125, 0.0375) m.
The half-step and associated-flow controls examine time discretization and
the choice of flow direction separately. The associated control uses dilation
slope 0.6 and zero hardening. The tabulated transverse variation measures
spatial structure in the raw element averages of B − B_el; acoustic sign
changes and spatial variation are distinct diagnostics.

The hardening cases retain dilation slope 0.4 and use
c = c0 + H times the accumulated plastic multiplier, with H = 100 MPa.
The current plastic increment enters the same implicit consistency solve.
This is a synthetic constitutive choice; no material-specific calibration is
claimed. The minimum sampled determinant on the 40 × 4 mesh is
0.0379635 GPa². The scalar mineral equation's
local uniqueness is checked separately from this mechanical loading tangent.

| Case | Minimum sampled det(Q), GPa² | Maximum transverse RMS of B − B_el | Maximum relative reaction mass error |
| --- | ---: | ---: | ---: |
| H = 0 | -0.00904082 | 0.000459171 | 9.24372e-13 |
| H = 0, half time step | -0.00911466 | 0.000401425 | 3.28786e-12 |
| H = 0, associated flow | -0.00636678 | 0.000247744 | 8.99369e-13 |
| H = 100 MPa, 20 × 2 | 0.0380548 | 8.22055e-14 | 2.50888e-13 |
| H = 100 MPa, 40 × 4 | 0.0379635 | 8.62208e-15 | 8.54694e-13 |
| H = 100 MPa, 40 × 4, half time step | 0.0379488 | 4.50357e-13 | 4.04652e-12 |

## Refinement and conservation

For the hardening cases, the final-time coarse/fine differences in B − B_el
have RMS 8.26464e-06 and maximum 1.84454e-05 on the
common reference domain. Halving the fine-grid time step gives a largest
local difference of 2.48731e-06 over the six saved snapshots. The fine/coarse
ratio of final X-direction second-difference RMS is 0.282825, below the
retained 0.6 acceptance limit. Fields are reported as unsmoothed element averages.

The pressure-boundary reaction is integrated using the same end-step time
quadrature as the fluid residual. Its mass error is normalized by initial
water mass and is reported in the table. A boundary Darcy flux reconstructed
from pressure gradients has a separate spatial error; on the fine hardening
run its maximum normalized mismatch is
0.00336289.
Solid conservation is enforced pointwise, and its independently integrated
L2 diagnostic on that run is
1.8564e-17.

[The matrix driver](scripts/check_poroplastic_spatial_stability.py) checks
complete histories, acoustic signs, transverse structure, and mesh/time
sensitivity before curating results. The coupled storage and assembled-Jacobian
checks are recorded separately in
[the flow verification](poroplastic_mandel_verification.json).
The publication contours show B/B0; B − B_el isolates the effect of plastic
history at fixed current pressure and total volume. These calculations verify
and characterize the stated constitutive model; material-specific physical
validation remains future work.
