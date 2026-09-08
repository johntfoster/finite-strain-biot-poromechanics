# Canonical implicit-coefficient feedback at nonzero pore pressure.
# Single element driven by the stateful multiplicative tensorial engine
# (ADTensorialPoroplasticBiotMaterial, M = 0.6, beta = 0.4) under drained
# uniaxial-strain compression to 20% axial compression (axial stretch ramped
# 1.0 -> 0.8 over t in [0,1]) at a prescribed NONZERO uniform pore pressure.
# The single-prime driving stress tau' = tau'' + (1 - B) p J I contains the
# pore-allocation-corrected coefficient B = 1 - (1 - B_el)/a^p (> B_el), so
# the coefficient and the plastic state are coupled: the returned pore
# allocation a^p and increment Delta_gamma carry the feedback of the corrected
# coefficient through the isotropic term (1 - B) p J I.
#
# A frozen-elastic reference pass (same run structure with the elastic
# coefficient B_el held in the single-prime reconstruction via
# use_elastic_coefficient_in_trial = true) is produced by the driver that
# curates this deck, isolating the coefficient feedback.
#
# SWEEP ANCHORS (substituted by validation/scripts/check_poroplastic_b_feedback.py):
#   'value = 1.5e8'  : uniform pore pressure p0
#   'y = \'1 0.8\''  : axial ramp target (axial stretch at end of load)

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
  [p_value]
    type = DirichletBC
    variable = p
    boundary = 'left right bottom top'
    value = 1.5e8
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
    x = '0 1'
    y = '1 0.8'
  []
[]

[AuxVariables]
  [axial_aux]
    family = MONOMIAL
    order = CONSTANT
  []
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
  [b]
    family = MONOMIAL
    order = CONSTANT
  []
[]

[AuxKernels]
  [axial_aux]
    type = FunctionAux
    variable = axial_aux
    function = axial
    execute_on = 'INITIAL TIMESTEP_BEGIN'
  []
  [b_el_aux]
    type = ADMaterialRealAux
    variable = b_el
    property = plastic_elastic_biot_coefficient
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
    type = ADTensorialPoroplasticBiotMaterial
    pressure = p
    shear_modulus = 0.75e9
    skeleton_bulk_modulus = 1.0e9
    mineral_bulk_modulus = 2.5e9
    reference_solid_volume_fraction = 0.9
    dp_friction_slope = 0.6
    dp_dilation_slope = 0.4
    dp_cohesion = 0.0
  []
[]

[Postprocessors]
  [compression]
    type = ElementAverageValue
    variable = axial_aux
  []
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
  [b_avg]
    type = ElementAverageValue
    variable = b
  []
  [p_avg]
    type = ElementAverageValue
    variable = p
  []
[]

[Executioner]
  type = Transient
  start_time = 0
  end_time = 1
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
