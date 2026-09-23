#include "ADBinarySolidSpatialMassMaterial.h"

#include "metaphysicl/raw_type.h"

registerMooseObject("MulticomponentReactiveFlowApp", ADBinarySolidSpatialMassMaterial);

InputParameters
ADBinarySolidSpatialMassMaterial::validParams()
{
  InputParameters params = Material::validParams();
  params.addClassDescription(
      "Enforces constant referential solid mass by eliminating the partial density. "
      "The output is the current solid partial density divided "
      "by its reference value.");
  params.addParam<MaterialPropertyName>(
      "solid_jacobian_name", "solid_reference_J", "Solid-reference Jacobian J_s.");
  params.addParam<MaterialPropertyName>("solid_jacobian_rate_name",
                                        "solid_reference_J_dot",
                                        "Material time rate of J_s.");

  params.addParam<MaterialPropertyName>("reference_component_accumulation_name",
                                        "solid_component_reference_accumulation",
                                        "Output name for the normalized referential solid mass.");
  params.addParam<MaterialPropertyName>("reference_component_storage_rate_name",
                                        "solid_component_reference_storage_rate",
                                        "Output name for its material time rate.");
  return params;
}

ADBinarySolidSpatialMassMaterial::ADBinarySolidSpatialMassMaterial(
    const InputParameters & parameters)
  : Material(parameters),
    _J(getADMaterialProperty<Real>("solid_jacobian_name")),
    _J_dot(getADMaterialProperty<Real>("solid_jacobian_rate_name")),
    _solid_spatial_mass_ratio(declareADProperty<Real>("solid_spatial_mass_ratio")),
    _solid_spatial_mass_ratio_dot(declareADProperty<Real>("solid_spatial_mass_ratio_dot")),
    _reference_component_accumulation(declareADProperty<Real>(
        getParam<MaterialPropertyName>("reference_component_accumulation_name"))),
    _reference_component_storage_rate(declareADProperty<Real>(
        getParam<MaterialPropertyName>("reference_component_storage_rate_name")))
{
}

void
ADBinarySolidSpatialMassMaterial::computeQpProperties()
{
  if (MetaPhysicL::raw_value(_J[_qp]) <= 0.0)
    mooseError(name(), ": requires a positive total Jacobian.");
  _solid_spatial_mass_ratio[_qp] = 1.0 / _J[_qp];
  _solid_spatial_mass_ratio_dot[_qp] = -_J_dot[_qp] / (_J[_qp] * _J[_qp]);
  _reference_component_accumulation[_qp] = _J[_qp] * _solid_spatial_mass_ratio[_qp];
  _reference_component_storage_rate[_qp] = 0.0;
}
