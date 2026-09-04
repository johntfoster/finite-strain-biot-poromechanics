#include "ADBiotDarcyReferenceFluxMaterial.h"

registerMooseObject("MulticomponentReactiveFlowApp", ADBiotDarcyReferenceFluxMaterial);

InputParameters
ADBiotDarcyReferenceFluxMaterial::validParams()
{
  InputParameters params = Material::validParams();
  params.addClassDescription(
      "Computes the solid-reference Darcy mass flux for the single-water Biot "
      "specialization using a continuous pressure field.");
  params.addRequiredCoupledVar("pressure", "Continuous water-pressure field.");
  params.addParam<MaterialPropertyName>(
      "solid_jacobian_name", "solid_reference_J", "Solid-reference Jacobian J_s.");
  params.addParam<MaterialPropertyName>("inverse_deformation_gradient_name",
                                        "solid_reference_F_inv",
                                        "Inverse solid deformation gradient F^{-1}.");
  params.addRequiredParam<MaterialPropertyName>("intrinsic_density_name",
                                                 "Water intrinsic density.");
  params.addRequiredRangeCheckedParam<Real>(
      "permeability", "permeability>=0", "Scalar isotropic intrinsic permeability.");
  params.addRequiredRangeCheckedParam<Real>(
      "viscosity", "viscosity>0", "Constant water dynamic viscosity.");
  params.addParam<MaterialPropertyName>("reference_mobility_name",
                                        "biot_water_reference_mobility",
                                        "Pulled-back Darcy mobility tensor.");
  params.addParam<MaterialPropertyName>("reference_mass_flux_name",
                                        "biot_water_reference_mass_flux",
                                        "Solid-reference water mass flux.");
  return params;
}

ADBiotDarcyReferenceFluxMaterial::ADBiotDarcyReferenceFluxMaterial(
    const InputParameters & parameters)
  : Material(parameters),
    _solid_J(getADMaterialProperty<Real>("solid_jacobian_name")),
    _inverse_deformation_gradient(
        getADMaterialProperty<RankTwoTensor>("inverse_deformation_gradient_name")),
    _pressure_gradient(adCoupledGradient("pressure")),
    _intrinsic_density(getADMaterialProperty<Real>("intrinsic_density_name")),
    _permeability(getParam<Real>("permeability")),
    _viscosity(getParam<Real>("viscosity")),
    _reference_mobility(declareADProperty<RankTwoTensor>(
        getParam<MaterialPropertyName>("reference_mobility_name"))),
    _reference_mass_flux(declareADProperty<RealVectorValue>(
        getParam<MaterialPropertyName>("reference_mass_flux_name")))
{
}

void
ADBiotDarcyReferenceFluxMaterial::computeQpProperties()
{
  const ADReal mobility = _intrinsic_density[_qp] * _permeability / _viscosity;
  _reference_mobility[_qp] = mobility * _solid_J[_qp] *
                             _inverse_deformation_gradient[_qp] *
                             _inverse_deformation_gradient[_qp].transpose();
  _reference_mass_flux[_qp] = -_reference_mobility[_qp] * _pressure_gradient[_qp];
}
