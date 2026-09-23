//* SPDX-License-Identifier: LGPL-2.1-or-later
#pragma once
#include "Material.h"

/** Mineral and pore-volume rates including the exponential plastic increment. */
class ADPoroplasticPoreVolumeMaterial : public Material
{
public:
  static InputParameters validParams();
  ADPoroplasticPoreVolumeMaterial(const InputParameters & parameters);
protected:
  void initQpStatefulProperties() override { computeQpProperties(); }
  void computeQpProperties() override;
  const ADVariableValue & _p;
  const ADVariableValue & _p_dot;
  const ADMaterialProperty<Real> & _rho;
  const ADMaterialProperty<Real> & _rho_dot;
  const ADMaterialProperty<Real> & _J;
  const ADMaterialProperty<Real> & _J_dot;
  const ADMaterialProperty<Real> & _ratio;
  const ADMaterialProperty<Real> & _ap;
  const ADMaterialProperty<Real> & _gamma;
  const Real _K, _Ks, _phi0, _beta;
  ADMaterialProperty<Real> & _phi;
  ADMaterialProperty<Real> & _phi_dot;
  ADMaterialProperty<Real> & _eos;
  ADMaterialProperty<Real> & _plastic_storage;
};
