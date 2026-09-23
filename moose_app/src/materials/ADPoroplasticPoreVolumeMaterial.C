//* SPDX-License-Identifier: LGPL-2.1-or-later
#include "ADPoroplasticPoreVolumeMaterial.h"
#include "metaphysicl/raw_type.h"

registerMooseObject("MulticomponentReactiveFlowApp", ADPoroplasticPoreVolumeMaterial);
InputParameters
ADPoroplasticPoreVolumeMaterial::validParams()
{
  auto params = Material::validParams();
  params.addClassDescription("Pore volume and its chain-rule rate during implicit poroplastic flow.");
  params.addRequiredCoupledVar("pressure", "Water pressure.");
  params.addRequiredParam<Real>("skeleton_bulk_modulus", "K.");
  params.addRequiredParam<Real>("mineral_bulk_modulus", "Ks.");
  params.addRequiredParam<Real>("reference_solid_volume_fraction", "Initial solid fraction.");
  params.addRequiredParam<Real>("dp_dilation_slope", "Dilation slope used by the return mapping.");
  return params;
}
ADPoroplasticPoreVolumeMaterial::ADPoroplasticPoreVolumeMaterial(const InputParameters & p)
  : Material(p),
    _p(adCoupledValue("pressure")), _p_dot(adCoupledDot("pressure")),
    _rho(getADMaterialProperty<Real>("solid_spatial_mass_ratio")),
    _rho_dot(getADMaterialProperty<Real>("solid_spatial_mass_ratio_dot")),
    _J(getADMaterialProperty<Real>("solid_reference_J")),
    _J_dot(getADMaterialProperty<Real>("solid_reference_J_dot")),
    _ratio(getADMaterialProperty<Real>("implicit_plastic_density_ratio")),
    _ap(getADMaterialProperty<Real>("plastic_pore_allocation")),
    _gamma(getADMaterialProperty<Real>("plastic_multiplier_increment")),
    _K(getParam<Real>("skeleton_bulk_modulus")),
    _Ks(getParam<Real>("mineral_bulk_modulus")),
    _phi0(getParam<Real>("reference_solid_volume_fraction")),
    _beta(getParam<Real>("dp_dilation_slope")),
    _phi(declareADProperty<Real>("solid_volume_fraction")),
    _phi_dot(declareADProperty<Real>("solid_volume_fraction_dot")),
    _eos(declareADProperty<Real>("solid_mineral_eos_constraint")),
    _plastic_storage(declareADProperty<Real>("plastic_pore_volume_rate"))
{
}
void
ADPoroplasticPoreVolumeMaterial::computeQpProperties()
{
  const Real alpha = 1. - _K / (_phi0 * _Ks);
  const ADReal z = 1. / _ratio[_qp];
  const ADReal D = _Ks + alpha * _p[_qp] * z;
  // det(exp(W)) gives log(ap/ap_old) = beta Delta_gamma exactly.
  const ADReal plastic_log_rate = _dt > 0. ? _beta * _gamma[_qp] / _dt : ADReal(0.);
  const ADReal z_dot = z / D *
      (_K / _phi0 * (_J_dot[_qp] / _J[_qp] - plastic_log_rate) -
       alpha * z * _p_dot[_qp]);
  _phi[_qp] = _phi0 * _rho[_qp] * z;
  _phi_dot[_qp] = _phi0 * (_rho_dot[_qp] * z + _rho[_qp] * z_dot);
  _eos[_qp] = log(z) + alpha * _p[_qp] * z / _Ks -
      _K / (_phi0 * _Ks) * log(_J[_qp] / _ap[_qp]);
  _plastic_storage[_qp] = _J[_qp] * _rho[_qp] * z * _K / D * plastic_log_rate;
  if (MetaPhysicL::raw_value(_phi[_qp]) <= 0. || MetaPhysicL::raw_value(_phi[_qp]) >= 1.)
    mooseError(name(), ": solid fraction outside (0,1).");
}
