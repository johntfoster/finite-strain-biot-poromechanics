#pragma once

#include "Material.h"

/**
 * Local elastic mineral state, constraint residuals and closed-form Biot coefficient.
 *
 * An AD material property stores the current solid partial density divided
 * by its reference value. The mineral EOS supplies the intrinsic solid density,
 * and the solid volume fraction follows from the material-mass identity. The
 * material publishes residual derivatives consumed by
 * ADConstrainedSkeletonBiotMaterial. Its state-only tangent supplies the production
 * coefficient; the general constrained material is an independent diagnostic.
 */
class ADLocalElasticMineralBiotMaterial : public Material
{
public:
  static InputParameters validParams();
  ADLocalElasticMineralBiotMaterial(const InputParameters & parameters);

protected:
  void initQpStatefulProperties() override { computeQpProperties(); }
  void computeQpProperties() override;

  const ADVariableValue & _pressure;
  const ADVariableValue * _pressure_dot;
  const ADMaterialProperty<Real> & _solid_spatial_mass_ratio;
  const ADMaterialProperty<Real> & _solid_spatial_mass_ratio_dot;
  const ADMaterialProperty<Real> & _J;
  const ADMaterialProperty<Real> & _J_dot;
  const Real _skeleton_bulk_modulus;
  const Real _mineral_bulk_modulus;
  const Real _reference_solid_volume_fraction;
  const Real _finite_difference_step;
  ADMaterialProperty<Real> & _biot_finite_difference;

  ADMaterialProperty<Real> & _intrinsic_density_ratio;
  ADMaterialProperty<Real> & _intrinsic_density_ratio_dot;
  ADMaterialProperty<Real> & _solid_volume_fraction;
  ADMaterialProperty<Real> & _solid_volume_fraction_dot;
  ADMaterialProperty<Real> & _biot_coefficient;
  ADMaterialProperty<Real> & _intrinsic_specific_volume_jacobian_tangent;
  ADMaterialProperty<Real> & _mineral_eos_residual;
  ADMaterialProperty<Real> & _material_mass_residual;
  ADMaterialProperty<Real> & _material_mass_intrinsic_density_derivative;
  ADMaterialProperty<Real> & _material_mass_volume_fraction_derivative;
  ADMaterialProperty<Real> & _material_mass_jacobian_derivative;
  ADMaterialProperty<Real> & _mineral_eos_intrinsic_density_derivative;
  ADMaterialProperty<Real> & _mineral_eos_volume_fraction_derivative;
  ADMaterialProperty<Real> & _mineral_eos_jacobian_derivative;
};
