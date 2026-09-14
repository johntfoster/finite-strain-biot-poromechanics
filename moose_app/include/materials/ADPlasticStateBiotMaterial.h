//* This file is part of the nonlinear-Biot implicit-AD application.
//* SPDX-License-Identifier: LGPL-2.1-or-later

#pragma once

#include "Material.h"

/** Mass and mineral-equilibrium residuals at fixed plastic distention.
 * Supplies an independent two-state tangent for equations (63) and (68).
 */
class ADPlasticStateBiotMaterial : public Material
{
public:
  static InputParameters validParams();

  ADPlasticStateBiotMaterial(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  const ADMaterialProperty<Real> & _J;
  const ADVariableValue & _pressure;
  const ADVariableValue & _solid_spatial_mass_ratio;
  const MaterialProperty<Real> & _plastic_pore_allocation; // a^p (frozen, non-AD)

  const Real _skeleton_bulk_modulus;
  const Real _mineral_bulk_modulus;     // K_s
  const Real _reference_solid_volume_fraction; // phi_s0

  ADMaterialProperty<Real> & _intrinsic_density_ratio;   // ratio = rho_s/rho_s0
  ADMaterialProperty<Real> & _solid_volume_fraction;     // phi_s (incl. a^p)
  ADMaterialProperty<Real> & _material_mass_residual;
  ADMaterialProperty<Real> & _material_mass_intrinsic_density_derivative;
  ADMaterialProperty<Real> & _material_mass_volume_fraction_derivative;
  ADMaterialProperty<Real> & _material_mass_jacobian_derivative;
  ADMaterialProperty<Real> & _mineral_eos_residual;
  ADMaterialProperty<Real> & _mineral_eos_intrinsic_density_derivative;
  ADMaterialProperty<Real> & _mineral_eos_volume_fraction_derivative;
  ADMaterialProperty<Real> & _mineral_eos_jacobian_derivative;
};
