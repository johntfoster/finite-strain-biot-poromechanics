# Quadrature-point samples for independent storage-rate and mineral checks.
[Materials]
  [sample_pressure]
    type = ADParsedMaterial
    coupled_variables = p
    property_name = sample_pressure
    expression = p
  []
  [sample_density]
    type = ADParsedMaterial
    coupled_variables = solid_spatial_mass_ratio
    property_name = sample_density
    expression = solid_spatial_mass_ratio
  []
  [sample_values]
    type = MaterialADConverter
    ad_props_in = 'sample_pressure sample_density solid_reference_J solid_reference_J_dot plastic_pore_allocation plastic_multiplier_increment implicit_plastic_density_ratio solid_volume_fraction solid_volume_fraction_dot water_reference_storage_rate plastic_pore_volume_rate poroplastic_biot_coefficient plastic_elastic_biot_coefficient'
    reg_props_out = 'check_p check_rho check_J check_Jdot check_ap check_gamma check_ratio check_phi check_phidot check_storage check_plastic_rate check_B check_Bel'
  []
[]
[VectorPostprocessors]
  [storage_samples]
    type = ElementMaterialSampler
    property = 'check_p check_rho check_J check_Jdot check_ap check_gamma check_ratio check_phi check_phidot check_storage check_plastic_rate check_B check_Bel'
    execute_on = 'INITIAL TIMESTEP_END'
  []
[]
