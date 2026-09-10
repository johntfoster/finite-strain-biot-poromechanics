# Algebraic material probe: active return at nonzero pressure and three
# distinct principal stretches. Both residuals retain state-dependent B.
[Mesh]
  type = GeneratedMesh
  dim = 1
  nx = 1
[]
[Variables]
  [axial]
    initial_condition = 0.85
  []
  [p]
    initial_condition = 0.1
  []
[]
[Materials]
  [F]
    type = ADConstantDeformationGradientMaterial
    axial_stretch_variable = axial
    transverse_stretch = 1.02
    out_of_plane_stretch = 0.98
  []
  [plastic]
    type = ADImplicitPoroplasticBiotMaterial
    pressure = p
    shear_modulus = 0.75
    skeleton_bulk_modulus = 1.0
    mineral_bulk_modulus = 2.5
    reference_solid_volume_fraction = 0.8
  []
  [axial_probe]
    type = ADParsedMaterial
    coupled_variables = axial
    material_property_names = 'plastic_equivalent_shear_stress poroplastic_biot_coefficient'
    property_name = axial_probe
    expression = 'axial+plastic_equivalent_shear_stress/1.0+poroplastic_biot_coefficient-1.3'
  []
  [pressure_probe]
    type = ADParsedMaterial
    coupled_variables = p
    material_property_names = 'plastic_mean_effective_pressure poroplastic_biot_coefficient plastic_pore_allocation'
    property_name = pressure_probe
    expression = 'p/1.0+plastic_mean_effective_pressure/1.0+poroplastic_biot_coefficient+plastic_pore_allocation-1.85'
  []
[]
[Kernels]
  [axial]
    type = ADMaterialPropertyResidual
    variable = axial
    property = axial_probe
  []
  [pressure]
    type = ADMaterialPropertyResidual
    variable = p
    property = pressure_probe
  []
[]
[Preconditioning]
  [full]
    type = SMP
    full = true
  []
[]
[Executioner]
  type = Steady
  solve_type = NEWTON
  nl_abs_tol = 1e-10
  nl_rel_tol = 1e-10
  nl_max_its = 20
[]
[Outputs]
  console = false
[]
