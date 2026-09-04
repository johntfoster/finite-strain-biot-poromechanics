#pragma once

#include "Material.h"
#include "RankTwoTensor.h"

/**
 * Pressure-coupled effective skeleton stress with a volumetric barotropic law.
 *
 * The zero-pressure skeleton potential is
 *   W_0 = mu/2 (J^(-2/3) I_1 - 3) + K_sk/2 (ln J)^2.
 * The mineral-density closure uses
 *   q_s(J) = -K_sk ln(J)/(phi_s0 J),
 * so its small-strain Biot limit is B_0=1-K_sk/K_s.  The pressure-dependent
 * contribution is the fixed-equivalent-pressure derivative of the same
 * double-prime potential used by the constrained Biot transform.
 */
class ADVolumetricBarotropicSkeletonStressMaterial : public Material
{
public:
  static InputParameters validParams();

  ADVolumetricBarotropicSkeletonStressMaterial(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  const ADMaterialProperty<RankTwoTensor> & _F;
  const ADMaterialProperty<Real> & _J;
  const ADMaterialProperty<RankTwoTensor> & _F_inv;
  const ADVariableValue & _equivalent_pressure;
  const ADVariableValue * _equivalent_pressure_enrichment;

  const Real _shear_modulus;
  const Real _skeleton_bulk_modulus;
  const Real _mineral_bulk_modulus;
  const Real _reference_solid_volume_fraction;

  ADMaterialProperty<RankTwoTensor> & _effective_first_piola;
  ADMaterialProperty<Real> & _mineral_effective_pressure;
  ADMaterialProperty<Real> & _mineral_effective_pressure_jacobian_derivative;
};
