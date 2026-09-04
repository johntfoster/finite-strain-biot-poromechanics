#include "ADReferenceSolidStressMaterial.h"

#include "metaphysicl/raw_type.h"

registerMooseObject("MulticomponentReactiveFlowApp", ADReferenceSolidStressMaterial);

InputParameters
ADReferenceSolidStressMaterial::validParams()
{
  InputParameters params = Material::validParams();
  params.addClassDescription(
      "Recovers P'=P''+(1-B)p_E J F^{-T} by the inverse Biot transform, then assembles "
      "P=P'-p_E J F^{-T}, with an optional pulled-back Maxwell Cauchy stress, for the "
      "solid-reference skeleton momentum balance.");
  params.addParam<MaterialPropertyName>(
      "effective_first_piola_name",
      "solid_effective_first_piola",
      "Material property name for the effective first Piola stress P''.");
  params.addParam<MaterialPropertyName>(
      "reference_prestress_name",
      "",
      "Optional initial/reference first-Piola prestress added to P''. This permits a "
      "loaded reference configuration (for example an in-situ reservoir state) without "
      "embedding benchmark-specific initialization in the constitutive model.");
  params.addCoupledVar("equivalent_pressure", 0.0, "Equivalent pore pressure backbone or field.");
  params.addCoupledVar("equivalent_pressure_enrichment",
                       "Optional P0 enrichment. When supplied, the stress uses p_E + p_E,enr.");
  params.addParam<MaterialPropertyName>(
      "equivalent_pressure_total_name",
      "",
      "Optional reconstructed equivalent-pressure material property. When supplied, this "
      "property is used instead of the directly coupled pressure fields.");
  params.addParam<Real>("biot_coefficient",
                        0.0,
                        "Backward-compatible constant aggregate Biot coefficient B used when "
                        "biot_coefficient_name is not supplied.");
  params.addParam<MaterialPropertyName>(
      "biot_coefficient_name",
      "",
      "Optional AD material property for the nonlinear Biot coefficient B. When supplied, "
      "the stress preserves the AD chain rule through B in P = P'' - B p_E J F^{-T}.");
  params.addParam<bool>(
      "strip_biot_derivatives",
      false,
      "Verification-only ablation that reevaluates B with the current state but removes its AD "
      "derivatives from the stress Jacobian.");
  params.addParam<MaterialPropertyName>(
      "prime_first_piola_name",
      "solid_prime_first_piola",
      "Output first-prime stress P'=P''+(1-B)p_E J F^{-T} recovered from P'' by the "
      "inverse Biot transform.");
  params.addParam<MaterialPropertyName>(
      "solid_jacobian_name", "solid_reference_J", "Material property name for J.");
  params.addParam<MaterialPropertyName>("solid_inverse_deformation_gradient_name",
                                        "solid_reference_F_inv",
                                        "Material property name for F^{-1}.");
  params.addParam<MaterialPropertyName>(
      "maxwell_cauchy_stress_name",
      "",
      "Optional current Maxwell stress E tensor d to be pulled back as J sigma F^{-T}.");
  params.addParam<MaterialPropertyName>(
      "total_first_piola_name",
      "reference_solid_total_first_piola",
      "Material property name for the total first Piola stress entering the residual.");
  return params;
}

ADReferenceSolidStressMaterial::ADReferenceSolidStressMaterial(const InputParameters & parameters)
  : Material(parameters),
    _effective_first_piola(getADMaterialProperty<RankTwoTensor>("effective_first_piola_name")),
    _reference_prestress(getParam<MaterialPropertyName>("reference_prestress_name").empty()
                             ? nullptr
                             : &getADMaterialProperty<RankTwoTensor>("reference_prestress_name")),
    _solid_J(getADMaterialProperty<Real>("solid_jacobian_name")),
    _solid_F_inv(getADMaterialProperty<RankTwoTensor>("solid_inverse_deformation_gradient_name")),
    _maxwell_cauchy_stress(
        getParam<MaterialPropertyName>("maxwell_cauchy_stress_name").empty()
            ? nullptr
            : &getADMaterialProperty<RankTwoTensor>("maxwell_cauchy_stress_name")),
    _equivalent_pressure(adCoupledValue("equivalent_pressure")),
    _equivalent_pressure_enrichment(isCoupled("equivalent_pressure_enrichment")
                                        ? &adCoupledValue("equivalent_pressure_enrichment")
                                        : nullptr),
    _equivalent_pressure_total(
        getParam<MaterialPropertyName>("equivalent_pressure_total_name").empty()
            ? nullptr
            : &getADMaterialProperty<Real>("equivalent_pressure_total_name")),
    _constant_biot_coefficient(getParam<Real>("biot_coefficient")),
    _biot_coefficient(getParam<MaterialPropertyName>("biot_coefficient_name").empty()
                          ? nullptr
                          : &getADMaterialProperty<Real>("biot_coefficient_name")),
    _strip_biot_derivatives(getParam<bool>("strip_biot_derivatives")),
    _prime_first_piola(
        declareADProperty<RankTwoTensor>(getParam<MaterialPropertyName>("prime_first_piola_name"))),
    _total_first_piola(
        declareADProperty<RankTwoTensor>(getParam<MaterialPropertyName>("total_first_piola_name")))
{
}

void
ADReferenceSolidStressMaterial::computeQpProperties()
{
  const ADRankTwoTensor J_F_inv_T = _solid_J[_qp] * _solid_F_inv[_qp].transpose();
  const ADReal pressure =
      _equivalent_pressure_total
          ? (*_equivalent_pressure_total)[_qp]
          : _equivalent_pressure[_qp] +
                (_equivalent_pressure_enrichment ? (*_equivalent_pressure_enrichment)[_qp] : 0.0);
  ADReal biot_coefficient =
      _biot_coefficient ? (*_biot_coefficient)[_qp] : _constant_biot_coefficient;
  if (_strip_biot_derivatives)
    biot_coefficient = MetaPhysicL::raw_value(biot_coefficient);
  _prime_first_piola[_qp] =
      _effective_first_piola[_qp] +
      (_reference_prestress ? (*_reference_prestress)[_qp] : ADRankTwoTensor()) +
      (1.0 - biot_coefficient) * pressure * J_F_inv_T;
  _total_first_piola[_qp] = _prime_first_piola[_qp] - pressure * J_F_inv_T;

  if (_maxwell_cauchy_stress)
    _total_first_piola[_qp] +=
        _solid_J[_qp] * (*_maxwell_cauchy_stress)[_qp] * _solid_F_inv[_qp].transpose();
}
