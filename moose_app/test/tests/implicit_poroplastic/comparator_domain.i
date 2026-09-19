# Fixed isotropic plastic history: the current mineral state is admissible
# while the virgin comparator has no stable tensile root. Stresses use GPa.
[Mesh]
  type = GeneratedMesh
  dim = 1
  nx = 1
[]
[Variables]
  [p]
    initial_condition = -1.35
  []
  [axial]
    initial_condition = 2
  []
[]
[Kernels]
  [p]
    type = Reaction
    variable = p
  []
  [axial]
    type = Reaction
    variable = axial
  []
[]
[BCs]
  [p]
    type = DirichletBC
    variable = p
    boundary = 'left right'
    value = -1.35
  []
  [axial]
    type = DirichletBC
    variable = axial
    boundary = 'left right'
    value = 2
  []
[]
[Materials]
  [F]
    type = ADConstantDeformationGradientMaterial
    axial_stretch_variable = axial
  []
  [plastic]
    type = ADImplicitPoroplasticBiotMaterial
    pressure = p
    shear_modulus = .75
    skeleton_bulk_modulus = 1
    mineral_bulk_modulus = 2.5
    reference_solid_volume_fraction = .9
    initial_plastic_distention = 2
    dp_cohesion = 1000
  []
[]
[AuxVariables]
  [B]
    family = MONOMIAL
    order = CONSTANT
  []
  [virgin]
    family = MONOMIAL
    order = CONSTANT
  []
  [available]
    family = MONOMIAL
    order = CONSTANT
  []
[]
[AuxKernels]
  [B]
    type = ADMaterialRealAux
    variable = B
    property = poroplastic_biot_coefficient
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [virgin]
    type = ADMaterialRealAux
    variable = virgin
    property = plastic_elastic_biot_coefficient
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [available]
    type = MaterialRealAux
    variable = available
    property = plastic_elastic_biot_coefficient_available
    execute_on = 'INITIAL TIMESTEP_END'
  []
[]
[Postprocessors]
  [B]
    type = ElementAverageValue
    variable = B
  []
  [virgin]
    type = ElementAverageValue
    variable = virgin
  []
  [available]
    type = ElementAverageValue
    variable = available
  []
[]
[Executioner]
  type = Steady
[]
[Outputs]
  console = false
  csv = true
[]
