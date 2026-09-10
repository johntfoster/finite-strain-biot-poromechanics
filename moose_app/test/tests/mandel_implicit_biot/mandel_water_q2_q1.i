# Water-filled Mandel consolidation on the solid reference configuration.
# The quarter-domain uses Q2 displacement and continuous Q1 pore pressure.
# The solid partial density is solved globally; mineral state and Biot coefficient are local outputs.

mesh_nx := 20
mesh_ny := 2
load_pa := 1e5
stiffness_scale_pa := 1e9
deformation_scale := '${fparse load_pa/stiffness_scale_pa}'
initial_solid_volume_fraction := 0.9
skeleton_bulk_modulus_pa := '${fparse 1.0*stiffness_scale_pa}'
skeleton_shear_modulus_pa := '${fparse 0.75*stiffness_scale_pa}'
mineral_bulk_modulus_pa := '${fparse 2.5*stiffness_scale_pa}'
water_bulk_modulus_pa := '${fparse 8.0*stiffness_scale_pa}'
water_density_kg_m3 := 1000
water_viscosity_pa_s := 1e-3
water_permeability_m2 := '${fparse 1.5*water_viscosity_pa_s/stiffness_scale_pa}'
time_sequence := '0 0.002 0.006 0.014 0.03 0.046 0.062 0.078 0.094 0.11 0.126 0.142 0.158 0.174 0.19 0.206 0.222 0.238 0.254 0.27 0.286 0.302 0.318 0.334 0.35 0.366 0.382 0.398 0.414 0.43 0.446 0.462 0.478 0.494 0.51 0.526 0.542 0.558 0.574 0.59 0.606 0.622 0.638 0.654 0.67 0.686 0.702'

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
    type = PiecewiseLinear
    x = '0 0.002 0.006 0.014 0.03 0.046 0.062 0.078 0.094 0.11 0.126 0.142 0.158 0.174 0.19 0.206 0.222 0.238 0.254 0.27 0.286 0.302 0.318 0.334 0.35 0.366 0.382 0.398 0.414 0.43 0.446 0.462 0.478 0.494 0.51 0.526 0.542 0.558 0.574 0.59 0.606 0.622 0.638 0.654 0.67 0.686 0.702'
    y = '${fparse -0.0419771815701955*deformation_scale} ${fparse -0.0427302686674154*deformation_scale} ${fparse -0.0434127120839256*deformation_scale} ${fparse -0.0442886698279412*deformation_scale} ${fparse -0.0455091812735037*deformation_scale} ${fparse -0.0464596499348389*deformation_scale} ${fparse -0.0472682456066736*deformation_scale} ${fparse -0.0479747485683798*deformation_scale} ${fparse -0.0485971093691553*deformation_scale} ${fparse -0.0491467002296859*deformation_scale} ${fparse -0.0496323879221514*deformation_scale} ${fparse -0.0500616974080911*deformation_scale} ${fparse -0.0504411980354753*deformation_scale} ${fparse -0.050776675278685*deformation_scale} ${fparse -0.0510732377476134*deformation_scale} ${fparse -0.0513353999490549*deformation_scale} ${fparse -0.0515671523222325*deformation_scale} ${fparse -0.0517720223248796*deformation_scale} ${fparse -0.051953128215522*deformation_scale} ${fparse -0.0521132265396356*deformation_scale} ${fparse -0.0522547540923857*deformation_scale} ${fparse -0.0523798650098385*deformation_scale} ${fparse -0.0524904635566767*deformation_scale} ${fparse -0.0525882331103904*deformation_scale} ${fparse -0.052674661783343*deformation_scale} ${fparse -0.0527510650727585*deformation_scale} ${fparse -0.0528186058833959*deformation_scale} ${fparse -0.0528783122276706*deformation_scale} ${fparse -0.0529310928726318*deformation_scale} ${fparse -0.0529777511719526*deformation_scale} ${fparse -0.0530189972934639*deformation_scale} ${fparse -0.0530554590283425*deformation_scale} ${fparse -0.0530876913464769*deformation_scale} ${fparse -0.0531161848434476*deformation_scale} ${fparse -0.0531413732076924*deformation_scale} ${fparse -0.0531636398215089*deformation_scale} ${fparse -0.0531833235963676*deformation_scale} ${fparse -0.0532007241313516*deformation_scale} ${fparse -0.0532161062732375*deformation_scale} ${fparse -0.0532297041476256*deformation_scale} ${fparse -0.0532417247224745*deformation_scale} ${fparse -0.0532523509582798*deformation_scale} ${fparse -0.0532617445928445*deformation_scale} ${fparse -0.0532700486030276*deformation_scale} ${fparse -0.0532773893809391*deformation_scale} ${fparse -0.0532838786577052*deformation_scale} ${fparse -0.0532896152040841*deformation_scale}'
  []
[]

[Materials]
  [solid_kinematics]
    type = ADSolidReferenceKinematics
    displacements = 'ux uy'
  []
  [solid_spatial_mass]
    type = ADBinarySolidSpatialMassMaterial
    solid_spatial_mass_ratio = solid_spatial_mass_ratio
  []
  [double_prime_skeleton_stress]
    type = ADVolumetricBarotropicSkeletonStressMaterial
    equivalent_pressure = p
    shear_modulus = ${skeleton_shear_modulus_pa}
    skeleton_bulk_modulus = ${skeleton_bulk_modulus_pa}
    mineral_bulk_modulus = ${mineral_bulk_modulus_pa}
    reference_solid_volume_fraction = ${initial_solid_volume_fraction}
  []
  [local_solid_state]
    type = ADLocalElasticMineralBiotMaterial
    finite_difference_step = 1e-5
    biot_finite_difference_name = biot_fixed_pressure_fd_check
    skeleton_bulk_modulus = ${skeleton_bulk_modulus_pa}
    pressure = p
    solid_spatial_mass_ratio = solid_spatial_mass_ratio
    mineral_bulk_modulus = ${mineral_bulk_modulus_pa}
    reference_solid_volume_fraction = ${initial_solid_volume_fraction}
    biot_coefficient_name = solid_biot_coefficient
    intrinsic_specific_volume_jacobian_tangent_name = elastic_specific_volume_jacobian_tangent
  []
  [solid_reference_accumulation_for_biot]
    type = ADParsedMaterial
    material_property_names = solid_component_reference_accumulation
    property_name = solid_reference_accumulation_for_biot
    constant_names = phi0
    constant_expressions = ${initial_solid_volume_fraction}
    expression = 'phi0*solid_component_reference_accumulation'
  []
  [implicit_state_selectors]
    type = ADGenericConstantMaterial
    prop_names = 'implicit_state_zero implicit_state_one'
    prop_values = '0 1'
  []
  [constrained_biot_state]
    type = ADConstrainedSkeletonBiotMaterial
    biot_coefficient_name = solid_biot_implicit_diagnostic
    constraint_residual_names = 'solid_local_material_mass_constraint solid_mineral_eos_constraint'
    implicit_state_symbols = 'solid_intrinsic_density_ratio solid_volume_fraction'
    constraint_residual_scales = '1 1'
    aggregate_solid_volume_fraction_name = solid_volume_fraction
    skeleton_component_reference_accumulation_names = solid_reference_accumulation_for_biot
    constraint_jacobian_derivative_names = 'solid_local_material_mass_d_jacobian solid_mineral_eos_d_jacobian'
    constraint_state_derivative_names = 'solid_local_material_mass_d_intrinsic_density_ratio solid_local_material_mass_d_volume_fraction solid_mineral_eos_d_intrinsic_density_ratio solid_mineral_eos_d_volume_fraction'
    volume_fraction_state_derivative_names = 'implicit_state_zero implicit_state_one'
    reference_specific_volume = '${fparse 1/initial_solid_volume_fraction}'
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
  [biot_analytic_error]
    type = ADParsedMaterial
    material_property_names = 'solid_biot_coefficient solid_biot_implicit_diagnostic'
    property_name = biot_analytic_error
    expression = 'solid_biot_coefficient-solid_biot_implicit_diagnostic'
  []
  [biot_fixed_pressure_fd_error]
    type = ADParsedMaterial
    material_property_names = 'solid_biot_coefficient biot_fixed_pressure_fd_check'
    property_name = biot_fixed_pressure_fd_error
    expression = 'solid_biot_coefficient-biot_fixed_pressure_fd_check'
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
    type = ADReferenceSolidMomentum
    variable = ux
    component = 0
  []
  [solid_y]
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
    type = ADReferenceMaterialStorageRateTerm
    variable = p
    reference_storage_rate_name = water_reference_storage_rate
    scale = '${fparse 1/water_density_kg_m3}'
  []
  [water_flux]
    type = ADReferenceComponentFluxTerm
    variable = p
    reference_flux_name = water_reference_mass_flux
    scale = '${fparse 1/water_density_kg_m3}'
  []
[]

[AuxKernels]
  [biot_coefficient_output]
    type = ADMaterialRealAux
    variable = biot_coefficient_state
    property = solid_biot_coefficient
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [solid_intrinsic_density_ratio_output]
    type = ADMaterialRealAux
    variable = solid_intrinsic_density_ratio_state
    property = solid_intrinsic_density_ratio
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
    rank_two_tensor = reference_solid_total_first_piola
    index_i = 1
    index_j = 1
    use_displaced_mesh = false
  []
  [biot_average]
    type = ADElementAverageMaterialProperty
    mat_prop = solid_biot_coefficient
  []
  [biot_minimum]
    type = ADElementExtremeMaterialProperty
    mat_prop = solid_biot_coefficient
    value_type = min
  []
  [biot_maximum]
    type = ADElementExtremeMaterialProperty
    mat_prop = solid_biot_coefficient
    value_type = max
  []
  [biot_analytic_error_l2]
    type = ADMaterialScalarL2Error
    property = biot_analytic_error
    function = zero
  []
  [biot_fixed_pressure_fd_error_l2]
    type = ADMaterialScalarL2Error
    property = biot_fixed_pressure_fd_error
    function = zero
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
  automatic_scaling = true
  compute_scaling_once = false
  nl_abs_tol = 1e-7
  nl_rel_tol = 1e-9
  nl_max_its = 30
  start_time = 0
  end_time = 0.702
  [TimeStepper]
    type = TimeSequenceStepper
    time_sequence = ${time_sequence}
  []
[]

[Outputs]
  execute_on = TIMESTEP_END
  csv = true
  console = false
[]
