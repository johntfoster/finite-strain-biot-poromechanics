#include "ADSolidReferenceKinematics.h"

#include "metaphysicl/raw_type.h"

registerMooseObject("MulticomponentReactiveFlowApp", ADSolidReferenceKinematics);

InputParameters
ADSolidReferenceKinematics::validParams()
{
  InputParameters params = Material::validParams();
  params.addClassDescription("Computes dimension-aware solid-reference kinematics F, J, F^{-1}, "
                             "and J F^{-1} for solid-reference pull-backs.");
  params.addCoupledVar("displacements", "Solid displacement components in reference coordinates.");
  params.addParam<MaterialPropertyName>("deformation_gradient_name",
                                        "solid_reference_F",
                                        "Material property name for F.");
  params.addParam<MaterialPropertyName>(
      "jacobian_name", "solid_reference_J", "Material property name for J=det(F).");
  params.addParam<MaterialPropertyName>("jacobian_dot_name",
                                        "solid_reference_J_dot",
                                        "Material property name for the material time rate of J.");
  params.addParam<MaterialPropertyName>("inverse_deformation_gradient_name",
                                        "solid_reference_F_inv",
                                        "Material property name for F^{-1}.");
  params.addParam<MaterialPropertyName>("jacobian_inverse_deformation_gradient_name",
                                        "solid_reference_J_F_inv",
                                        "Material property name for J F^{-1}.");
  return params;
}

ADSolidReferenceKinematics::ADSolidReferenceKinematics(const InputParameters & parameters)
  : Material(parameters),
    _ndisp(coupledComponents("displacements")),
    _F(declareADProperty<RankTwoTensor>(getParam<MaterialPropertyName>("deformation_gradient_name"))),
    _J(declareADProperty<Real>(getParam<MaterialPropertyName>("jacobian_name"))),
    _J_dot(declareADProperty<Real>(getParam<MaterialPropertyName>("jacobian_dot_name"))),
    _F_inv(declareADProperty<RankTwoTensor>(
        getParam<MaterialPropertyName>("inverse_deformation_gradient_name"))),
    _J_F_inv(declareADProperty<RankTwoTensor>(
        getParam<MaterialPropertyName>("jacobian_inverse_deformation_gradient_name")))
{
  if (_ndisp > Moose::dim)
    paramError("displacements", "The number of displacement components cannot exceed mesh dimension.");
  if (_ndisp > 3)
    paramError("displacements", "At most three displacement components are supported.");

  _grad_disp.resize(_ndisp);
  _grad_disp_dot.resize(_ndisp);
  _disp_dot_du.resize(_ndisp);
  for (const auto i : make_range(_ndisp))
  {
    _grad_disp[i] = &adCoupledGradient("displacements", i);
    _grad_disp_dot[i] =
        _fe_problem.isTransient() ? &coupledGradientDot("displacements", i) : nullptr;
    _disp_dot_du[i] =
        _fe_problem.isTransient() ? &coupledDotDu("displacements", i) : nullptr;
  }
}

void
ADSolidReferenceKinematics::computeQpProperties()
{
  _F[_qp].zero();
  for (unsigned int i = 0; i < 3; ++i)
    _F[_qp](i, i) = 1.0;

  for (const auto i : make_range(_ndisp))
    for (const auto j : make_range(Moose::dim))
      _F[_qp](i, j) += (*_grad_disp[i])[_qp](j);

  _J[_qp] = _F[_qp].det();
  _F_inv[_qp] = _F[_qp].inverse();
  _J_F_inv[_qp] = _F_inv[_qp] * _J[_qp];

  ADRankTwoTensor F_dot;
  F_dot.zero();
  if (_fe_problem.isTransient())
    for (const auto i : make_range(_ndisp))
      for (const auto j : make_range(Moose::dim))
      {
        const Real dot_du = (*_disp_dot_du[i])[_qp];
        const ADReal & grad_u = (*_grad_disp[i])[_qp](j);
        F_dot(i, j) = dot_du * grad_u + (*_grad_disp_dot[i])[_qp](j) -
                      dot_du * MetaPhysicL::raw_value(grad_u);
      }
  _J_dot[_qp] = _J[_qp] * (F_dot * _F_inv[_qp]).trace();
}
