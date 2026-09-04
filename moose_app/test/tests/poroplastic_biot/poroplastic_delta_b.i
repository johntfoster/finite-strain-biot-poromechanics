# Single-element demonstration of the plastic pore-allocation correction to B:
#   B_pl = 1 - (1 - B_el)/a^p   (route A, M3)
# Prescribed 10% axial compression, drained (p=0), active DP return (M=0.2).
# Outputs: elastic B_el, a^p, Delta_gamma, B_pl, Delta B = B_pl - B_el.

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
[]

[AuxVariables]
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
  [b_pl]
    family = MONOMIAL
    order = CONSTANT
  []
  [db]
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
  [local_elastic]
    type = ADLocalElasticMineralBiotMaterial
    pressure = p
    solid_spatial_mass_ratio = r
    mineral_bulk_modulus = 2.5e9
    reference_solid_volume_fraction = 0.9
    biot_coefficient_name = elastic_biot_closed_form
  []
  [const_biot]
    type = ADGenericConstantMaterial
    prop_names = solid_biot_coefficient
    prop_values = 0.6
  []
  [jdot_zero]
    type = ADGenericConstantMaterial
    prop_names = solid_reference_J_dot
    prop_values = 0
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
  [b_correct]
    type = ADPoroplasticBiotCoefficientMaterial
    elastic_biot_coefficient_name = elastic_biot_closed_form
    plastic_pore_allocation_name = plastic_pore_allocation
    biot_coefficient_name = poroplastic_biot_coefficient
    biot_delta_name = poroplastic_biot_delta
  []
[]

[AuxKernels]
  [b_el_aux]
    type = ADMaterialRealAux
    variable = b_el
    property = elastic_biot_closed_form
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
  [b_pl_aux]
    type = ADMaterialRealAux
    variable = b_pl
    property = poroplastic_biot_coefficient
  []
  [db_aux]
    type = ADMaterialRealAux
    variable = db
    property = poroplastic_biot_delta
  []
[]

[Postprocessors]
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
  [b_pl_avg]
    type = ElementAverageValue
    variable = b_pl
  []
  [db_avg]
    type = ElementAverageValue
    variable = db
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
