
# A sealed, uniformly deformed body at nonzero pressure must remain stationary.
[Functions]
  [ux_initial]
    expression = '0.02*x'
  []
  [pressure_initial]
    expression = '0.25'
  []
[]
[BCs]
  active = ux
  [ux]
    function = ux_initial
  []
[]
[Postprocessors]
  [pressure]
    execute_on = 'INITIAL TIMESTEP_END'
    type = ElementAverageValue
    variable = p
  []
  [mass]
    execute_on = 'INITIAL TIMESTEP_END'
    type = ADElementIntegralMaterialProperty
    mat_prop = fluid_mass
  []
  [solid_mass]
    execute_on = 'INITIAL TIMESTEP_END'
    type = ADElementIntegralMaterialProperty
    mat_prop = solid_component_reference_accumulation
  []
[]
[Executioner]
  end_time = 0.1
[]
[Outputs]
  csv = true
  execute_on = 'INITIAL TIMESTEP_END'
[]
