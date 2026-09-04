#include "ADBiotPressureStorageMaterial.h"

#include "metaphysicl/raw_type.h"

registerMooseObject("MulticomponentReactiveFlowApp", ADBiotPressureStorageMaterial);

InputParameters
ADBiotPressureStorageMaterial::validParams()
{
  InputParameters params = Material::validParams();
  params.addClassDescription(
      "Computes rhobar_f(p), the exact solid-reference water accumulation "
      "J_s(1-phi_s)rhobar_f, and its complete AD material time rate.");
  params.addRequiredCoupledVar("pressure", "Continuous pore-pressure field.");
  params.addParam<MaterialPropertyName>(
      "solid_volume_fraction_name", "solid_volume_fraction", "Aggregate solid volume fraction.");
  params.addParam<MaterialPropertyName>("solid_volume_fraction_rate_name",
                                        "solid_volume_fraction_dot",
                                        "Material time rate of the solid volume fraction.");
  params.addParam<MaterialPropertyName>(
      "solid_jacobian_name", "solid_reference_J", "Solid-reference Jacobian J_s.");
  params.addParam<MaterialPropertyName>("solid_jacobian_rate_name",
                                        "solid_reference_J_dot",
                                        "AD time-integrator rate of J_s.");
  params.addRequiredRangeCheckedParam<Real>(
      "reference_density", "reference_density>0", "Water density at the reference pressure.");
  params.addParam<Real>(
      "reference_pressure", 0.0, "Reference pressure associated with the reference density.");
  params.addRequiredRangeCheckedParam<Real>(
      "fluid_bulk_modulus", "fluid_bulk_modulus>0", "Fluid bulk modulus K_f.");
  params.addParam<MaterialPropertyName>(
      "intrinsic_density_name", "water_intrinsic_density", "Intrinsic water density rhobar_f.");
  params.addParam<MaterialPropertyName>("reference_accumulation_name",
                                        "water_reference_accumulation",
                                        "Solid-reference water accumulation J_s(1-phi_s)rhobar_f.");
  params.addParam<MaterialPropertyName>("storage_rate_name",
                                        "water_reference_storage_rate",
                                        "Complete AD time rate of the water accumulation.");
  return params;
}

ADBiotPressureStorageMaterial::ADBiotPressureStorageMaterial(
    const InputParameters & parameters)
  : Material(parameters),
    _pressure(adCoupledValue("pressure")),
    _pressure_dot(_fe_problem.isTransient() ? &adCoupledDot("pressure") : nullptr),
    _solid_J(getADMaterialProperty<Real>("solid_jacobian_name")),
    _solid_J_dot(getADMaterialProperty<Real>("solid_jacobian_rate_name")),
    _solid_volume_fraction(getADMaterialProperty<Real>("solid_volume_fraction_name")),
    _solid_volume_fraction_dot(
        getADMaterialProperty<Real>("solid_volume_fraction_rate_name")),
    _reference_density(getParam<Real>("reference_density")),
    _reference_pressure(getParam<Real>("reference_pressure")),
    _fluid_bulk_modulus(getParam<Real>("fluid_bulk_modulus")),
    _intrinsic_density(
        declareADProperty<Real>(getParam<MaterialPropertyName>("intrinsic_density_name"))),
    _reference_accumulation(declareADProperty<Real>(
        getParam<MaterialPropertyName>("reference_accumulation_name"))),
    _storage_rate(declareADProperty<Real>(getParam<MaterialPropertyName>("storage_rate_name")))
{
}

void
ADBiotPressureStorageMaterial::computeQpProperties()
{
  _intrinsic_density[_qp] =
      _reference_density * exp((_pressure[_qp] - _reference_pressure) / _fluid_bulk_modulus);
  if (MetaPhysicL::raw_value(_intrinsic_density[_qp]) <= 0.0)
    mooseError(name(), ": computed nonpositive intrinsic water density.");

  const ADReal fluid_volume_fraction = 1.0 - _solid_volume_fraction[_qp];
  _reference_accumulation[_qp] =
      _solid_J[_qp] * fluid_volume_fraction * _intrinsic_density[_qp];

  _storage_rate[_qp] =
      _fe_problem.isTransient()
          ? _intrinsic_density[_qp] *
                (fluid_volume_fraction * _solid_J_dot[_qp] -
                 _solid_J[_qp] * _solid_volume_fraction_dot[_qp] +
                 _solid_J[_qp] * fluid_volume_fraction * (*_pressure_dot)[_qp] /
                     _fluid_bulk_modulus)
          : 0.0;
}
