# Vision

The paper will show that the finite-deformation Biot coefficient is not a
manually supplied scalar. It is a constrained constitutive tangent computed
from material conservation, phase volume, EOS, and equilibrium statements at
fixed equivalent pore pressure. A small dense implicit solve supplies the inner
partial derivative, while MOOSE automatic differentiation differentiates the
resulting coefficient through the global residual.

The pressure-dependent dunite measurements provide a stringent nonreacting
application: microcrack closure raises the drained tangent bulk modulus with
confining pressure, causing the measured Biot coefficient to fall. The study
will determine whether a compact pressure-dependent constitutive closure,
embedded in the same implicit-AD architecture, reproduces HT14, SP14, and SP30.

