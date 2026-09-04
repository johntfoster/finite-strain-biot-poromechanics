//* This file is part of the nonlinear-Biot implicit-AD application
//* https://github.com/...
//* SPDX-License-Identifier: LGPL-2.1-or-later

#pragma once

#include "Material.h"
#include "RankTwoTensor.h"

/**
 * Drucker-Prager-type poroplastic return mapping on the single-prime Kirchhoff
 * stress.
 *
 * The single-prime Kirchhoff stress is reconstructed from the repo double-prime
 * first Piola stress and the current (implicit) Biot coefficient,
 *   P' = P'' + (1-B) p J F^{-T},   tau' = P' F^T,
 * i.e. tau' = tau'' + (1-B) p J I.  A Drucker-Prager surface
 *   f = q' - M p' <= 0,   M = mu + beta,
 * with flow potential g = q' - beta p' is integrated by the exact ideal-plastic
 * radial return (the backward-Euler limit for constant strength), giving the
 * scalar plastic increment Delta_gamma and the plastic pore allocation
 *   a^p = exp(beta Delta_gamma),   phi_s = phi_s0/a^p (volumetric allocation).
 *
 * Rate independence is retained exactly (no viscous regularization): the yield
 * branch is the closed-form discrete consistency f(tau'(Delta_gamma))=0.
 * Inactive branch: Delta_gamma = 0, a^p = 1, stress = trial (elastic).
 *
 * Prototype scope (documented): valid for first loading from a virgin plastic
 * state (F^p_n = I) on the drained neo-Hookean skeleton; elastic moduli in the
 * return map are the drained G and K_sk; the coupling of the plastic state back
 * into the constrained Biot coefficient is a follow-up milestone.
 */
class ADDruckerPragerPoroplasticBiotMaterial : public Material
{
public:
  static InputParameters validParams();

  ADDruckerPragerPoroplasticBiotMaterial(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  // Compressive-positive mean and von Mises invariant of a symmetric stress.
  void stressInvariants(const ADRankTwoTensor & tau, ADReal & p, ADReal & q) const;

  const ADMaterialProperty<RankTwoTensor> & _F;
  const ADMaterialProperty<Real> & _J;
  const ADMaterialProperty<RankTwoTensor> & _effective_first_piola;
  const ADMaterialProperty<Real> & _biot_coefficient;
  const ADVariableValue & _pressure;

  const Real _shear_modulus;   // drained isochoric shear modulus G
  const Real _skeleton_bulk;   // drained skeleton bulk modulus K_sk
  const Real _friction_slope;  // M = mu + beta
  const Real _dilation_slope;  // beta
  const Real _cohesion;        // cohesion (zero for cohesionless)

  ADMaterialProperty<Real> & _plastic_pore_allocation;   // a^p
  ADMaterialProperty<Real> & _plastic_multiplier_increment; // Delta_gamma
  ADMaterialProperty<Real> & _yield_function;            // f (after return)
  ADMaterialProperty<Real> & _mean_effective_pressure;   // p' (compressive +)
  ADMaterialProperty<Real> & _equivalent_shear_stress;   // q'
  ADMaterialProperty<RankTwoTensor> & _effective_kirchhoff_stress; // tau' returned
};
