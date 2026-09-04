[Mesh]
  type = GeneratedMesh
  dim = 1
  xmin = 0
  xmax = 1
  nx = 2
  elem_type = EDGE3
[]

[Variables]
  [ux]
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

[Functions]
  [zero]
    type = ParsedFunction
    expression = '0'
  []
  [ux_initial]
    type = ParsedFunction
    expression = '0.02*x*(1-x)'
  []
  [pressure_initial]
    type = ParsedFunction
    expression = '0.25+0.03*x'
  []
  [solid_spatial_mass_initial]
    type = ParsedFunction
    expression = '1+0.01*x'
  []
[]

[ICs]
  [ux]
    type = FunctionIC
    variable = ux
    function = ux_initial
  []
  [p]
    type = FunctionIC
    variable = p
    function = pressure_initial
  []
  [solid_spatial_mass]
    type = FunctionIC
    variable = solid_spatial_mass_ratio
    function = solid_spatial_mass_initial
  []
[]

[Materials]
  [solid_kinematics]
    type = ADSolidReferenceKinematics
    displacements = ux
  []
  [solid_spatial_mass]
    type = ADBinarySolidSpatialMassMaterial
    solid_spatial_mass_ratio = solid_spatial_mass_ratio
  []
  [double_prime_stress]
    type = ADVolumetricBarotropicSkeletonStressMaterial
    equivalent_pressure = p
    shear_modulus = 0.3
    skeleton_bulk_modulus = 0.5
    mineral_bulk_modulus = 2
    reference_solid_volume_fraction = 0.25
  []
  [local_solid_state]
    type = ADLocalElasticMineralBiotMaterial
    pressure = p
    solid_spatial_mass_ratio = solid_spatial_mass_ratio
    mineral_bulk_modulus = 2
    reference_solid_volume_fraction = 0.25
    biot_coefficient_name = elastic_biot_closed_form
    intrinsic_specific_volume_jacobian_tangent_name = elastic_specific_volume_jacobian_tangent
  []
  [solid_reference_accumulation_for_biot]
    type = ADParsedMaterial
    material_property_names = solid_component_reference_accumulation
    property_name = solid_reference_accumulation_for_biot
    constant_names = phi0
    constant_expressions = 0.25
    expression = 'phi0*solid_component_reference_accumulation'
  []
  [implicit_state_selectors]
    type = ADGenericConstantMaterial
    prop_names = 'implicit_state_zero implicit_state_one'
    prop_values = '0 1'
  []
  [constrained_biot_state]
    type = ADConstrainedSkeletonBiotMaterial
    constraint_residual_names = 'solid_local_material_mass_constraint solid_mineral_eos_constraint'
    implicit_state_symbols = 'solid_intrinsic_density_ratio solid_volume_fraction'
    constraint_residual_scales = '1 1'
    aggregate_solid_volume_fraction_name = solid_volume_fraction
    skeleton_component_reference_accumulation_names = solid_reference_accumulation_for_biot
    constraint_jacobian_derivative_names = 'solid_local_material_mass_d_jacobian solid_mineral_eos_d_jacobian'
    constraint_state_derivative_names = 'solid_local_material_mass_d_intrinsic_density_ratio solid_local_material_mass_d_volume_fraction solid_mineral_eos_d_intrinsic_density_ratio solid_mineral_eos_d_volume_fraction'
    volume_fraction_state_derivative_names = 'implicit_state_zero implicit_state_one'
    reference_specific_volume = 4
    intrinsic_specific_volume_name = solid_intrinsic_specific_volume_from_constraints
    intrinsic_skeleton_density_name = solid_intrinsic_density_from_constraints
    constraint_norm_name = solid_biot_constraint_norm
  []
  [total_stress]
    type = ADReferenceSolidStressMaterial
    equivalent_pressure = p
    biot_coefficient_name = solid_biot_coefficient
  []
  [water_mass_storage]
    type = ADBiotPressureStorageMaterial
    pressure = p
    reference_density = 1
    fluid_bulk_modulus = 3
    intrinsic_density_name = water_intrinsic_density
    reference_accumulation_name = water_reference_accumulation
    storage_rate_name = water_reference_storage_rate
  []
  [water_flux]
    type = ADBiotDarcyReferenceFluxMaterial
    pressure = p
    intrinsic_density_name = water_intrinsic_density
    permeability = 0.02
    viscosity = 1
    reference_mobility_name = water_mobility_ref
    reference_mass_flux_name = water_reference_mass_flux
  []
[]

[Kernels]
  [solid_momentum]
    type = ADReferenceSolidMomentum
    variable = ux
    component = 0
  []
  [solid_mass_storage]
    type = ADReferenceMaterialStorageRateTerm
    variable = solid_spatial_mass_ratio
    reference_storage_rate_name = solid_component_reference_storage_rate
  []
  [water_storage]
    type = ADReferenceMaterialStorageRateTerm
    variable = p
    reference_storage_rate_name = water_reference_storage_rate
  []
  [water_flux]
    type = ADReferenceComponentFluxTerm
    variable = p
    reference_flux_name = water_reference_mass_flux
  []
[]

[BCs]
  [ux]
    type = FunctionDirichletBC
    variable = ux
    boundary = 'left right'
    function = zero
  []
  [drained_pressure]
    type = DirichletBC
    variable = p
    boundary = right
    value = 0
  []
[]

[Preconditioning]
  [monolithic]
    type = SMP
    full = true
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  scheme = implicit-euler
  start_time = 0
  dt = 0.05
  end_time = 0.05
  nl_abs_tol = 1e-11
  nl_rel_tol = 1e-10
  nl_max_its = 20
[]

[Outputs]
  console = false
[]
