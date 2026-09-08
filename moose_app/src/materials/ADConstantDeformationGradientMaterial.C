//* This file is part of the nonlinear-Biot implicit-AD application.
//* SPDX-License-Identifier: LGPL-2.1-or-later

#include "ADConstantDeformationGradientMaterial.h"

registerMooseObject("MulticomponentReactiveFlowApp", ADConstantDeformationGradientMaterial);

InputParameters
ADConstantDeformationGradientMaterial::validParams()
{
  InputParameters params = Material::validParams();
  params.addClassDescription(
      "Prescribes a uniform diagonal deformation gradient for single-element constitutive "
      "checks: F = diag(transverse, axial, out_of_plane), with J = det F and F^{-1} written "
      "to the repo kinematic property names.");
  params.addParam<Real>("transverse_stretch", 1.0, "In-plane transverse stretch F_xx.");
  params.addParam<Real>("axial_stretch", 1.0, "Axial stretch F_yy.");
  params.addCoupledVar("axial_stretch_variable",
                       "Optional auxiliary variable giving the axial stretch F_yy; overrides "
                       "the axial_stretch parameter for time-ramped material tests.");
  params.addParam<Real>("out_of_plane_stretch", 1.0, "Out-of-plane stretch F_zz.");
  params.addParam<MaterialPropertyName>(
      "deformation_gradient_name", "solid_reference_F", "Output deformation gradient F.");
  params.addParam<MaterialPropertyName>(
      "jacobian_name", "solid_reference_J", "Output Jacobian J_s.");
  params.addParam<MaterialPropertyName>(
      "inverse_deformation_gradient_name", "solid_reference_F_inv", "Output F^{-1}.");
  return params;
}

ADConstantDeformationGradientMaterial::ADConstantDeformationGradientMaterial(
    const InputParameters & parameters)
  : Material(parameters),
    _transverse_stretch(getParam<Real>("transverse_stretch")),
    _axial_stretch(getParam<Real>("axial_stretch")),
    _out_of_plane_stretch(getParam<Real>("out_of_plane_stretch")),
    _axial_var(isCoupled("axial_stretch_variable")
                   ? &coupledValue("axial_stretch_variable")
                   : nullptr),
    _F(declareADProperty<RankTwoTensor>(
        getParam<MaterialPropertyName>("deformation_gradient_name"))),
    _J(declareADProperty<Real>(getParam<MaterialPropertyName>("jacobian_name"))),
    _F_inv(declareADProperty<RankTwoTensor>(
        getParam<MaterialPropertyName>("inverse_deformation_gradient_name")))
{
}

void
ADConstantDeformationGradientMaterial::computeQpProperties()
{
  const Real axial =
      _axial_var ? (*_axial_var)[_qp] : _axial_stretch;
  RankTwoTensor F;
  F(0, 0) = _transverse_stretch;
  F(1, 1) = axial;
  F(2, 2) = _out_of_plane_stretch;
  _F[_qp] = F;

  const Real J = _transverse_stretch * axial * _out_of_plane_stretch;
  if (J <= 0.0)
    mooseError(name(), ": requires J_s>0.");
  _J[_qp] = J;

  RankTwoTensor Fi;
  Fi(0, 0) = 1.0 / _transverse_stretch;
  Fi(1, 1) = 1.0 / axial;
  Fi(2, 2) = 1.0 / _out_of_plane_stretch;
  _F_inv[_qp] = Fi;
}
