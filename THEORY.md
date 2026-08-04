# Theory reference

Let \(\mathcal S\) denote the registered solid phases and \(\alpha\) their
components. The intrinsic skeleton specific volume is formed directly from the
solid-phase/component sum of the referential storage in Eq. (32):

\[
\bar v_s =
\frac{J_s\displaystyle\sum_{a\in\mathcal S}\phi_a}
{\displaystyle\sum_{a\in\mathcal S}\sum_\alpha J_s\rho_a^\alpha}.
\]

The nonlinear coefficient is

\[
B = 1-\frac{1}{v_{s0}}
\left.\frac{\partial\bar v_s}{\partial J_s}
\right|_{p_E,T,\ldots}.
\]

For local constraints \(\mathbf R(\mathbf y,J_s,p_E,T,\ldots)=\mathbf0\),

\[
\mathbf R_{\mathbf y}\mathbf y_{,J}+\mathbf R_{,J}=\mathbf0,
\qquad
\mathbf y_{,J}=-\mathbf R_{\mathbf y}^{-1}\mathbf R_{,J},
\]

where the derivative is evaluated at fixed \(p_E\) and the other declared
variables. Substitution into the quotient derivative of \(\bar v_s\) gives the
constrained tangent. In the single-solid infinitesimal-strain limit,

\[
B_0=1-\frac{K}{K_s}.
\]

Lawal and Kim report the same classical coefficient as
\(\alpha=1-K/K_s'\), using pressure-dependent drained modulus \(K\) and the
unjacketed modulus \(K_s'\). Their pressure coordinate is confining/effective
mean pressure, not the equivalent pore pressure held fixed in the constitutive
partial.

For the replication, fit a positive pressure-dependent drained tangent modulus
using a crack-closure compliance law,

\[
\frac{1}{K(P)}=\frac{1}{K_\infty}+C_c\exp(-P/P_c),
\]

and compare \(1-K(P)/K_s'\) with both the experimental points and the nonlinear
implicit-AD result along the hydrostatic loading path. The final accepted model
must preserve positive tangent stiffness and \(0\le B\le1\) over the calibrated
pressure range.

