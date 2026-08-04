[Materials]
  [solid_reference_j_path]
    type = ADParsedMaterial
    coupled_variables = solid_reference_J_state
    property_name = solid_reference_J
    expression = 'solid_reference_J_state'
  []
  [equivalent_pressure_reconstructed]
    type = ADEGReconstructedScalarMaterial
    field_name = equivalent_pressure
    backbone = equivalent_pressure
    enrichment = equivalent_pressure_enr
  []
[]

[AuxKernels]
  [equivalent_pressure_total_aux]
    type = ADMaterialRealAux
    variable = equivalent_pressure_total
    property = equivalent_pressure_total
    execute_on = INITIAL
  []
[]
