//* This file is part of the nonlinear-Biot implicit-AD application.
//* SPDX-License-Identifier: LGPL-2.1-or-later

#pragma once

#include "Material.h"
#include "RankTwoTensor.h"

/**
 * Prescribes a uniform diagonal deformation gradient for single-element
 * constitutive checks.
 *
 * F = diag(transverse_stretch, axial_stretch, out_of_plane_stretch), with the
 * Jacobian J = det F and F^{-1} written to the repo's kinematic property names
 * (solid_reference_F / solid_reference_J / solid_reference_F_inv).  Intended
 * for material-only tests that exercise a constitutive model without a
 * displacement solve.
 */
class ADConstantDeformationGradientMaterial : public Material
{
public:
  static InputParameters validParams();

  ADConstantDeformationGradientMaterial(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  const Real _transverse_stretch;
  const Real _axial_stretch;
  const Real _out_of_plane_stretch;
  const Real _rotation;
  const ADVariableValue * _axial_var; // optional time-ramped axial stretch

  ADMaterialProperty<RankTwoTensor> & _F;
  ADMaterialProperty<Real> & _J;
  ADMaterialProperty<RankTwoTensor> & _F_inv;
};
