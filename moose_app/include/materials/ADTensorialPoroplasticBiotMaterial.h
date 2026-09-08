//* This file is part of the nonlinear-Biot implicit-AD application.
//* SPDX-License-Identifier: LGPL-2.1-or-later

#pragma once

#include "Material.h"
#include "RankTwoTensor.h"

/**
 * Stateful finite-deformation multiplicative ideal Drucker-Prager return
 * mapping (the canonical inelastic update).
 *
 * The skeleton deformation is split multiplicatively, F = F^e F^p, with the
 * aggregate plastic factor F^p stored as history (det F^p = a^p the plastic
 * pore allocation).  Each step forms the elastic trial F^e_tr = F (F^p_n)^-1,
 * evaluates the drained skeleton and mineral response on F^e_tr, reconstructs
 * the single-prime Kirchhoff stress, and performs the ideal (constant-strength)
 * Drucker-Prager radial return on the deviatoric (isochoric) and scalar
 * (pore-allocation) mechanisms.  The isochoric part updates Fbar^p =
 * (a^p)^-1/3 F^p through the exact exponential of the symmetric flow
 * increment; the scalar allocation updates a^p = exp(beta Delta_gamma) a^p_n.
 * When the trial lies inside the yield surface the step is elastic and the
 * plastic state is frozen, giving immediate elastic unloading and
 * reloading re-yield.
 *
 * The elastic response on the trial uses the repository decoupled skeleton
 * potential and mineral compressibility so the first-loading limit (F^p = I)
 * reduces to the repository elastic response.  App-local; prototype with no
 * hardening.
 */
class ADTensorialPoroplasticBiotMaterial : public Material
{
public:
  static InputParameters validParams();

  ADTensorialPoroplasticBiotMaterial(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  void initQpStatefulProperties() override;

  void stressInvariants(const ADRankTwoTensor & tau, ADReal & p, ADReal & q) const;

  const ADMaterialProperty<RankTwoTensor> & _F;
  const ADMaterialProperty<Real> & _J;
  const ADVariableValue & _pressure;

  const Real _shear_modulus;   // drained isochoric shear modulus G
  const Real _skeleton_bulk;   // drained skeleton bulk modulus K_sk
  const Real _mineral_bulk;    // mineral bulk modulus K_s
  const Real _phi_s0;          // reference solid volume fraction
  const Real _friction_slope;  // M
  const Real _dilation_slope;  // beta
  const Real _cohesion;
  const bool _use_elastic_coefficient_in_trial;  // frozen-elastic reference

  // Stateful plastic history (plain, history-frozen for the AD tangent).
  MaterialProperty<RankTwoTensor> & _F_p;
  const MaterialProperty<RankTwoTensor> & _F_p_old;
  MaterialProperty<Real> & _a_p;
  const MaterialProperty<Real> & _a_p_old;

  ADMaterialProperty<Real> & _a_p_out;        // current a^p (AD)
  MaterialProperty<Real> & _a_p_value;        // current a^p as plain value
  ADMaterialProperty<Real> & _increment;      // Delta_gamma
  ADMaterialProperty<Real> & _yield_function; // f after return
  ADMaterialProperty<Real> & _mean_pressure;  // returned compressive mean p'
  ADMaterialProperty<Real> & _equiv_shear;    // returned equivalent shear q'
  ADMaterialProperty<Real> & _biot;           // B = 1 - (1 - B_el)/a^p
  ADMaterialProperty<Real> & _biot_elastic;   // B_el at total J (route-A base)
  ADMaterialProperty<RankTwoTensor> & _elastic_trial; // F^e_tr
  ADMaterialProperty<RankTwoTensor> & _kirchhoff;     // returned tau'
};
