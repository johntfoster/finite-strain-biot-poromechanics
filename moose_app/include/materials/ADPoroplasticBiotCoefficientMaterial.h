//* SPDX-License-Identifier: LGPL-2.1-or-later
#pragma once

#include "Material.h"

/** Closed-form coefficient at the mineral state for fixed plastic distention. */
class ADPoroplasticBiotCoefficientMaterial : public Material
{
public:
  static InputParameters validParams();
  ADPoroplasticBiotCoefficientMaterial(const InputParameters & parameters);

protected:
  void computeQpProperties() override;
  const ADVariableValue & _pressure;
  const ADMaterialProperty<Real> & _J;
  const ADMaterialProperty<Real> & _a_p;
  const Real _K, _Ks, _phi0;
  ADMaterialProperty<Real> & _biot;
  ADMaterialProperty<Real> & _elastic_biot;
  ADMaterialProperty<Real> & _delta;
};
