//* This file is part of the nonlinear-Biot implicit-AD application.
//* SPDX-License-Identifier: LGPL-2.1-or-later

#pragma once

#include "Material.h"

/**
 * Local-state value/residual provider for the fixed-history, fixed-pressure
 * Biot tangent of the active poroplastic branch.
 *
 * The provider mirrors the elastic `ADLocalElasticMineralBiotMaterial`
 * residual provider, but carries the (frozen) plastic pore allocation a^p into
 * the solid volume fraction through the route-A mapping
 *   phi_s = phi_s0 * r / (ratio * a^p),
 * where ratio = exp((p + q_s(J))/K_s) is the elastic intrinsic density ratio
 * (isochoric plastic flow leaves the intrinsic density elastic) and a^p is
 * read as a NON-AD value so that it is history-frozen in the local tangent.
 * It publishes the two local residuals (material-mass definition and mineral
 * EOS) and their partial derivatives with respect to the implicit state
 * y = (ratio, phi_s) and with respect to J at fixed referential solid mass,
 * exactly in the form consumed by `ADConstrainedSkeletonBiotMaterial`.  The
 * general dense AD solve then returns the coefficient
 *   B = 1 - phi_s0 d(Jbar/a^p)/dJ|_{p, J rho_s, a^p}
 * which is the general-path (pure-AD) counterpart of the reduced closed form
 * B = 1 - (1 - B_el)/a^p.
 *
 * App-local (not in moose/sync_manifest.json); prototype scope matches the
 * first-loading poroplastic material.
 */
class ADPlasticStateBiotMaterial : public Material
{
public:
  static InputParameters validParams();

  ADPlasticStateBiotMaterial(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  const ADMaterialProperty<Real> & _J;
  const ADMaterialProperty<Real> & _mineral_effective_pressure;
  const ADMaterialProperty<Real> & _mineral_effective_pressure_jacobian_derivative;
  const ADVariableValue & _pressure;
  const ADVariableValue & _solid_spatial_mass_ratio;
  const MaterialProperty<Real> & _plastic_pore_allocation; // a^p (frozen, non-AD)

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
