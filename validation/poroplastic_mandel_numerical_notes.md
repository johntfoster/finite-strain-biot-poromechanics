# Coupled poroplastic Mandel verification

The compression test uses the Mandel quarter-domain with Q2 displacement and
continuous Q1 water pressure. Solid partial density equals its reference value
divided by the total Jacobian at every quadrature point. The platen reaches
10% axial compression in 0.2 s and remains fixed to 0.7 s. Friction slope is
0.6, dilation slope is 0.4, initial cohesion is 20 MPa, and the isotropic
hardening modulus is 100 MPa. Elastic moduli, initial solid fraction, and fluid
properties equal those of the elastic continuation.

`ReferenceMomentum` and `ReferenceFluidMass` assemble the total first Piola
stress and the backward difference of complete fluid mass, respectively.
`ADReferenceBalanceState` connects the existing constitutive properties to
these common kernels. The current mineral and plastic states enter the mass
and retain their outer automatic-differentiation derivatives. Solid density
is eliminated using source-free solid conservation. Previous fluid mass is a
stateful quadrature-point property initialized from the actual initial fields
and prescribed plastic history.

The continuous mineral-volume and fluid-storage rates remain independent
diagnostics. They do not supply the time-discrete fluid residual. The storage
check solves perturbed mineral states independently and separately verifies
the full finite-step mass difference. Its maximum normalized discrete-storage
error is 6.62e-12, compared with a
2e-10 limit. It exercises
807 active-plastic quadrature-point samples.

The coupled PETSc comparison uses unit-scaled stiffness and pressure and a
0.9 temporal predictor to avoid evaluating a derivative exactly at a yield
switch. A perturbation study brackets truncation and subtraction roundoff;
3e-10 gives a maximum relative Jacobian difference of
5.54e-08 and an absolute difference of
3.47e-07 across 49 comparisons.
The acceptance limits remain 1e-7 and 1e-5. See
[the perturbation study](conservative_jacobian_perturbations.json).

The publication mesh is 40 × 4 with a 0.0025 s backward-Euler step. The final
reference-volume average of B − B_el is 0.007231903.
At the same step, its maximum history difference between the 20 × 2 and 40 × 4
meshes is 3.91e-07.
The final local element-average field difference has RMS 8.26e-06 and
maximum 1.84e-05. The six-panel figure plots B/B0 with B0 = 0.6,
using the same scale and panel layout as the elastic figure. Raw element
averages are plotted without smoothing.

The pressure-boundary reaction sums only actual pressure degrees of freedom.
Integrated reaction and total fluid-mass change agree within 2.0e-12 of the
initial fluid mass across all five mesh/time cases. The storage differences
telescope within 5.1e-14, and the largest solid reference-mass L2 residual
is 2.2e-17. These checks enforce conservation separately on every mesh and
time step. They do not require a nonzero defect to decrease monotonically.
Direct integration of the boundary-gradient Darcy flux has a separate spatial
discretization error: the publication run's maximum mismatch is
0.3363% of initial fluid mass.

The return mapping and its local constitutive equations are unchanged.
Independent material-point tests verify flow, hardening, mineral equilibrium,
stress transformations, and their derivatives. Suppressing yielding recovers
the elastic coupled solution within 1.2e-13
in the normalized pressure, displacement, and coefficient comparisons.

[The verification record](poroplastic_mandel_verification.json) contains run
commands, source hashes, discretizations, environment evidence and all
acceptance checks. [The spatial-stability audit](poroplastic_spatial_stability.md)
reports the separate acoustic replay and zero-hardening controls.
The single-phase water EOS is continued into tension; cavitation,
desaturation, material calibration, and experimental validation are outside
this synthetic test.
