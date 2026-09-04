#include "ADReferenceSolidMomentum.h"

#include "Function.h"

registerMooseObject("MulticomponentReactiveFlowApp", ADReferenceSolidMomentum);

InputParameters
ADReferenceSolidMomentum::validParams()
{
  InputParameters params = ADKernel::validParams();
  params += FunctionInterface::validParams();
  params.addClassDescription(
      "Quasi-static solid-skeleton momentum residual on the solid reference configuration, "
      "Grad(test) : P - test b_0.");
  params.addRequiredRangeCheckedParam<unsigned int>("component", "component<3", "Momentum component.");
  params.addParam<MaterialPropertyName>(
      "first_piola_stress_name",
      "reference_solid_total_first_piola",
      "Material property for P'' - B p_E J F^{-T} plus optional pulled-back current stresses.");
  params.addParam<MaterialPropertyName>("solid_jacobian_name",
                                        "solid_reference_J",
                                        "Material property name for J.");
  params.addCoupledVar(
      "current_volume_force",
      "Optional current-volume force components, such as rho g, thermocapillary, or conversion "
      "insertion forces; the kernel multiplies them by J.");
  params.addParam<FunctionName>(
      "reference_body_force",
      "0",
      "Reference-volume force component b_0 appearing in Div_X P + b_0 = 0.");
  return params;
}

ADReferenceSolidMomentum::ADReferenceSolidMomentum(const InputParameters & parameters)
  : ADKernel(parameters),
    _component(getParam<unsigned int>("component")),
    _dim(_mesh.dimension()),
    _first_piola_stress(getADMaterialProperty<RankTwoTensor>("first_piola_stress_name")),
    _solid_J(getADMaterialProperty<Real>("solid_jacobian_name")),
    _reference_body_force(getFunction("reference_body_force"))
{
  if (_component >= _dim)
    paramError("component", "Momentum component must be smaller than the mesh dimension.");
  if (isCoupled("current_volume_force") && coupledComponents("current_volume_force") != _dim)
    paramError("current_volume_force", "Provide exactly dim current-volume force components.");

  _current_volume_force.reserve(_dim);
  if (isCoupled("current_volume_force"))
    for (const auto i : make_range(_dim))
      _current_volume_force.push_back(&adCoupledValue("current_volume_force", i));
}

ADReal
ADReferenceSolidMomentum::computeQpResidual()
{
  ADReal residual = 0.0;
  for (const auto j : make_range(_dim))
    residual += _grad_test[_i][_qp](j) * _first_piola_stress[_qp](_component, j);

  ADReal reference_force = _reference_body_force.value(_t, _q_point[_qp]);
  if (!_current_volume_force.empty())
    reference_force += _solid_J[_qp] * (*_current_volume_force[_component])[_qp];

  return residual - _test[_i][_qp] * reference_force;
}
