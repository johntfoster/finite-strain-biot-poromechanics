# Coupled poroplastic Mandel verification

The compression test uses the Mandel quarter-domain, Q2 displacement,
continuous Q1 water pressure, and Q2 solid partial density. The platen reaches
10% axial compression in 0.2 s and remains fixed to 0.7 s. The plastic law has
friction slope 0.6, dilation slope 0.4, initial cohesion 20 MPa, and
isotropic hardening modulus 100 MPa. Elastic moduli,
initial solid fraction, and fluid properties match the elastic continuation.

`ADPoroplasticPoreVolumeMaterial` differentiates the scalar mineral equation
using the total-volume rate, pressure rate, and logarithmic plastic-distention
increment. The solved solid partial density supplies solid volume fraction.
`ADBiotPressureStorageMaterial` consumes that fraction and its complete rate.
The material-point coefficient and the virgin elastic comparator both use the
same current pressure and total volume; their difference isolates plastic
history. This comparison does not subtract two different boundary-value
solutions.

The return mapping solves local values with scalar forward derivatives, then
recovers the global AD derivatives by the implicit-function theorem. Previous
plastic history is fixed during this derivative. The independent material-point
checks and the existing active-plastic PETSc regression cover this change.
A nonpositive current trial volume is a recoverable domain error for Newton
backtracking. A nonpositive stored plastic volume remains a fatal error.

The coupled Jacobian diagnostic scales stiffness and pressure together, uses
a temporal predictor with factor 0.9, and sets PETSc's finite-difference error
parameter to 1e-9. Every Jacobian assembled along the diagnostic path is checked
against the unchanged relative 1e-7 and absolute 1e-5 limits. At a yield switch,
a perturbation can enter a different branch; a single smooth Jacobian cannot
represent both sides. An unpredicted first guess at the start of the hold
exhibited this branch mismatch. The predictor avoids that exact switching
state while the test still spans compression and the full hold.

Water-mass change is compared both with integrated Darcy flux at the drained
face and with the assembled pressure-boundary reaction. The latter sums only
actual pressure degrees of freedom: a generic nodal sum would also count Q1
interpolated values at the QUAD9 midside geometry nodes. Water accumulation is
a chain-rule rate, so its integrated rate differs from a backward difference
of the complete nonlinear mass at finite step. The temporal study measures
that drift. Boundary-gradient flux has a separate spatial discretization error.

The synthetic water EOS is continued into tension. Cavitation, desaturation,
material calibration, and experimental validation are outside this test.

The publication run uses a 40 × 4 mesh, a uniform 0.0025 s backward-Euler step,
and Newton backtracking with the temporal predictor. It reaches the final time
without step reductions. The complete verification record includes all run
commands, discretizations, source hashes, and the framework and Conda versions.

The final reference-volume average of B − B_el is 0.00723269. At a common
0.0025 s step, its maximum difference between the 20 × 2 and 40 × 4 meshes over
the history is 3.91e-7. The final RMS difference between local piecewise-constant
element-average fields is 8.25e-6, and the maximum difference is 1.85e-5.
The six-panel figure plots element-averaged B, including plasticity, divided by
the constant reference coefficient B0 = 1 − K/Ks = 0.6, using the same viridis scale, limits (0.965, 1.02), panel dimensions, and
colorbar placement as the elastic B/B0 figure. A ratio of one marks the reference
coefficient. The same-state elastic comparator is retained in the history plot
and numerical diagnostics. The raw values are not smoothed.

For the fine-grid run, the maximum mass mismatch against integrated Darcy
outflow is 0.291% of initial water mass. The boundary-reaction comparison gives
0.0445%. On the fixed 20 × 2 grid, halving the time step twice reduces reaction
mass drift from 0.178% to 0.0890% and 0.0446%, with a corresponding decrease in
solid-mass drift. These are implementation and numerical-sensitivity checks;
they do not establish physical validation.

## Mineral branch and late-time spatial variation

`python3 validation/scripts/diagnose_poroplastic_contours.py` audits the saved
Exodus fields and writes `.agent-runtime/poroplastic-mandel/contour_diagnostics.json`.
The diagnostic checks the verified source hashes and records the hashes of the
four Exodus files it reads. It does not run a new simulation or change an
acceptance threshold.

The material calls `matchedLogMineralVolume` with elastic volume J/a_p. At
negative pressure the solver brackets log(mineral volume) between its
zero-pressure value and the zero-tangent turning point. It therefore selects
the root continuously connected to zero pressure and enforces a positive
derivative after AD polishing. The same solver evaluates the elastic comparator.
It also enforces mineral volume below e. For Q1 pressure on these reference
rectangles, the nodal pressure minimum bounds the quadrature-point pressure.
Combining these bounds gives a conservative lower bound on the normalized
mineral tangent, 1 + (1 − K/(phi_s0 Ks)) p z/Ks, without treating element
averages as pointwise constitutive states. In the original zero-hardening run the minimum
pressure is −28.530 MPa and this tangent is bounded below by 0.982766.
The mineral-root turning point is therefore remote from the accepted states.

The spatial diagnostic computes the RMS unscaled second difference along X
and the RMS departure from each column's mean over Y. These are descriptive
measures, not convergence norms or eigenvalue stability tests. For the original zero-hardening case at 0.7 s, the
second difference of B − B_el is 6.87e-6 on the 20 × 2 mesh and 6.93e-4 on
the 40 × 4 mesh at the same time step. On the latter mesh, the transverse
departure grows from 1.76e-7 at 0.3 s to 2.87e-4 at 0.5 s and 4.59e-4 at
0.7 s. Plastic distention and the plastic multiplier increment also develop
transverse variation. Thus the late panels show variation in the computed
plastic state, rather than a color interpolation artifact. Correct mineral
branch selection and a passing residual Jacobian test do not establish
stability of the coupled spatial solution.

The acoustic-tensor audit identifies loss of ellipticity in the original
perfectly plastic response before the pronounced late-time pattern. The
approved isotropic hardening law increases cohesion with accumulated plastic
multiplier inside the same local return. Existing zero-hardening tests remain
in place. On the corrected fine grid, the maximum transverse RMS variation of
B − B_el is 2.34e-16 over the saved history. Its final unscaled second difference
along X is 1.15e-6, compared with 4.06e-6 on the corrected coarse grid.
The minimum sampled fixed-pressure acoustic determinant is 0.03797 GPa^2.
Halving the fine-grid time step to 0.00125 s retains transverse variation below
7.4e-16 and a positive sampled acoustic minimum of 0.03795 GPa^2. The maximum
coefficient-contrast difference over the six snapshots is 3.85e-6.

See [the spatial-stability audit](poroplastic_spatial_stability.md) for the
independent replay, root-selection check, hardening implementation, controlled
comparisons, and scope of the stability evidence. The hardening modulus is a
synthetic constitutive choice; neither smoothing nor pressure stabilization is
used to remove the pattern.
