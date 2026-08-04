mesh_nx := 80
pressure_max_gpa := 0.04
k_infinity_gpa := 51.0527461946679
crack_compliance_per_gpa := 0.014981038312398408
closure_pressure_gpa := 0.013368859928405467
unjacketed_bulk_modulus_gpa := 85.3

!include includes/mesh_q2_1d.i
!include includes/fields_q2_eg.i

[Functions]
  [zero]
    type = ParsedFunction
    expression = '0'
  []
  [mean_pressure_exact]
    type = ParsedFunction
    expression = '${pressure_max_gpa}*x'
  []
  [solid_jacobian_exact]
    type = ParsedFunction
    symbol_names = 'pmax kinf cc pc'
    symbol_values = '${pressure_max_gpa} ${k_infinity_gpa} ${crack_compliance_per_gpa} ${closure_pressure_gpa}'
    expression = 'exp(-(pmax*x/kinf+cc*pc*(1-exp(-(pmax*x)/pc))))'
  []
  [solid_volume_fraction_exact]
    type = ParsedFunction
    symbol_names = 'pmax kinf cc pc ks'
    symbol_values = '${pressure_max_gpa} ${k_infinity_gpa} ${crack_compliance_per_gpa} ${closure_pressure_gpa} ${unjacketed_bulk_modulus_gpa}'
    expression = 'exp(-(pmax*x)/ks)/exp(-(pmax*x/kinf+cc*pc*(1-exp(-(pmax*x)/pc))))'
  []
[]

[ICs]
  [ux_ic]
    type = FunctionIC
    variable = ux
    function = zero
  []
  [solid_jacobian_ic]
    type = FunctionIC
    variable = solid_reference_J_state
    function = solid_jacobian_exact
  []
  [equivalent_pressure_ic]
    type = FunctionIC
    variable = equivalent_pressure
    function = zero
  []
  [equivalent_pressure_enr_ic]
    type = FunctionIC
    variable = equivalent_pressure_enr
    function = zero
  []
  [mean_pressure_ic]
    type = FunctionIC
    variable = mean_effective_pressure_state
    function = mean_pressure_exact
  []
  [solid_volume_fraction_ic]
    type = FunctionIC
    variable = solid_volume_fraction_state
    function = solid_volume_fraction_exact
  []
[]

!include includes/solid_kinematics_and_pressure.i

[Materials]
  [solid_component_reference_accumulation]
    type = ADGenericConstantMaterial
    prop_names = solid_component_reference_accumulation
    prop_values = 1
  []
  [solid_volume_fraction]
    type = ADDerivativeParsedMaterial
    coupled_variables = 'mean_effective_pressure_state solid_volume_fraction_state'
    material_property_names = solid_reference_J
    property_name = solid_volume_fraction
    expression = 'solid_volume_fraction_state+0*mean_effective_pressure_state+0*solid_reference_J'
    additional_derivative_symbols = solid_reference_J
    derivative_order = 2
    enable_jit = true
  []
  [hydrostatic_skeleton_constraint]
    type = ADDerivativeParsedMaterial
    coupled_variables = 'mean_effective_pressure_state solid_volume_fraction_state'
    material_property_names = 'solid_reference_J equivalent_pressure_total'
    property_name = hydrostatic_skeleton_constraint
    constant_names = 'kinf cc pc'
    constant_expressions = '${k_infinity_gpa} ${crack_compliance_per_gpa} ${closure_pressure_gpa}'
    expression = 'log(solid_reference_J)+mean_effective_pressure_state/kinf+cc*pc*(1-exp(-mean_effective_pressure_state/pc))+0*solid_volume_fraction_state+0*equivalent_pressure_total'
    additional_derivative_symbols = solid_reference_J
    derivative_order = 2
    enable_jit = true
  []
  [intrinsic_grain_volume_constraint]
    type = ADDerivativeParsedMaterial
    coupled_variables = 'mean_effective_pressure_state solid_volume_fraction_state'
    material_property_names = 'solid_reference_J equivalent_pressure_total'
    property_name = intrinsic_grain_volume_constraint
    constant_names = ks
    constant_expressions = '${unjacketed_bulk_modulus_gpa}'
    expression = 'solid_reference_J*solid_volume_fraction_state-exp(-mean_effective_pressure_state/ks)+0*equivalent_pressure_total'
    additional_derivative_symbols = solid_reference_J
    derivative_order = 2
    enable_jit = true
  []
  [constrained_biot]
    type = ADConstrainedSkeletonBiotMaterial
    constraint_residual_names = 'hydrostatic_skeleton_constraint intrinsic_grain_volume_constraint'
    implicit_state_symbols = 'mean_effective_pressure_state solid_volume_fraction_state'
    aggregate_solid_volume_fraction_name = solid_volume_fraction
    skeleton_component_reference_accumulation_names = solid_component_reference_accumulation
    reference_specific_volume = 1
  []
  [drained_bulk_modulus]
    type = ADParsedMaterial
    coupled_variables = mean_effective_pressure_state
    property_name = drained_bulk_modulus_gpa
    constant_names = 'kinf cc pc'
    constant_expressions = '${k_infinity_gpa} ${crack_compliance_per_gpa} ${closure_pressure_gpa}'
    expression = '1/(1/kinf+cc*exp(-mean_effective_pressure_state/pc))'
  []
  [classical_biot]
    type = ADParsedMaterial
    material_property_names = drained_bulk_modulus_gpa
    property_name = classical_biot_coefficient
    constant_names = ks
    constant_expressions = '${unjacketed_bulk_modulus_gpa}'
    expression = '1-drained_bulk_modulus_gpa/ks'
  []
[]

[AuxKernels]
  [biot_output]
    type = ADMaterialRealAux
    variable = biot_coefficient_out
    property = solid_biot_coefficient
    execute_on = INITIAL
  []
  [biot_classical_output]
    type = ADMaterialRealAux
    variable = biot_classical_out
    property = classical_biot_coefficient
    execute_on = INITIAL
  []
  [drained_modulus_output]
    type = ADMaterialRealAux
    variable = drained_bulk_modulus_out
    property = drained_bulk_modulus_gpa
    execute_on = INITIAL
  []
  [constraint_norm_output]
    type = ADMaterialRealAux
    variable = constraint_norm_out
    property = solid_biot_constraint_norm
    execute_on = INITIAL
  []
[]

[VectorPostprocessors]
  [pressure_path]
    type = LineValueSampler
    variable = 'mean_effective_pressure_state drained_bulk_modulus_out biot_coefficient_out biot_classical_out constraint_norm_out'
    start_point = '0.00625 0 0'
    end_point = '0.99375 0 0'
    num_points = 80
    sort_by = x
    execute_on = INITIAL
  []
[]

[Problem]
  solve = false
[]

[Executioner]
  type = Steady
[]

[Outputs]
  console = true
  [csv]
    type = CSV
    execute_on = final
  []
[]
