# Overlay for compression.i: sealed body with prescribed nonzero plastic history.
[Functions]
  [top_displacement]
    expression = '-0.001'
  []
  [initial_vertical]
    type = ParsedFunction
    expression = '-0.01*y'
  []
[]
[ICs]
  [vertical]
    type = FunctionIC
    variable = uy
    function = initial_vertical
  []
  [pressure]
    type = ConstantIC
    variable = p
    value = 1e6
  []
[]
[Materials]
  [plastic]
    initial_plastic_distention = 1.01
  []
[]
[BCs]
  active = 'symmetry_x symmetry_y rigid_top lateral_fix'
  [lateral_fix]
    type = DirichletBC
    variable = ux
    boundary = right
    value = 0
  []
[]
[Postprocessors]
  [mass_initial_check]
    type = ADElementIntegralMaterialProperty
    mat_prop = fluid_mass
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [pressure_initial_check]
    type = ElementAverageValue
    variable = p
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [plastic_initial_check]
    type = ADElementAverageMaterialProperty
    mat_prop = plastic_pore_allocation
    execute_on = 'INITIAL TIMESTEP_END'
  []
[]
[Executioner]
  end_time = .02
[]
[Outputs]
  exodus = false
  execute_on = 'INITIAL TIMESTEP_END'
[]
