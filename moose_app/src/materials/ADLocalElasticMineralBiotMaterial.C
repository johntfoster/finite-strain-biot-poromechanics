#include "ADLocalElasticMineralBiotMaterial.h"

#include "metaphysicl/raw_type.h"

#include <cmath>

registerMooseObject("MulticomponentReactiveFlowApp", ADLocalElasticMineralBiotMaterial);

InputParameters
ADLocalElasticMineralBiotMaterial::validParams()
{
  InputParameters params = Material::validParams();
  params.addClassDescription(
      "Supplies the elastic verification state, local material-mass and mineral-EOS "
      "residual derivatives, material rates, and a closed-form fixed-pressure Biot oracle. "
      "The production Biot coefficient is computed by ADConstrainedSkeletonBiotMaterial.");
  params.addRequiredCoupledVar("pressure", "Continuous pore-pressure field.");
  params.addRequiredCoupledVar(
      "solid_spatial_mass_ratio",
      "Current bulk solid partial density divided by its reference value.");
  params.addParam<MaterialPropertyName>(
      "solid_jacobian_name", "solid_reference_J", "Solid-reference Jacobian J_s.");
  params.addParam<MaterialPropertyName>(
      "solid_jacobian_rate_name", "solid_reference_J_dot", "Material time rate of J_s.");
  params.addParam<MaterialPropertyName>("mineral_effective_pressure_name",
                                        "solid_mineral_effective_pressure",
                                        "Compression-positive mineral pressure q_s(J_s).");
  params.addParam<MaterialPropertyName>(
      "mineral_effective_pressure_jacobian_derivative_name",
      "solid_mineral_effective_pressure_jacobian_derivative",
      "Fixed-state derivative dq_s/dJ_s.");
  params.addRequiredRangeCheckedParam<Real>(
      "mineral_bulk_modulus", "mineral_bulk_modulus>0", "Mineral bulk modulus K_s.");
  params.addRequiredRangeCheckedParam<Real>("reference_solid_volume_fraction",
                                            "reference_solid_volume_fraction>0 & "
                                            "reference_solid_volume_fraction<1",
                                            "Reference solid volume fraction phi_s0.");
  params.addParam<MaterialPropertyName>("intrinsic_density_ratio_name",
                                        "solid_intrinsic_density_ratio",
                                        "Output intrinsic solid-density ratio.");
  params.addParam<MaterialPropertyName>("intrinsic_density_ratio_rate_name",
                                        "solid_intrinsic_density_ratio_dot",
                                        "Output material rate of the density ratio.");
  params.addParam<MaterialPropertyName>(
      "solid_volume_fraction_name", "solid_volume_fraction", "Output solid volume fraction.");
  params.addParam<MaterialPropertyName>("solid_volume_fraction_rate_name",
                                        "solid_volume_fraction_dot",
                                        "Output material rate of the solid volume fraction.");
  params.addParam<MaterialPropertyName>(
      "biot_coefficient_name", "solid_biot_coefficient", "Output nonlinear Biot coefficient.");
  params.addParam<MaterialPropertyName>(
      "intrinsic_specific_volume_jacobian_tangent_name",
      "solid_intrinsic_specific_volume_jacobian_tangent",
      "Output fixed-pressure mineral-distension tangent.");
  params.addParam<MaterialPropertyName>("mineral_eos_residual_name",
                                        "solid_mineral_eos_constraint",
                                        "Output mineral-EOS residual diagnostic.");
  params.addParam<MaterialPropertyName>("material_mass_residual_name",
                                        "solid_local_material_mass_constraint",
                                        "Output local material-mass residual.");
  params.addParam<MaterialPropertyName>(
      "material_mass_intrinsic_density_derivative_name",
      "solid_local_material_mass_d_intrinsic_density_ratio",
      "Output partial derivative of the material-mass residual with respect to the "
      "intrinsic-density ratio.");
  params.addParam<MaterialPropertyName>(
      "material_mass_volume_fraction_derivative_name",
      "solid_local_material_mass_d_volume_fraction",
      "Output partial derivative of the material-mass residual with respect to phi_s.");
  params.addParam<MaterialPropertyName>(
      "material_mass_jacobian_derivative_name",
      "solid_local_material_mass_d_jacobian",
      "Output partial derivative of the material-mass residual with respect to J_s at fixed "
      "referential solid mass and local state.");
  params.addParam<MaterialPropertyName>(
      "mineral_eos_intrinsic_density_derivative_name",
      "solid_mineral_eos_d_intrinsic_density_ratio",
      "Output partial derivative of the mineral-EOS residual with respect to the "
      "intrinsic-density ratio.");
  params.addParam<MaterialPropertyName>(
      "mineral_eos_volume_fraction_derivative_name",
      "solid_mineral_eos_d_volume_fraction",
      "Output partial derivative of the mineral-EOS residual with respect to phi_s.");
  params.addParam<MaterialPropertyName>(
      "mineral_eos_jacobian_derivative_name",
      "solid_mineral_eos_d_jacobian",
      "Output partial derivative of the mineral-EOS residual with respect to J_s.");
  return params;
}

ADLocalElasticMineralBiotMaterial::ADLocalElasticMineralBiotMaterial(
    const InputParameters & parameters)
  : Material(parameters),
    _pressure(adCoupledValue("pressure")),
    _pressure_dot(_fe_problem.isTransient() ? &adCoupledDot("pressure") : nullptr),
    _solid_spatial_mass_ratio(adCoupledValue("solid_spatial_mass_ratio")),
    _solid_spatial_mass_ratio_dot(
        _fe_problem.isTransient() ? &adCoupledDot("solid_spatial_mass_ratio") : nullptr),
    _J(getADMaterialProperty<Real>("solid_jacobian_name")),
    _J_dot(getADMaterialProperty<Real>("solid_jacobian_rate_name")),
    _mineral_effective_pressure(
        getADMaterialProperty<Real>("mineral_effective_pressure_name")),
    _mineral_effective_pressure_jacobian_derivative(
        getADMaterialProperty<Real>("mineral_effective_pressure_jacobian_derivative_name")),
    _mineral_bulk_modulus(getParam<Real>("mineral_bulk_modulus")),
    _reference_solid_volume_fraction(getParam<Real>("reference_solid_volume_fraction")),
    _intrinsic_density_ratio(
        declareADProperty<Real>(getParam<MaterialPropertyName>("intrinsic_density_ratio_name"))),
    _intrinsic_density_ratio_dot(declareADProperty<Real>(
        getParam<MaterialPropertyName>("intrinsic_density_ratio_rate_name"))),
    _solid_volume_fraction(
        declareADProperty<Real>(getParam<MaterialPropertyName>("solid_volume_fraction_name"))),
    _solid_volume_fraction_dot(declareADProperty<Real>(
        getParam<MaterialPropertyName>("solid_volume_fraction_rate_name"))),
    _biot_coefficient(
        declareADProperty<Real>(getParam<MaterialPropertyName>("biot_coefficient_name"))),
    _intrinsic_specific_volume_jacobian_tangent(declareADProperty<Real>(
        getParam<MaterialPropertyName>("intrinsic_specific_volume_jacobian_tangent_name"))),
    _mineral_eos_residual(
        declareADProperty<Real>(getParam<MaterialPropertyName>("mineral_eos_residual_name"))),
    _material_mass_residual(
        declareADProperty<Real>(getParam<MaterialPropertyName>("material_mass_residual_name"))),
    _material_mass_intrinsic_density_derivative(declareADProperty<Real>(
        getParam<MaterialPropertyName>("material_mass_intrinsic_density_derivative_name"))),
    _material_mass_volume_fraction_derivative(declareADProperty<Real>(
        getParam<MaterialPropertyName>("material_mass_volume_fraction_derivative_name"))),
    _material_mass_jacobian_derivative(declareADProperty<Real>(
        getParam<MaterialPropertyName>("material_mass_jacobian_derivative_name"))),
    _mineral_eos_intrinsic_density_derivative(declareADProperty<Real>(
        getParam<MaterialPropertyName>("mineral_eos_intrinsic_density_derivative_name"))),
    _mineral_eos_volume_fraction_derivative(declareADProperty<Real>(
        getParam<MaterialPropertyName>("mineral_eos_volume_fraction_derivative_name"))),
    _mineral_eos_jacobian_derivative(declareADProperty<Real>(
        getParam<MaterialPropertyName>("mineral_eos_jacobian_derivative_name")))
{
}

void
ADLocalElasticMineralBiotMaterial::computeQpProperties()
{
  if (MetaPhysicL::raw_value(_J[_qp]) <= 0.0)
    mooseError(name(), ": requires J_s>0.");
  if (MetaPhysicL::raw_value(_solid_spatial_mass_ratio[_qp]) <= 0.0)
    mooseError(name(), ": requires a positive normalized solid partial density.");

  // The thermodynamic phase pressure is p.  The sum p+q appears because q(J)
  // is the deformation-density coupling in d psi_min/d vbar; q is not a
  // second phase pressure.
  const ADReal mineral_compression_argument =
      _pressure[_qp] + _mineral_effective_pressure[_qp];
  _intrinsic_density_ratio[_qp] =
      exp(mineral_compression_argument / _mineral_bulk_modulus);
  _solid_volume_fraction[_qp] = _reference_solid_volume_fraction *
                               _solid_spatial_mass_ratio[_qp] / _intrinsic_density_ratio[_qp];

  if (MetaPhysicL::raw_value(_solid_volume_fraction[_qp]) <= 0.0 ||
      MetaPhysicL::raw_value(_solid_volume_fraction[_qp]) >= 1.0)
    mooseError(name(), ": computed a solid volume fraction outside (0,1).");

  if (_fe_problem.isTransient())
  {
    _intrinsic_density_ratio_dot[_qp] =
        _intrinsic_density_ratio[_qp] *
        ((*_pressure_dot)[_qp] +
         _mineral_effective_pressure_jacobian_derivative[_qp] * _J_dot[_qp]) /
        _mineral_bulk_modulus;
    _solid_volume_fraction_dot[_qp] =
        _reference_solid_volume_fraction *
        ((*_solid_spatial_mass_ratio_dot)[_qp] / _intrinsic_density_ratio[_qp] -
         _solid_spatial_mass_ratio[_qp] * _intrinsic_density_ratio_dot[_qp] /
             (_intrinsic_density_ratio[_qp] * _intrinsic_density_ratio[_qp]));
  }
  else
  {
    _intrinsic_density_ratio_dot[_qp] = 0.0;
    _solid_volume_fraction_dot[_qp] = 0.0;
  }

  // Publish the converged elastic residuals and their partial derivatives for
  // the reusable constrained-state tangent. The current referential solid mass
  // is held fixed when the residual derivative with respect to J is formed.
  const ADReal reference_solid_mass = _J[_qp] * _solid_spatial_mass_ratio[_qp];
  _material_mass_residual[_qp] =
      _J[_qp] * _solid_volume_fraction[_qp] * _intrinsic_density_ratio[_qp] -
      _reference_solid_volume_fraction * reference_solid_mass;
  _material_mass_intrinsic_density_derivative[_qp] =
      _J[_qp] * _solid_volume_fraction[_qp];
  _material_mass_volume_fraction_derivative[_qp] =
      _J[_qp] * _intrinsic_density_ratio[_qp];
  _material_mass_jacobian_derivative[_qp] =
      _solid_volume_fraction[_qp] * _intrinsic_density_ratio[_qp];
  _mineral_eos_intrinsic_density_derivative[_qp] =
      1.0 / _intrinsic_density_ratio[_qp];
  _mineral_eos_volume_fraction_derivative[_qp] = 0.0;
  _mineral_eos_jacobian_derivative[_qp] =
      -_mineral_effective_pressure_jacobian_derivative[_qp] / _mineral_bulk_modulus;

  // The explicit elastic derivative is an independent oracle.  The production
  // coefficient used by the residual is supplied by the general constrained
  // material under a different property name in the verification inputs.
  _intrinsic_specific_volume_jacobian_tangent[_qp] =
      -_mineral_effective_pressure_jacobian_derivative[_qp] /
      (_mineral_bulk_modulus * _intrinsic_density_ratio[_qp]);
  _biot_coefficient[_qp] =
      1.0 - _reference_solid_volume_fraction *
                _intrinsic_specific_volume_jacobian_tangent[_qp];
  _mineral_eos_residual[_qp] =
      log(_intrinsic_density_ratio[_qp]) -
      mineral_compression_argument / _mineral_bulk_modulus;

}
