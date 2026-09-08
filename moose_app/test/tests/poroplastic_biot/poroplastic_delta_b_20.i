# Canonical delta-B demonstration at 20% axial compression.
# Canonical stateful multiplicative ideal Drucker-Prager first-loading
# demonstration (ADTensorialPoroplasticBiotMaterial): single element, drained
# (p = 0), axial stretch ramped in time from 1.0 to 0.8 over t in
# [0,1] at M = 0.6, dilation beta = 0.4.  The stored plastic factor F^p
# (det F^p = a^p) accumulates along the path; the reported coefficient
#   B = 1 - (1 - B_el)/a^p
# uses the total-J elastic coefficient B_el of the same drained skeleton and
# mineral (route-A convention), so Delta B = B - B_el > 0 with the mechanism
# active.  

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
[]

[Kernels]
  [p_diffusion]
    type = Diffusion
    variable = p
  []
[]

[BCs]
  [p_zero]
    type = DirichletBC
    variable = p
    boundary = 'left right bottom top'
    value = 0
  []
[]

[ICs]
  [axial_ic]
    type = ConstantIC
    variable = axial_aux
    value = 1
  []
[]

[Functions]
  [axial]
    type = PiecewiseLinear
    x = '0 1'
    y = '1 0.8'
  []
[]

[AuxVariables]
  [axial_aux]
    family = MONOMIAL
    order = CONSTANT
  []
  [b_el]
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
  [b]
    family = MONOMIAL
    order = CONSTANT
  []
  [db]
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
  [b_el_aux]
    type = ADMaterialRealAux
    variable = b_el
    property = plastic_elastic_biot_coefficient
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
  [b_aux]
    type = ADMaterialRealAux
    variable = b
    property = poroplastic_biot_coefficient
  []
  [db_aux]
    type = ParsedAux
    variable = db
    expression = 'b - b_el'
    coupled_variables = 'b b_el'
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
    type = ADTensorialPoroplasticBiotMaterial
    pressure = p
    shear_modulus = 0.75e9
    skeleton_bulk_modulus = 1.0e9
    mineral_bulk_modulus = 2.5e9
    reference_solid_volume_fraction = 0.9
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
  [b_el_avg]
    type = ElementAverageValue
    variable = b_el
  []
  [a_p_avg]
    type = ElementAverageValue
    variable = a_p
  []
  [dgamma_avg]
    type = ElementAverageValue
    variable = dgamma
  []
  [b_avg]
    type = ElementAverageValue
    variable = b
  []
  [db_avg]
    type = ElementAverageValue
    variable = db
  []
[]

[Executioner]
  type = Transient
  start_time = 0
  end_time = 1
  dt = 0.02
  solve_type = NEWTON
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[Outputs]
  csv = true
  execute_on = 'TIMESTEP_END'
  time_step_interval = 2
[]
