# Single-element constitutive check of ADDruckerPragerPoroplasticBiotMaterial.
# Prescribed uniform compression (constant deformation gradient), drained (p=0),
# fixed Biot coefficient.  Confirms the active-yield return map runs: a^p > 1,
# Delta_gamma > 0, yield f ~ 0 after return.

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

[AuxVariables]
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
  [equiv_q]
    family = MONOMIAL
    order = CONSTANT
  []
[]

[Materials]
  [const_f]
    type = ADConstantDeformationGradientMaterial
    transverse_stretch = 1.0
    axial_stretch = 0.9
    out_of_plane_stretch = 1.0
  []
  [double_prime]
    type = ADVolumetricBarotropicSkeletonStressMaterial
    equivalent_pressure = p
    shear_modulus = 0.75e9
    skeleton_bulk_modulus = 1.0e9
    mineral_bulk_modulus = 2.5e9
    reference_solid_volume_fraction = 0.9
  []
  [const_biot]
    type = ADGenericConstantMaterial
    prop_names = solid_biot_coefficient
    prop_values = 0.6
  []
  [dp]
    type = ADDruckerPragerPoroplasticBiotMaterial
    pressure = p
    shear_modulus = 0.75e9
    skeleton_bulk_modulus = 1.0e9
    dp_friction_slope = 0.2
    dp_dilation_slope = 0.4
    dp_cohesion = 0.0
  []
[]

[AuxKernels]
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
  [yield_aux]
    type = ADMaterialRealAux
    variable = yield_f
    property = plastic_yield_function
  []
  [mean_aux]
    type = ADMaterialRealAux
    variable = mean_p
    property = plastic_mean_effective_pressure
  []
  [equiv_aux]
    type = ADMaterialRealAux
    variable = equiv_q
    property = plastic_equivalent_shear_stress
  []
[]

[Postprocessors]
  [a_p_avg]
    type = ElementAverageValue
    variable = a_p
  []
  [dgamma_avg]
    type = ElementAverageValue
    variable = dgamma
  []
  [yield_avg]
    type = ElementAverageValue
    variable = yield_f
  []
  [mean_p_avg]
    type = ElementAverageValue
    variable = mean_p
  []
  [equiv_q_avg]
    type = ElementAverageValue
    variable = equiv_q
  []
[]

[Executioner]
  type = Steady
  solve_type = NEWTON
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[Outputs]
  csv = true
  execute_on = timestep_end
[]
