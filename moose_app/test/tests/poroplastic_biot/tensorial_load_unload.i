# Implicit poroplastic loading with the mineral equation (63) and coefficient (68).
[Mesh]
  type = GeneratedMesh
  dim = 2
  xmin = 0
  xmax = 1
  ymin = 0
  ymax = 0.1
  nx = 1
  ny = 1
  elem_type = QUAD9
[]

[Variables]
  [p]
    family = LAGRANGE
    order = FIRST
  []
  [r]
    family = LAGRANGE
    order = FIRST
  []
[]

[Kernels]
  [p_diffusion]
    type = Diffusion
    variable = p
  []
  [r_diffusion]
    type = Diffusion
    variable = r
  []
[]

[BCs]
  [p_zero]
    type = DirichletBC
    variable = p
    boundary = 'left right bottom top'
    value = 0
  []
  [r_one]
    type = DirichletBC
    variable = r
    boundary = 'left right bottom top'
    value = 1
  []
[]

[ICs]
  [r_ic]
    type = ConstantIC
    variable = r
    value = 1
  []
  [axial_ic]
    type = ConstantIC
    variable = axial_aux
    value = 1
  []
[]

[Functions]
  [axial]
    type = PiecewiseLinear
    x = '0 1 2 3'
    y = '1 0.8 0.9 0.8'
  []
[]

[AuxVariables]
  [axial_aux]
    family = MONOMIAL
    order = CONSTANT
  []
  [a_p]
    family = MONOMIAL
    order = CONSTANT
  []
  [dgamma]
    family = MONOMIAL
    order = CONSTANT
  []
  [yield_f]
    family = MONOMIAL
    order = CONSTANT
  []
  [mean_p]
    family = MONOMIAL
    order = CONSTANT
  []
  [q]
    family = MONOMIAL
    order = CONSTANT
  []
  [b]
    family = MONOMIAL
    order = CONSTANT
  []
[]

[AuxKernels]
  [axial_aux]
    type = FunctionAux
    variable = axial_aux
    function = axial
    execute_on = 'INITIAL TIMESTEP_BEGIN'
  []
  [a_p_aux]
    type = ADMaterialRealAux
    variable = a_p
    property = plastic_pore_allocation
  []
  [dgamma_aux]
    type = ADMaterialRealAux
    variable = dgamma
    property = plastic_multiplier_increment
  []
  [yield_f_aux]
    type = ADMaterialRealAux
    variable = yield_f
    property = plastic_yield_function
  []
  [mean_p_aux]
    type = ADMaterialRealAux
    variable = mean_p
    property = plastic_mean_effective_pressure
  []
  [q_aux]
    type = ADMaterialRealAux
    variable = q
    property = plastic_equivalent_shear_stress
  []
  [b_aux]
    type = ADMaterialRealAux
    variable = b
    property = poroplastic_biot_coefficient
  []
[]

[Materials]
  [const_f]
    type = ADConstantDeformationGradientMaterial
    transverse_stretch = 1.0
    axial_stretch = 1.0
    out_of_plane_stretch = 1.0
    axial_stretch_variable = axial_aux
  []
  [tensorial]
    type = ADImplicitPoroplasticBiotMaterial
    pressure = p
    shear_modulus = 0.75e9
    skeleton_bulk_modulus = 1.0e9
    mineral_bulk_modulus = 2.5e9
    reference_solid_volume_fraction = 0.8
    dp_friction_slope = 0.6
    dp_dilation_slope = 0.4
    dp_cohesion = 0.0
  []
[]

[Postprocessors]
  [compression]
    type = ElementAverageValue
    variable = axial_aux
  []
  [a_p_avg]
    type = ElementAverageValue
    variable = a_p
  []
  [dgamma_avg]
    type = ElementAverageValue
    variable = dgamma
  []
  [yield_f_avg]
    type = ElementAverageValue
    variable = yield_f
  []
  [mean_p_avg]
    type = ElementAverageValue
    variable = mean_p
  []
  [q_avg]
    type = ElementAverageValue
    variable = q
  []
  [b_avg]
    type = ElementAverageValue
    variable = b
  []
[]

[Executioner]
  type = Transient
  start_time = 0
  end_time = 3
  dt = 0.02
  solve_type = NEWTON
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[Outputs]
  csv = true
  execute_on = 'TIMESTEP_END'
  time_step_interval = 5
[]
