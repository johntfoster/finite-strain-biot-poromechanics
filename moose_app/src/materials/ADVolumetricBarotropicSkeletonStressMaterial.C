#include "ADVolumetricBarotropicSkeletonStressMaterial.h"

#include "metaphysicl/raw_type.h"
#include "MatchedLogMineralState.h"

registerMooseObject("MulticomponentReactiveFlowApp", ADVolumetricBarotropicSkeletonStressMaterial);

InputParameters
ADVolumetricBarotropicSkeletonStressMaterial::validParams()
{
  InputParameters params = Material::validParams();
  params.addClassDescription(
      "Computes the pressure-coupled double-prime first Piola stress for a decoupled "
      "isochoric-volumetric skeleton potential and matched logarithmic mineral law.");
  params.addParam<MaterialPropertyName>(
      "deformation_gradient_name", "solid_reference_F", "Material property name for F_s.");
  params.addParam<MaterialPropertyName>(
      "jacobian_name", "solid_reference_J", "Material property name for J_s.");
  params.addParam<MaterialPropertyName>("inverse_deformation_gradient_name",
                                        "solid_reference_F_inv",
                                        "Material property name for F_s^{-1}.");
  params.addRequiredCoupledVar("equivalent_pressure", "Gauge equivalent pore pressure.");
  params.addCoupledVar("equivalent_pressure_enrichment", "Optional P0 pressure enrichment.");
  params.addRequiredRangeCheckedParam<Real>(
      "shear_modulus", "shear_modulus>0", "Skeleton isochoric shear modulus.");
  params.addRequiredRangeCheckedParam<Real>(
      "skeleton_bulk_modulus", "skeleton_bulk_modulus>0", "Reference skeleton bulk modulus.");
  params.addRequiredRangeCheckedParam<Real>(
      "mineral_bulk_modulus", "mineral_bulk_modulus>0", "Mineral solid bulk modulus K_s.");
  params.addRequiredRangeCheckedParam<Real>("reference_solid_volume_fraction",
                                            "reference_solid_volume_fraction>0 & "
                                            "reference_solid_volume_fraction<=1",
                                            "Reference solid volume fraction phi_s0.");
  params.addParam<MaterialPropertyName>("effective_first_piola_name",
                                        "solid_effective_first_piola",
                                        "Output pressure-coupled double-prime first Piola stress.");
  params.addParam<MaterialPropertyName>("mineral_effective_pressure_name",
                                        "solid_mineral_effective_pressure",
                                        "Output compression-positive mechanical mineral pressure.");
  params.addParam<MaterialPropertyName>("mineral_effective_pressure_jacobian_derivative_name",
                                        "solid_mineral_effective_pressure_jacobian_derivative",
                                        "Output fixed-pressure mineral-pressure derivative with respect to J_s.");
  return params;
}

ADVolumetricBarotropicSkeletonStressMaterial::ADVolumetricBarotropicSkeletonStressMaterial(
    const InputParameters & parameters)
  : Material(parameters),
    _F(getADMaterialProperty<RankTwoTensor>("deformation_gradient_name")),
    _J(getADMaterialProperty<Real>("jacobian_name")),
    _F_inv(getADMaterialProperty<RankTwoTensor>("inverse_deformation_gradient_name")),
    _equivalent_pressure(adCoupledValue("equivalent_pressure")),
    _equivalent_pressure_enrichment(isCoupled("equivalent_pressure_enrichment")
                                        ? &adCoupledValue("equivalent_pressure_enrichment")
                                        : nullptr),
    _shear_modulus(getParam<Real>("shear_modulus")),
    _skeleton_bulk_modulus(getParam<Real>("skeleton_bulk_modulus")),
    _mineral_bulk_modulus(getParam<Real>("mineral_bulk_modulus")),
    _reference_solid_volume_fraction(getParam<Real>("reference_solid_volume_fraction")),
    _effective_first_piola(declareADProperty<RankTwoTensor>(
        getParam<MaterialPropertyName>("effective_first_piola_name"))),
    _mineral_effective_pressure(
        declareADProperty<Real>(getParam<MaterialPropertyName>("mineral_effective_pressure_name"))),
    _mineral_effective_pressure_jacobian_derivative(declareADProperty<Real>(
        getParam<MaterialPropertyName>("mineral_effective_pressure_jacobian_derivative_name")))
{
}

void
ADVolumetricBarotropicSkeletonStressMaterial::computeQpProperties()
{
  const ADReal & J = _J[_qp];
  if (MetaPhysicL::raw_value(J) <= 0.0)
    mooseError(name(), ": requires J_s>0.");

  const ADReal log_J = log(J);
  const ADRankTwoTensor F_inv_T = _F_inv[_qp].transpose();
  const ADReal I_1 = _F[_qp].doubleContraction(_F[_qp]);
  const ADReal J_minus_two_thirds = pow(J, -2.0 / 3.0);
  const ADRankTwoTensor skeleton_first_piola =
      _shear_modulus * J_minus_two_thirds * (_F[_qp] - (I_1 / 3.0) * F_inv_T) +
      _skeleton_bulk_modulus * log_J * F_inv_T;

  const ADReal pressure =
      _equivalent_pressure[_qp] +
      (_equivalent_pressure_enrichment ? (*_equivalent_pressure_enrichment)[_qp] : 0.0);
  const Real alpha = 1.0 - _skeleton_bulk_modulus /
                              (_reference_solid_volume_fraction * _mineral_bulk_modulus);
  const ADReal z = matchedLogMineralVolume(J, pressure, _skeleton_bulk_modulus,
                                           _mineral_bulk_modulus,
                                           _reference_solid_volume_fraction);
  const ADReal D = _mineral_bulk_modulus + alpha * pressure * z;
  const ADReal z_J = _skeleton_bulk_modulus * z /
                    (_reference_solid_volume_fraction * J * D);
  // Mechanical mineral pressure, obtained from the intrinsic stress trace.
  _mineral_effective_pressure[_qp] = -_mineral_bulk_modulus * log(z) / z;
  _mineral_effective_pressure_jacobian_derivative[_qp] =
      -_mineral_bulk_modulus * (1.0 - log(z)) * z_J / (z * z);
  _effective_first_piola[_qp] = skeleton_first_piola +
      (_skeleton_bulk_modulus * alpha * pressure * pressure * z * z /
       (_mineral_bulk_modulus * D)) * F_inv_T;
}
