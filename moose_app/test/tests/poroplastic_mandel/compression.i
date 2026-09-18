# Coupled poroplastic compression and drainage on the Mandel quarter-domain.
# Backward Euler field rates and beta*Delta_gamma/dt supply the pore-volume rate.

mesh_nx := 20
mesh_ny := 2
stiffness_scale_pa := 1e9
initial_solid_volume_fraction := 0.9
skeleton_bulk_modulus_pa := '${fparse 1.0*stiffness_scale_pa}'
skeleton_shear_modulus_pa := '${fparse 0.75*stiffness_scale_pa}'
mineral_bulk_modulus_pa := '${fparse 2.5*stiffness_scale_pa}'
water_bulk_modulus_pa := '${fparse 8.0*stiffness_scale_pa}'
water_density_kg_m3 := 1000
water_viscosity_pa_s := 1e-3
water_permeability_m2 := '${fparse 1.5*water_viscosity_pa_s/stiffness_scale_pa}'
step := 0.01
cohesion_pa := 2e7
dilation_slope := 0.4
hardening_modulus_pa := '${fparse 0.1*stiffness_scale_pa}'

[Mesh]
  type = GeneratedMesh
  dim = 2
  xmin = 0
  xmax = 1
  ymin = 0
  ymax = 0.1
  nx = ${mesh_nx}
  ny = ${mesh_ny}
  elem_type = QUAD9
[]

[Variables]
  [ux]
    family = LAGRANGE
    order = SECOND
  []
  [uy]
    family = LAGRANGE
    order = SECOND
  []
  [p]
    family = LAGRANGE
    order = FIRST
  []
  [solid_spatial_mass_ratio]
    family = LAGRANGE
    order = SECOND
  []
[]

[AuxVariables]
  [water_reaction]
    family = LAGRANGE
    order = FIRST
  []
  [gamma]
    family = MONOMIAL
    order = CONSTANT
  []
  [ap]
    family = MONOMIAL
    order = CONSTANT
  []
  [delta_b]
    family = MONOMIAL
    order = CONSTANT
  []
  [elastic_b]
    family = MONOMIAL
    order = CONSTANT
  []
  [biot_coefficient_state]
    family = MONOMIAL
    order = CONSTANT
  []
  [solid_intrinsic_density_ratio_state]
    family = MONOMIAL
    order = CONSTANT
  []
  [solid_volume_fraction_state]
    family = MONOMIAL
    order = CONSTANT
  []
[]

[ICs]
  [solid_spatial_mass_ratio_ic]
    type = ConstantIC
    variable = solid_spatial_mass_ratio
    value = 1
  []
[]

[Functions]
  [zero]
    type = ParsedFunction
    expression = '0'
  []
  [top_displacement]
    type = ParsedFunction
    expression = '-0.01*min(t/0.2,1)'
  []
[]

[Materials]
  [plastic]
    type = ADImplicitPoroplasticBiotMaterial
    pressure = p
    shear_modulus = ${skeleton_shear_modulus_pa}
    skeleton_bulk_modulus = ${skeleton_bulk_modulus_pa}
    mineral_bulk_modulus = ${mineral_bulk_modulus_pa}
    reference_solid_volume_fraction = ${initial_solid_volume_fraction}
    dp_friction_slope = 0.6
    dp_dilation_slope = ${dilation_slope}
    dp_cohesion = ${cohesion_pa}
    dp_hardening_modulus = ${hardening_modulus_pa}
  []
  [pore_volume]
    type = ADPoroplasticPoreVolumeMaterial
    pressure = p
    solid_spatial_mass_ratio = solid_spatial_mass_ratio
    skeleton_bulk_modulus = ${skeleton_bulk_modulus_pa}
    mineral_bulk_modulus = ${mineral_bulk_modulus_pa}
    reference_solid_volume_fraction = ${initial_solid_volume_fraction}
    dp_dilation_slope = ${dilation_slope}
  []
  [delta_b]
    type = ADParsedMaterial
    material_property_names = 'poroplastic_biot_coefficient plastic_elastic_biot_coefficient'
    property_name = biot_difference
    expression = 'poroplastic_biot_coefficient-plastic_elastic_biot_coefficient'
  []
  [solid_kinematics]
    type = ADSolidReferenceKinematics
    displacements = 'ux uy'
  []
  [solid_spatial_mass]
    type = ADBinarySolidSpatialMassMaterial
    solid_spatial_mass_ratio = solid_spatial_mass_ratio
  []
  [water_mass_storage]
    type = ADBiotPressureStorageMaterial
    pressure = p
    reference_density = ${water_density_kg_m3}
    fluid_bulk_modulus = ${water_bulk_modulus_pa}
    intrinsic_density_name = water_intrinsic_density
    reference_accumulation_name = water_reference_accumulation
    storage_rate_name = water_reference_storage_rate
  []
  [water_flux]
    type = ADBiotDarcyReferenceFluxMaterial
    pressure = p
    intrinsic_density_name = water_intrinsic_density
    permeability = ${water_permeability_m2}
    viscosity = ${water_viscosity_pa_s}
    reference_mobility_name = water_mobility_ref
    reference_mass_flux_name = water_reference_mass_flux
  []
  [solid_material_mass_constraint]
    type = ADParsedMaterial
    coupled_variables = solid_spatial_mass_ratio
    material_property_names = solid_reference_J
    property_name = solid_material_mass_constraint
    expression = 'solid_reference_J*solid_spatial_mass_ratio-1'
  []
[]

[Kernels]
  [solid_x]
    first_piola_stress_name = implicit_plastic_total_P
    type = ADReferenceSolidMomentum
    variable = ux
    component = 0
  []
  [solid_y]
    first_piola_stress_name = implicit_plastic_total_P
    type = ADReferenceSolidMomentum
    variable = uy
    component = 1
  []
  [solid_mass_balance]
    type = ADReferenceMaterialStorageRateTerm
    variable = solid_spatial_mass_ratio
    reference_storage_rate_name = solid_component_reference_storage_rate
    scale = ${skeleton_bulk_modulus_pa}
  []
  [water_storage]
    save_in = water_reaction
    type = ADReferenceMaterialStorageRateTerm
    variable = p
    reference_storage_rate_name = water_reference_storage_rate
    scale = '${fparse 1/water_density_kg_m3}'
  []
  [water_flux]
    save_in = water_reaction
    type = ADReferenceComponentFluxTerm
    variable = p
    reference_flux_name = water_reference_mass_flux
    scale = '${fparse 1/water_density_kg_m3}'
  []
[]

[AuxKernels]
  [gamma]
    type = ADMaterialRealAux
    variable = gamma
    property = plastic_multiplier_increment
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [ap]
    type = ADMaterialRealAux
    variable = ap
    property = plastic_pore_allocation
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [delta_b]
    type = ADMaterialRealAux
    variable = delta_b
    property = biot_difference
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [elastic_b]
    type = ADMaterialRealAux
    variable = elastic_b
    property = plastic_elastic_biot_coefficient
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [biot_coefficient_output]
    type = ADMaterialRealAux
    variable = biot_coefficient_state
    property = poroplastic_biot_coefficient
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [solid_intrinsic_density_ratio_output]
    type = ADMaterialRealAux
    variable = solid_intrinsic_density_ratio_state
    property = implicit_plastic_density_ratio
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [solid_volume_fraction_output]
    type = ADMaterialRealAux
    variable = solid_volume_fraction_state
    property = solid_volume_fraction
    execute_on = 'INITIAL TIMESTEP_END'
  []
[]

[BCs]
  [symmetry_x]
    type = DirichletBC
    variable = ux
    boundary = left
    value = 0
  []
  [symmetry_y]
    type = DirichletBC
    variable = uy
    boundary = bottom
    value = 0
  []
  [rigid_top]
    type = FunctionDirichletBC
    variable = uy
    boundary = top
    function = top_displacement
  []
  [drained_side]
    type = DirichletBC
    variable = p
    boundary = right
    value = 0
  []
[]

[Postprocessors]
  [water_boundary_residual]
    type = NodalDofSum
    variable = water_reaction
    boundary = right
  []
  [outflow_reaction]
    type = ParsedPostprocessor
    pp_names = water_boundary_residual
    expression = '-1000*water_boundary_residual'
  []
  [water_mass]
    type = ADElementIntegralMaterialProperty
    mat_prop = water_reference_accumulation
  []
  [water_rate]
    type = ADElementIntegralMaterialProperty
    mat_prop = water_reference_storage_rate
  []
  [outflow]
    type = ADSideIntegralMaterialProperty
    property = water_reference_mass_flux
    component = 0
    boundary = right
  []
  [plastic_pore_rate]
    type = ADElementIntegralMaterialProperty
    mat_prop = plastic_pore_volume_rate
  []
  [gamma_max]
    type = ADElementExtremeMaterialProperty
    mat_prop = plastic_multiplier_increment
    value_type = max
  []
  [gamma_average]
    type = ADElementAverageMaterialProperty
    mat_prop = plastic_multiplier_increment
  []
  [ap_max]
    type = ADElementExtremeMaterialProperty
    mat_prop = plastic_pore_allocation
    value_type = max
  []
  [ap_average]
    type = ADElementAverageMaterialProperty
    mat_prop = plastic_pore_allocation
  []
  [delta_b_max]
    type = ADElementExtremeMaterialProperty
    mat_prop = biot_difference
    value_type = max
  []
  [delta_b_average]
    type = ADElementAverageMaterialProperty
    mat_prop = biot_difference
  []
  [elastic_b_max]
    type = ADElementExtremeMaterialProperty
    mat_prop = plastic_elastic_biot_coefficient
    value_type = max
  []
  [elastic_b_average]
    type = ADElementAverageMaterialProperty
    mat_prop = plastic_elastic_biot_coefficient
  []
  [pressure_x0]
    type = PointValue
    variable = p
    point = '0 0 0'
  []
  [pressure_x03]
    type = PointValue
    variable = p
    point = '0.3 0 0'
  []
  [pressure_x08]
    type = PointValue
    variable = p
    point = '0.8 0 0'
  []
  [side_displacement]
    type = PointValue
    variable = ux
    point = '1 0.1 0'
  []
  [top_displacement]
    type = PointValue
    variable = uy
    point = '1 0.1 0'
  []
  [vertical_nominal_stress]
    type = ADMaterialTensorAverage
    rank_two_tensor = implicit_plastic_total_P
    index_i = 1
    index_j = 1
    use_displaced_mesh = false
  []
  [biot_average]
    type = ADElementAverageMaterialProperty
    mat_prop = poroplastic_biot_coefficient
  []
  [biot_minimum]
    type = ADElementExtremeMaterialProperty
    mat_prop = poroplastic_biot_coefficient
    value_type = min
  []
  [biot_maximum]
    type = ADElementExtremeMaterialProperty
    mat_prop = poroplastic_biot_coefficient
    value_type = max
  []
  [solid_material_mass_constraint_l2]
    type = ADMaterialScalarL2Error
    property = solid_material_mass_constraint
    function = zero
  []
  [solid_mineral_eos_constraint_l2]
    type = ADMaterialScalarL2Error
    property = solid_mineral_eos_constraint
    function = zero
  []
[]

[Preconditioning]
  [monolithic]
    type = SMP
    full = true
    petsc_options_iname = '-pc_type -pc_factor_mat_solver_type'
    petsc_options_value = 'lu superlu_dist'
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  line_search = bt
  scheme = implicit-euler
  [Predictor]
    type = SimplePredictor
    scale = 0.9
  []
  automatic_scaling = true
  compute_scaling_once = false
  nl_abs_tol = 1e-7
  nl_rel_tol = 1e-9
  nl_max_its = 30
  start_time = 0
  end_time = 0.7
  dt = ${step}
[]

[Outputs]
  execute_on = TIMESTEP_END
  csv = true
  console = false
  exodus = true
[]
