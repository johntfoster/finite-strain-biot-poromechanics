# Homogeneous constitutive verification: load, unload and reload.
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
    x = '0 1 2 3'
    y = '1 0.8 0.9 0.76'
  []
[]

[AuxVariables]
  [density]
    family = MONOMIAL
    order = CONSTANT
  []
  [solid_fraction]
    family = MONOMIAL
    order = CONSTANT
  []
  [mass_error]
    family = MONOMIAL
    order = CONSTANT
  []
  [flow_error]
    family = MONOMIAL
    order = CONSTANT
  []
  [b_el]
    family = MONOMIAL
    order = CONSTANT
  []
  [fp00]
    family = MONOMIAL
    order = CONSTANT
  []
  [fp01]
    family = MONOMIAL
    order = CONSTANT
  []
  [fp02]
    family = MONOMIAL
    order = CONSTANT
  []
  [fp10]
    family = MONOMIAL
    order = CONSTANT
  []
  [fp11]
    family = MONOMIAL
    order = CONSTANT
  []
  [fp12]
    family = MONOMIAL
    order = CONSTANT
  []
  [fp20]
    family = MONOMIAL
    order = CONSTANT
  []
  [fp21]
    family = MONOMIAL
    order = CONSTANT
  []
  [fp22]
    family = MONOMIAL
    order = CONSTANT
  []
  [tau00]
    family = MONOMIAL
    order = CONSTANT
  []
  [tau01]
    family = MONOMIAL
    order = CONSTANT
  []
  [tau02]
    family = MONOMIAL
    order = CONSTANT
  []
  [tau10]
    family = MONOMIAL
    order = CONSTANT
  []
  [tau11]
    family = MONOMIAL
    order = CONSTANT
  []
  [tau12]
    family = MONOMIAL
    order = CONSTANT
  []
  [tau20]
    family = MONOMIAL
    order = CONSTANT
  []
  [tau21]
    family = MONOMIAL
    order = CONSTANT
  []
  [tau22]
    family = MONOMIAL
    order = CONSTANT
  []
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
  [density_aux]
    type = ADMaterialRealAux
    variable = density
    property = implicit_plastic_density_ratio
  []
  [solid_fraction_aux]
    type = ADMaterialRealAux
    variable = solid_fraction
    property = implicit_plastic_solid_fraction
  []
  [mass_error_aux]
    type = ADMaterialRealAux
    variable = mass_error
    property = implicit_plastic_mass_error
  []
  [flow_error_aux]
    type = ADMaterialRealAux
    variable = flow_error
    property = implicit_plastic_flow_error
  []
  [b_el_aux]
    type = ADMaterialRealAux
    variable = b_el
    property = plastic_elastic_biot_coefficient
  []
  [fp00_aux]
    type = ADMaterialRankTwoTensorAux
    variable = fp00
    property = implicit_plastic_Fp
    i = 0
    j = 0
  []
  [fp01_aux]
    type = ADMaterialRankTwoTensorAux
    variable = fp01
    property = implicit_plastic_Fp
    i = 0
    j = 1
  []
  [fp02_aux]
    type = ADMaterialRankTwoTensorAux
    variable = fp02
    property = implicit_plastic_Fp
    i = 0
    j = 2
  []
  [fp10_aux]
    type = ADMaterialRankTwoTensorAux
    variable = fp10
    property = implicit_plastic_Fp
    i = 1
    j = 0
  []
  [fp11_aux]
    type = ADMaterialRankTwoTensorAux
    variable = fp11
    property = implicit_plastic_Fp
    i = 1
    j = 1
  []
  [fp12_aux]
    type = ADMaterialRankTwoTensorAux
    variable = fp12
    property = implicit_plastic_Fp
    i = 1
    j = 2
  []
  [fp20_aux]
    type = ADMaterialRankTwoTensorAux
    variable = fp20
    property = implicit_plastic_Fp
    i = 2
    j = 0
  []
  [fp21_aux]
    type = ADMaterialRankTwoTensorAux
    variable = fp21
    property = implicit_plastic_Fp
    i = 2
    j = 1
  []
  [fp22_aux]
    type = ADMaterialRankTwoTensorAux
    variable = fp22
    property = implicit_plastic_Fp
    i = 2
    j = 2
  []
  [tau00_aux]
    type = ADMaterialRankTwoTensorAux
    variable = tau00
    property = implicit_plastic_tau_prime
    i = 0
    j = 0
  []
  [tau01_aux]
    type = ADMaterialRankTwoTensorAux
    variable = tau01
    property = implicit_plastic_tau_prime
    i = 0
    j = 1
  []
  [tau02_aux]
    type = ADMaterialRankTwoTensorAux
    variable = tau02
    property = implicit_plastic_tau_prime
    i = 0
    j = 2
  []
  [tau10_aux]
    type = ADMaterialRankTwoTensorAux
    variable = tau10
    property = implicit_plastic_tau_prime
    i = 1
    j = 0
  []
  [tau11_aux]
    type = ADMaterialRankTwoTensorAux
    variable = tau11
    property = implicit_plastic_tau_prime
    i = 1
    j = 1
  []
  [tau12_aux]
    type = ADMaterialRankTwoTensorAux
    variable = tau12
    property = implicit_plastic_tau_prime
    i = 1
    j = 2
  []
  [tau20_aux]
    type = ADMaterialRankTwoTensorAux
    variable = tau20
    property = implicit_plastic_tau_prime
    i = 2
    j = 0
  []
  [tau21_aux]
    type = ADMaterialRankTwoTensorAux
    variable = tau21
    property = implicit_plastic_tau_prime
    i = 2
    j = 1
  []
  [tau22_aux]
    type = ADMaterialRankTwoTensorAux
    variable = tau22
    property = implicit_plastic_tau_prime
    i = 2
    j = 2
  []
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
  [density]
    type = ElementAverageValue
    variable = density
  []
  [solid_fraction]
    type = ElementAverageValue
    variable = solid_fraction
  []
  [mass_error]
    type = ElementAverageValue
    variable = mass_error
  []
  [flow_error]
    type = ElementAverageValue
    variable = flow_error
  []
  [b_el]
    type = ElementAverageValue
    variable = b_el
  []
  [fp00]
    type = ElementAverageValue
    variable = fp00
  []
  [fp01]
    type = ElementAverageValue
    variable = fp01
  []
  [fp02]
    type = ElementAverageValue
    variable = fp02
  []
  [fp10]
    type = ElementAverageValue
    variable = fp10
  []
  [fp11]
    type = ElementAverageValue
    variable = fp11
  []
  [fp12]
    type = ElementAverageValue
    variable = fp12
  []
  [fp20]
    type = ElementAverageValue
    variable = fp20
  []
  [fp21]
    type = ElementAverageValue
    variable = fp21
  []
  [fp22]
    type = ElementAverageValue
    variable = fp22
  []
  [tau00]
    type = ElementAverageValue
    variable = tau00
  []
  [tau01]
    type = ElementAverageValue
    variable = tau01
  []
  [tau02]
    type = ElementAverageValue
    variable = tau02
  []
  [tau10]
    type = ElementAverageValue
    variable = tau10
  []
  [tau11]
    type = ElementAverageValue
    variable = tau11
  []
  [tau12]
    type = ElementAverageValue
    variable = tau12
  []
  [tau20]
    type = ElementAverageValue
    variable = tau20
  []
  [tau21]
    type = ElementAverageValue
    variable = tau21
  []
  [tau22]
    type = ElementAverageValue
    variable = tau22
  []
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
  time_step_interval = 1
[]
