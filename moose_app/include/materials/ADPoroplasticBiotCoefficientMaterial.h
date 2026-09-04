//* This file is part of the nonlinear-Biot implicit-AD application.
//* SPDX-License-Identifier: LGPL-2.1-or-later

#pragma once

#include "Material.h"

/**
 * Plastic pore-allocation correction to the Biot coefficient (M3, route A).
 *
 * With the plastic pore allocation a^p dividing the solid volume fraction at
 * fixed referential partial density, the fixed-pressure, fixed-history tangent
 * gives the intrinsic specific volume v = Jbar/a^p and hence
 *   B = 1 - phi_s0 dv/dJ = 1 - (1 - B_el)/a^p,
 * where B_el is the elastic constrained Biot coefficient (read from the shared
 * elastic local material / closed-form oracle).  For a^p = 1 this reproduces the
 * elastic coefficient exactly (E-1 collapse).  App-local; does not modify the
 * shared local-system materials.
 */
class ADPoroplasticBiotCoefficientMaterial : public Material
{
public:
  static InputParameters validParams();

  ADPoroplasticBiotCoefficientMaterial(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  const ADMaterialProperty<Real> & _elastic_biot;
  const ADMaterialProperty<Real> & _a_p;

  ADMaterialProperty<Real> & _biot;
  ADMaterialProperty<Real> & _delta;
};
