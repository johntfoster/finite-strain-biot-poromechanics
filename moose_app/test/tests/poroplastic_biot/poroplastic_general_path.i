# General-path oracle (pure AD): the pore-allocation-corrected coefficient
#   B_reduced = 1 - (1 - B_el)/a^p
# must equal the coefficient returned by the general fixed-history,
# fixed-pressure tangent of the active plastic local system, computed with AD:
#   B_general = 1 - phi_s0 * d(Jbar/a^p)/dJ |_{p, J rho_s, a^p}
# assembled by ADConstrainedSkeletonBiotMaterial from the local residuals of
# ADPlasticStateBiotMaterial (route-A volume fraction phi_s = phi_s0*r/(ratio*a^p)
# with a^p read frozen).  The frozen allocation is the accumulated a^p of the
# canonical stateful tensorial engine (ADTensorialPoroplasticBiotMaterial) at
# the same drained compression, so the oracle verifies that the coefficient the
# canonical engine reports is exactly the fixed-history, fixed-pressure tangent
# of the active plastic local system.  Single element, drained (p = 0),
# prescribed axial compression (SWEEP ANCHOR 'axial_stretch = 0.9').

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
  [b_general]
    family = MONOMIAL
    order = CONSTANT
  []
  [b_reduced]
    family = MONOMIAL
    order = CONSTANT
  []
  [oracle_error]
    family = MONOMIAL
    order = CONSTANT
  []
  [phi_s]
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
  # Elastic oracle provider (a^p = 1): supplies B_el and elastic residuals.
  [local_elastic]
    type = ADLocalElasticMineralBiotMaterial
    pressure = p
    solid_spatial_mass_ratio = r
    mineral_bulk_modulus = 2.5e9
    reference_solid_volume_fraction = 0.9
    biot_coefficient_name = elastic_biot_closed_form
    intrinsic_specific_volume_jacobian_tangent_name = elastic_specific_volume_jacobian_tangent
  []
  [jdot_zero]
    type = ADGenericConstantMaterial
    prop_names = solid_reference_J_dot
    prop_values = 0
  []
  # Frozen canonical plastic allocation: the accumulated a^p of the canonical
  # stateful tensorial engine at this compression (SWEEP ANCHOR
  # 'prop_values = 1.015137' below).
  [frozen_ap_ad]
    type = ADGenericConstantMaterial
    prop_names = plastic_pore_allocation
    prop_values = 1.015137
  []
  [frozen_ap_value]
    type = GenericConstantMaterial
    prop_names = plastic_pore_allocation_value
    prop_values = 1.015137
  []
  # Reduced closed-form oracle: B_reduced = 1 - (1 - B_el)/a^p.
  [b_correct]
    type = ADPoroplasticBiotCoefficientMaterial
    elastic_biot_coefficient_name = elastic_biot_closed_form
    plastic_pore_allocation_name = plastic_pore_allocation
  []
  # General-path residual provider (route-A phi_s with a^p frozen).
  [plastic_state]
    type = ADPlasticStateBiotMaterial
    pressure = p
    solid_spatial_mass_ratio = r
    mineral_bulk_modulus = 2.5e9
    reference_solid_volume_fraction = 0.9
    plastic_pore_allocation_value_name = plastic_pore_allocation_value
  []
  [plastic_accumulation]
    type = ADParsedMaterial
    material_property_names = solid_reference_J
    property_name = plastic_solid_reference_accumulation_for_biot
    constant_names = phi0
    constant_expressions = 0.9
    expression = 'phi0*solid_reference_J'
  []
  [implicit_state_selectors]
    type = ADGenericConstantMaterial
    prop_names = 'implicit_state_zero implicit_state_one'
    prop_values = '0 1'
  []
  # General dense AD tangent of the active plastic local system (V2 oracle).
  [constrained_biot_state]
    type = ADConstrainedSkeletonBiotMaterial
    constraint_residual_names = 'plastic_local_material_mass_constraint plastic_mineral_eos_constraint'
    implicit_state_symbols = 'plastic_intrinsic_density_ratio plastic_solid_volume_fraction'
    constraint_residual_scales = '1 1'
    aggregate_solid_volume_fraction_name = plastic_solid_volume_fraction
    skeleton_component_reference_accumulation_names = plastic_solid_reference_accumulation_for_biot
    constraint_jacobian_derivative_names = 'plastic_local_material_mass_d_jacobian plastic_mineral_eos_d_jacobian'
    constraint_state_derivative_names = 'plastic_local_material_mass_d_intrinsic_density_ratio plastic_local_material_mass_d_volume_fraction plastic_mineral_eos_d_intrinsic_density_ratio plastic_mineral_eos_d_volume_fraction'
    volume_fraction_state_derivative_names = 'implicit_state_zero implicit_state_one'
    reference_specific_volume = '${fparse 1/0.9}'
    intrinsic_specific_volume_name = plastic_intrinsic_specific_volume_from_constraints
    intrinsic_skeleton_density_name = plastic_intrinsic_density_from_constraints
    constraint_norm_name = plastic_biot_constraint_norm
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
  [b_general_aux]
    type = ADMaterialRealAux
    variable = b_general
    property = solid_biot_coefficient
  []
  [b_reduced_aux]
    type = ADMaterialRealAux
    variable = b_reduced
    property = poroplastic_biot_coefficient
  []
  [phi_s_aux]
    type = ADMaterialRealAux
    variable = phi_s
    property = plastic_solid_volume_fraction
  []
  [oracle_error_aux]
    type = ParsedAux
    variable = oracle_error
    expression = 'b_general - b_reduced'
    coupled_variables = 'b_general b_reduced'
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
  [b_general_avg]
    type = ElementAverageValue
    variable = b_general
  []
  [b_reduced_avg]
    type = ElementAverageValue
    variable = b_reduced
  []
  [oracle_error_avg]
    type = ElementAverageValue
    variable = oracle_error
  []
  [phi_s_avg]
    type = ElementAverageValue
    variable = phi_s
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
