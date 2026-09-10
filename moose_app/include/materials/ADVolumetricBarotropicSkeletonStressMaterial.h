#pragma once

#include "Material.h"
#include "RankTwoTensor.h"

/**
 * Pressure-coupled effective skeleton stress with a volumetric barotropic law.
 *
 * The zero-pressure skeleton potential is
 *   W_0 = mu/2 (J^(-2/3) I_1 - 3) + K_sk/2 (ln J)^2.
 * The matched mineral law gives the implicit volume z=barJ through
 * Ks ln(z)+(1-K/(phi_s0 Ks)) p z-K/phi_s0 ln(J)=0.
 * The pressure-dependent potential is phi_s0(1-K/(phi_s0 Ks))(pz)^2/(2Ks).
 * Its fixed-pressure derivative supplies the double-prime stress, retaining
 * the AD dependence of the implicit mineral volume.
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
