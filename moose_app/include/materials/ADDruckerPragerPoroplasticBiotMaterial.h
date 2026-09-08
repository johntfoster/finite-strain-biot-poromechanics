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
 * The coefficient entering the single-prime reconstruction is either an
 * external property (biot_coefficient_name, the default) or, with
 * biot_feedback = true, the implicit poroplastic coefficient
 *   B = 1 - (1 - B_el)/a^p
 * solved consistently with the return map: B enters the trial mean pressure
 * through (1-B) p J, the returned allocation a^p = exp(beta Delta_gamma)
 * corrects B, so the pair (Delta_gamma, B) is obtained by a fixed-point
 * iteration when the pore pressure p is nonzero.  When biot_feedback is on the
 * material also reports a frozen-elastic reference pass (the same return with
 * B held at the elastic coefficient B_el), whose outputs separate the effect
 * of the implicit-B feedback from the plastic mechanism itself.  The
 * prototypical scope (first loading from a virgin plastic state, drained
 * skeleton) is unchanged.
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
  const ADMaterialProperty<Real> * _biot_coefficient; // external B (default path)
  const ADMaterialProperty<Real> * _elastic_biot;     // elastic coefficient B_el (feedback)
  const ADVariableValue & _pressure;

  const bool _biot_feedback;      // solve B = 1 - (1 - B_el)/a^p with the return
  const Real _feedback_tol;       // fixed-point tolerance (raw value)
  const unsigned int _feedback_max_it;

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
  ADMaterialProperty<Real> & _biot_used;   // B used in the single-prime reconstruction
  // Frozen-elastic (B = B_el) reference pass, filled when biot_feedback is on.
  ADMaterialProperty<Real> & _a_p_ref;
  ADMaterialProperty<Real> & _dgamma_ref;
  ADMaterialProperty<Real> & _mean_p_ref;
  ADMaterialProperty<Real> & _q_ref;
  MaterialProperty<Real> & _a_p_value; // a^p as a plain value (frozen history)
};
