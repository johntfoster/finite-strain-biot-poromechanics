//* SPDX-License-Identifier: LGPL-2.1-or-later
#pragma once

#include "Material.h"
#include "RankTwoTensor.h"

/** Isotropic multiplicative poroplasticity with a constrained mineral tangent.
 * The current symmetric flow increment and yield consistency are solved together.
 * Only previous-step history is stored without AD derivatives.
 */
class ADImplicitPoroplasticBiotMaterial : public Material
{
public:
  static InputParameters validParams();
  ADImplicitPoroplasticBiotMaterial(const InputParameters & parameters);

protected:
  void computeQpProperties() override;
  void initQpStatefulProperties() override;
  const ADMaterialProperty<RankTwoTensor> & _F;
  const ADVariableValue & _pressure;
  const Real _G, _K, _Ks, _phi0, _M, _beta, _cohesion, _hardening;
  const bool _frozen_reference;
  const bool _compute_elastic;
  const Real _initial_ap;
  MaterialProperty<RankTwoTensor> & _Fp_history;
  const MaterialProperty<RankTwoTensor> & _Fp_old;
  MaterialProperty<Real> & _accumulated_history;
  const MaterialProperty<Real> & _accumulated_old;
  ADMaterialProperty<Real> & _accumulated;
  ADMaterialProperty<RankTwoTensor> & _Fp;
  ADMaterialProperty<RankTwoTensor> & _Fe;
  ADMaterialProperty<RankTwoTensor> & _tau;
  ADMaterialProperty<RankTwoTensor> & _P;
  ADMaterialProperty<Real> & _ap;
  ADMaterialProperty<Real> & _B;
  ADMaterialProperty<Real> & _B_el;
  MaterialProperty<Real> & _B_el_available;
  ADMaterialProperty<Real> & _ratio;
  ADMaterialProperty<Real> & _phi;
  ADMaterialProperty<Real> & _gamma;
  ADMaterialProperty<Real> & _yield;
  ADMaterialProperty<Real> & _flow_error;
  ADMaterialProperty<Real> & _mean;
  ADMaterialProperty<Real> & _q;
  ADMaterialProperty<Real> & _mass_error;
};
