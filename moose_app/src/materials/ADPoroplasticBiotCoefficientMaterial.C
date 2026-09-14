//* SPDX-License-Identifier: LGPL-2.1-or-later
#include "ADPoroplasticBiotCoefficientMaterial.h"
#include "MatchedLogMineralState.h"

registerMooseObject("MulticomponentReactiveFlowApp", ADPoroplasticBiotCoefficientMaterial);

InputParameters
ADPoroplasticBiotCoefficientMaterial::validParams()
{
  InputParameters params = Material::validParams();
  params.addClassDescription(
      "Solve the matched mineral equation at Je=J/ap and evaluate the fixed-history Biot coefficient.");
  params.addRequiredCoupledVar("pressure", "Pore pressure.");
  params.addParam<MaterialPropertyName>("jacobian_name", "solid_reference_J", "Total Jacobian.");
  params.addParam<MaterialPropertyName>(
      "plastic_pore_allocation_name", "plastic_pore_allocation", "Plastic distention.");
  params.addRequiredRangeCheckedParam<Real>("skeleton_bulk_modulus", "skeleton_bulk_modulus>0", "K.");
  params.addRequiredRangeCheckedParam<Real>("mineral_bulk_modulus", "mineral_bulk_modulus>0", "Ks.");
  params.addRequiredRangeCheckedParam<Real>("reference_solid_volume_fraction",
      "reference_solid_volume_fraction>0 & reference_solid_volume_fraction<1", "Reference solid fraction.");
  params.addParam<MaterialPropertyName>(
      "biot_coefficient_name", "poroplastic_biot_coefficient", "Coefficient at the current plastic state.");
  params.addParam<MaterialPropertyName>(
      "elastic_biot_coefficient_name", "elastic_biot_closed_form", "Virgin elastic coefficient output.");
  params.addParam<MaterialPropertyName>("biot_delta_name", "poroplastic_biot_delta", "B minus virgin B.");
  return params;
}

ADPoroplasticBiotCoefficientMaterial::ADPoroplasticBiotCoefficientMaterial(const InputParameters & p)
  : Material(p),
    _pressure(adCoupledValue("pressure")),
    _J(getADMaterialProperty<Real>("jacobian_name")),
    _a_p(getADMaterialProperty<Real>("plastic_pore_allocation_name")),
    _K(getParam<Real>("skeleton_bulk_modulus")),
    _Ks(getParam<Real>("mineral_bulk_modulus")),
    _phi0(getParam<Real>("reference_solid_volume_fraction")),
    _biot(declareADProperty<Real>(getParam<MaterialPropertyName>("biot_coefficient_name"))),
    _elastic_biot(declareADProperty<Real>(getParam<MaterialPropertyName>("elastic_biot_coefficient_name"))),
    _delta(declareADProperty<Real>(getParam<MaterialPropertyName>("biot_delta_name")))
{
}

void
ADPoroplasticBiotCoefficientMaterial::computeQpProperties()
{
  if (MetaPhysicL::raw_value(_a_p[_qp]) <= 0.0)
    mooseError(name(), ": requires positive plastic distention.");
  const ADReal Je = _J[_qp] / _a_p[_qp];
  const ADReal z = matchedLogMineralVolume(Je, _pressure[_qp], _K, _Ks, _phi0);
  const ADReal virgin_z = matchedLogMineralVolume(_J[_qp], _pressure[_qp], _K, _Ks, _phi0);
  _biot[_qp] = matchedLogBiotCoefficient(_J[_qp], _pressure[_qp], z, _K, _Ks, _phi0);
  _elastic_biot[_qp] =
      matchedLogBiotCoefficient(_J[_qp], _pressure[_qp], virgin_z, _K, _Ks, _phi0);
  _delta[_qp] = _biot[_qp] - _elastic_biot[_qp];
}
