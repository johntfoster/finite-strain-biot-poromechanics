# Vision

This repository develops a reproducible paper on the numerical evaluation of a
finite-deformation Biot coefficient for a body containing one deformable solid
and one water phase. The global fields are Q2 displacement and continuous Q1 water pressure.
Solid mass conservation determines partial density as its reference value
divided by the deformation Jacobian. A local constitutive update supplies
intrinsic solid density, solid volume fraction, and any plastic internal variables.
Matched logarithmic skeleton and mineral laws permit analytical elimination of
the fixed-pressure implicit tangent, giving the Biot coefficient in closed form
in the current states. A scalar mineral solve and the active poroplastic return
mapping retain their automatic-differentiation dependencies. The independent
two-state implicit tangent and centered differences verify that expression. The
water balance uses a barotropic pressure--density equation of state. The Biot
transform maps the constitutive double-prime stress to the single-prime material
stress and total mixture stress, and all local dependencies remain inside the
automatic-differentiation graph used by the global MOOSE Newton solve.

The work has three coupled tracks:

1. **Manuscript and publication.** Present the finite-deformation solid-water
   equations, spatial phase-mass balances, general local update, elastic
   verification specialization, Biot stress
   transform, and automatic-differentiation implementation without reproducing
   the general multicomponent derivation.
2. **Implementation and verification.** Maintain a minimal MOOSE application
   with Q2 displacement, continuous Q1 water pressure, pointwise solid mass
   conservation, conservative water storage, the mineral and water equations
   of state, and the nonlinear Biot coefficient.
3. **Mandel benchmark.** Compare spatial water-pressure and displacement
   profiles with the analytical Mandel solution and report two-dimensional
   Biot-coefficient and density snapshots at several times. A finite-deformation
   continuation demonstrates departure from the reference coefficient.

The repository must build the paper and reproduce its numerical evidence from
a clean clone. It owns its manuscript workflow and agent skills. Shared MOOSE
files remain synchronized with the authoritative general simulator repository
through a hash-checked, conflict-detecting workflow.
