//* This file is part of the nonlinear-Biot implicit-AD application.
//* SPDX-License-Identifier: LGPL-2.1-or-later

#include "ADPoroplasticBiotCoefficientMaterial.h"

#include "metaphysicl/raw_type.h"

registerMooseObject("MulticomponentReactiveFlowApp", ADPoroplasticBiotCoefficientMaterial);

InputParameters
ADPoroplasticBiotCoefficientMaterial::validParams()
{
  InputParameters params = Material::validParams();
  params.addClassDescription(
      "Plastic pore-allocation correction to the Biot coefficient: "
      "B = 1 - (1 - B_el)/a^p from the fixed-pressure, fixed-history tangent with "
      "v = Jbar/a^p.  Reduces to the elastic coefficient for a^p = 1.");
  params.addParam<MaterialPropertyName>("elastic_biot_coefficient_name",
                                        "elastic_biot_closed_form",
                                        "Elastic Biot coefficient (B_el) to correct.");
  params.addParam<MaterialPropertyName>("plastic_pore_allocation_name",
                                        "plastic_pore_allocation",
                                        "Plastic pore allocation a^p.");
  params.addParam<MaterialPropertyName>(
      "biot_coefficient_name",
      "poroplastic_biot_coefficient",
      "Output pore-allocation-corrected Biot coefficient B.");
  params.addParam<MaterialPropertyName>("biot_delta_name",
                                        "poroplastic_biot_delta",
                                        "Output Delta B = B - B_el.");
  return params;
}

ADPoroplasticBiotCoefficientMaterial::ADPoroplasticBiotCoefficientMaterial(
    const InputParameters & parameters)
  : Material(parameters),
    _elastic_biot(getADMaterialProperty<Real>("elastic_biot_coefficient_name")),
    _a_p(getADMaterialProperty<Real>("plastic_pore_allocation_name")),
    _biot(declareADProperty<Real>(getParam<MaterialPropertyName>("biot_coefficient_name"))),
    _delta(declareADProperty<Real>(getParam<MaterialPropertyName>("biot_delta_name")))
{
}

void
ADPoroplasticBiotCoefficientMaterial::computeQpProperties()
{
  using MetaPhysicL::raw_value;

  const ADReal & B_el = _elastic_biot[_qp];
  const ADReal & a_p = _a_p[_qp];
  if (raw_value(a_p) <= 0.0)
    mooseError(name(), ": requires a^p > 0.");

  const ADReal B = 1.0 - (1.0 - B_el) / a_p;
  _biot[_qp] = B;
  _delta[_qp] = B - B_el;
}
