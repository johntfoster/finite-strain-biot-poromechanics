//* This file is part of the nonlinear-Biot implicit-AD application.
//* SPDX-License-Identifier: LGPL-2.1-or-later

#include "ADPlasticStateBiotMaterial.h"

#include "metaphysicl/raw_type.h"
#include "MatchedLogMineralState.h"

#include <cmath>

registerMooseObject("MulticomponentReactiveFlowApp", ADPlasticStateBiotMaterial);

InputParameters
ADPlasticStateBiotMaterial::validParams()
{
  InputParameters params = Material::validParams();
  params.addClassDescription(
      "Mass and matched logarithmic mineral residuals at fixed plastic distention.");
  params.addRequiredCoupledVar("pressure", "Continuous pore-pressure field p.");
  params.addRequiredCoupledVar(
      "solid_spatial_mass_ratio",
      "Current bulk solid partial density divided by its reference value (r).");
  params.addParam<MaterialPropertyName>(
      "solid_jacobian_name", "solid_reference_J", "Solid-reference Jacobian J_s.");
  params.addRequiredRangeCheckedParam<Real>(
      "skeleton_bulk_modulus", "skeleton_bulk_modulus>0", "Drained bulk modulus K.");
  params.addParam<MaterialPropertyName>(
      "plastic_pore_allocation_value_name",
      "plastic_pore_allocation_value",
      "Frozen plastic pore allocation a^p (non-AD, history held fixed in the tangent).");
  params.addRequiredRangeCheckedParam<Real>(
      "mineral_bulk_modulus", "mineral_bulk_modulus>0", "Mineral bulk modulus K_s.");
  params.addRequiredRangeCheckedParam<Real>("reference_solid_volume_fraction",
                                            "reference_solid_volume_fraction>0 & "
                                            "reference_solid_volume_fraction<1",
                                            "Reference solid volume fraction phi_s0.");
  params.addParam<MaterialPropertyName>("intrinsic_density_ratio_name",
                                        "plastic_intrinsic_density_ratio",
                                        "Output intrinsic solid-density ratio.");
  params.addParam<MaterialPropertyName>("solid_volume_fraction_name",
                                        "plastic_solid_volume_fraction",
                                        "Output mass-conserving solid volume fraction.");
  params.addParam<MaterialPropertyName>("material_mass_residual_name",
                                        "plastic_local_material_mass_constraint",
                                        "Output local material-mass residual.");
  params.addParam<MaterialPropertyName>("material_mass_intrinsic_density_derivative_name",
                                        "plastic_local_material_mass_d_intrinsic_density_ratio",
                                        "Output dR_mass/d(ratio).");
  params.addParam<MaterialPropertyName>("material_mass_volume_fraction_derivative_name",
                                        "plastic_local_material_mass_d_volume_fraction",
                                        "Output dR_mass/d(phi_s).");
  params.addParam<MaterialPropertyName>("material_mass_jacobian_derivative_name",
                                        "plastic_local_material_mass_d_jacobian",
                                        "Output dR_mass/dJ at fixed referential solid mass.");
  params.addParam<MaterialPropertyName>("mineral_eos_residual_name",
                                        "plastic_mineral_eos_constraint",
                                        "Output mineral-EOS residual.");
  params.addParam<MaterialPropertyName>("mineral_eos_intrinsic_density_derivative_name",
                                        "plastic_mineral_eos_d_intrinsic_density_ratio",
                                        "Output dR_eos/d(ratio).");
  params.addParam<MaterialPropertyName>("mineral_eos_volume_fraction_derivative_name",
                                        "plastic_mineral_eos_d_volume_fraction",
                                        "Output dR_eos/d(phi_s).");
  params.addParam<MaterialPropertyName>("mineral_eos_jacobian_derivative_name",
                                        "plastic_mineral_eos_d_jacobian",
                                        "Output dR_eos/dJ.");
  return params;
}

ADPlasticStateBiotMaterial::ADPlasticStateBiotMaterial(const InputParameters & parameters)
  : Material(parameters),
    _J(getADMaterialProperty<Real>("solid_jacobian_name")),
    _pressure(adCoupledValue("pressure")),
    _solid_spatial_mass_ratio(adCoupledValue("solid_spatial_mass_ratio")),
    _plastic_pore_allocation(getMaterialProperty<Real>("plastic_pore_allocation_value_name")),
    _skeleton_bulk_modulus(getParam<Real>("skeleton_bulk_modulus")),
    _mineral_bulk_modulus(getParam<Real>("mineral_bulk_modulus")),
    _reference_solid_volume_fraction(getParam<Real>("reference_solid_volume_fraction")),
    _intrinsic_density_ratio(
        declareADProperty<Real>(getParam<MaterialPropertyName>("intrinsic_density_ratio_name"))),
    _solid_volume_fraction(
        declareADProperty<Real>(getParam<MaterialPropertyName>("solid_volume_fraction_name"))),
    _material_mass_residual(
        declareADProperty<Real>(getParam<MaterialPropertyName>("material_mass_residual_name"))),
    _material_mass_intrinsic_density_derivative(declareADProperty<Real>(
        getParam<MaterialPropertyName>("material_mass_intrinsic_density_derivative_name"))),
    _material_mass_volume_fraction_derivative(declareADProperty<Real>(
        getParam<MaterialPropertyName>("material_mass_volume_fraction_derivative_name"))),
    _material_mass_jacobian_derivative(declareADProperty<Real>(
        getParam<MaterialPropertyName>("material_mass_jacobian_derivative_name"))),
    _mineral_eos_residual(
        declareADProperty<Real>(getParam<MaterialPropertyName>("mineral_eos_residual_name"))),
    _mineral_eos_intrinsic_density_derivative(declareADProperty<Real>(
        getParam<MaterialPropertyName>("mineral_eos_intrinsic_density_derivative_name"))),
    _mineral_eos_volume_fraction_derivative(declareADProperty<Real>(
        getParam<MaterialPropertyName>("mineral_eos_volume_fraction_derivative_name"))),
    _mineral_eos_jacobian_derivative(declareADProperty<Real>(
        getParam<MaterialPropertyName>("mineral_eos_jacobian_derivative_name")))
{
}

void
ADPlasticStateBiotMaterial::computeQpProperties()
{
  using std::exp;
  using std::log;
  using MetaPhysicL::raw_value;

  if (raw_value(_J[_qp]) <= 0.0)
    mooseError(name(), ": requires J_s>0.");
  if (raw_value(_solid_spatial_mass_ratio[_qp]) <= 0.0)
    mooseError(name(), ": requires a positive normalized solid partial density.");

  const Real a_p = _plastic_pore_allocation[_qp];
  if (a_p <= 0.0)
    mooseError(name(), ": requires a^p>0 (frozen plastic pore allocation).");

  const Real k = _skeleton_bulk_modulus /
                 (_reference_solid_volume_fraction * _mineral_bulk_modulus);
  const Real alpha = 1.0 - k;
  const ADReal Je = _J[_qp] / a_p;
  const ADReal z = matchedLogMineralVolume(Je, _pressure[_qp],
      _skeleton_bulk_modulus, _mineral_bulk_modulus, _reference_solid_volume_fraction);
  const ADReal ratio = 1.0 / z;
  const ADReal phi = _reference_solid_volume_fraction * _solid_spatial_mass_ratio[_qp] * z;
  if (raw_value(phi) <= 0.0 || raw_value(phi) >= 1.0)
    mooseError(name(), ": computed a solid volume fraction outside (0,1).");
  const ADReal reference_solid_mass = _J[_qp] * _solid_spatial_mass_ratio[_qp];
  const ADReal R_mass = _J[_qp] * phi * ratio -
                        _reference_solid_volume_fraction * reference_solid_mass;
  const ADReal R_mass_ratio = _J[_qp] * phi;
  const ADReal R_mass_phi = _J[_qp] * ratio;
  const ADReal R_mass_jacobian = phi * ratio;
  const ADReal R_eos = log(ratio) + k * log(Je) -
                       alpha * _pressure[_qp] * z / _mineral_bulk_modulus;
  const ADReal R_eos_ratio = 1.0 / ratio +
                            alpha * _pressure[_qp] / (_mineral_bulk_modulus * ratio * ratio);
  const ADReal R_eos_phi = 0.0;
  const ADReal R_eos_jacobian = k / _J[_qp];

  _intrinsic_density_ratio[_qp] = ratio;
  _solid_volume_fraction[_qp] = phi;
  _material_mass_residual[_qp] = R_mass;
  _material_mass_intrinsic_density_derivative[_qp] = R_mass_ratio;
  _material_mass_volume_fraction_derivative[_qp] = R_mass_phi;
  _material_mass_jacobian_derivative[_qp] = R_mass_jacobian;
  _mineral_eos_residual[_qp] = R_eos;
  _mineral_eos_intrinsic_density_derivative[_qp] = R_eos_ratio;
  _mineral_eos_volume_fraction_derivative[_qp] = R_eos_phi;
  _mineral_eos_jacobian_derivative[_qp] = R_eos_jacobian;
}
