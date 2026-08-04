[AuxVariables]
  [ux]
    family = LAGRANGE
    order = SECOND
  []
  [solid_reference_J_state]
    family = LAGRANGE
    order = SECOND
  []
  [equivalent_pressure]
    family = LAGRANGE
    order = FIRST
  []
  [equivalent_pressure_enr]
    family = MONOMIAL
    order = CONSTANT
  []
  [equivalent_pressure_total]
    family = MONOMIAL
    order = FIRST
  []
  [mean_effective_pressure_state]
    family = LAGRANGE
    order = SECOND
  []
  [solid_volume_fraction_state]
    family = LAGRANGE
    order = SECOND
  []
  [biot_coefficient_out]
    family = MONOMIAL
    order = CONSTANT
  []
  [biot_classical_out]
    family = MONOMIAL
    order = CONSTANT
  []
  [drained_bulk_modulus_out]
    family = MONOMIAL
    order = CONSTANT
  []
  [constraint_norm_out]
    family = MONOMIAL
    order = CONSTANT
  []
[]
