#include "ADLocalElasticMineralBiotMaterial.h"

#include "metaphysicl/raw_type.h"
#include "MatchedLogMineralState.h"

#include <cmath>

registerMooseObject("MulticomponentReactiveFlowApp", ADLocalElasticMineralBiotMaterial);

InputParameters
ADLocalElasticMineralBiotMaterial::validParams()
{
  InputParameters params = Material::validParams();
  params.addClassDescription(
      "Supplies the elastic verification state, local material-mass and mineral-EOS "
      "residual derivatives, material rates, and the production closed-form fixed-pressure "
      "Biot coefficient. "
      "ADConstrainedSkeletonBiotMaterial supplies an independent implicit diagnostic.");
  params.addRequiredCoupledVar("pressure", "Continuous pore-pressure field.");

  params.addParam<MaterialPropertyName>(
      "solid_jacobian_name", "solid_reference_J", "Solid-reference Jacobian J_s.");
  params.addParam<MaterialPropertyName>(
      "solid_jacobian_rate_name", "solid_reference_J_dot", "Material time rate of J_s.");
  params.addRequiredRangeCheckedParam<Real>(
      "skeleton_bulk_modulus", "skeleton_bulk_modulus>0", "Reference drained modulus K.");
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
  params.addRangeCheckedParam<Real>("finite_difference_step", 0.0,
      "finite_difference_step>=0", "Optional fixed-pressure volume perturbation for verification.");
  params.addParam<MaterialPropertyName>("biot_finite_difference_name",
      "solid_biot_fixed_pressure_fd", "Output centered-difference Biot diagnostic.");
  return params;
}

ADLocalElasticMineralBiotMaterial::ADLocalElasticMineralBiotMaterial(
    const InputParameters & parameters)
  : Material(parameters),
    _pressure(adCoupledValue("pressure")),
    _pressure_dot(_fe_problem.isTransient() ? &adCoupledDot("pressure") : nullptr),
    _solid_spatial_mass_ratio(getADMaterialProperty<Real>("solid_spatial_mass_ratio")),
    _solid_spatial_mass_ratio_dot(
        getADMaterialProperty<Real>("solid_spatial_mass_ratio_dot")),
    _J(getADMaterialProperty<Real>("solid_jacobian_name")),
    _J_dot(getADMaterialProperty<Real>("solid_jacobian_rate_name")),
    _skeleton_bulk_modulus(getParam<Real>("skeleton_bulk_modulus")),
    _mineral_bulk_modulus(getParam<Real>("mineral_bulk_modulus")),
    _reference_solid_volume_fraction(getParam<Real>("reference_solid_volume_fraction")),
    _finite_difference_step(getParam<Real>("finite_difference_step")),
    _biot_finite_difference(declareADProperty<Real>(
        getParam<MaterialPropertyName>("biot_finite_difference_name"))),
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

  const Real k = _skeleton_bulk_modulus /
                 (_reference_solid_volume_fraction * _mineral_bulk_modulus);
  const Real alpha = 1.0 - k;
  const ADReal z = matchedLogMineralVolume(_J[_qp], _pressure[_qp],
      _skeleton_bulk_modulus, _mineral_bulk_modulus, _reference_solid_volume_fraction);
  const ADReal D = _mineral_bulk_modulus + alpha * _pressure[_qp] * z;
  _intrinsic_density_ratio[_qp] = 1.0 / z;
  _solid_volume_fraction[_qp] = _reference_solid_volume_fraction *
                               _solid_spatial_mass_ratio[_qp] / _intrinsic_density_ratio[_qp];

  if (MetaPhysicL::raw_value(_solid_volume_fraction[_qp]) <= 0.0 ||
      MetaPhysicL::raw_value(_solid_volume_fraction[_qp]) >= 1.0)
    mooseError(name(), ": computed a solid volume fraction outside (0,1).");

  if (_fe_problem.isTransient())
  {
    _intrinsic_density_ratio_dot[_qp] =
        (alpha * (*_pressure_dot)[_qp] -
         _skeleton_bulk_modulus * _J_dot[_qp] /
             (_reference_solid_volume_fraction * _J[_qp] * z)) / D;
    _solid_volume_fraction_dot[_qp] =
        _reference_solid_volume_fraction *
        (_solid_spatial_mass_ratio_dot[_qp] / _intrinsic_density_ratio[_qp] -
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
      D / (_mineral_bulk_modulus * _intrinsic_density_ratio[_qp]);
  _mineral_eos_volume_fraction_derivative[_qp] = 0.0;
  _mineral_eos_jacobian_derivative[_qp] = k / _J[_qp];

  // State-only closed form; the general constrained material independently
  // solves the two-state residual Jacobian for the verification diagnostic.
  _intrinsic_specific_volume_jacobian_tangent[_qp] =
      _skeleton_bulk_modulus * z / (_reference_solid_volume_fraction * _J[_qp] * D);
  _biot_coefficient[_qp] =
      matchedLogBiotCoefficient(_J[_qp], _pressure[_qp], z, _skeleton_bulk_modulus,
                                _mineral_bulk_modulus, _reference_solid_volume_fraction);
  _mineral_eos_residual[_qp] =
      log(_intrinsic_density_ratio[_qp]) + k * log(_J[_qp]) -
      alpha * _pressure[_qp] * z / _mineral_bulk_modulus;
  _biot_finite_difference[_qp] = 0.0;
  if (_finite_difference_step > 0.0)
  {
    const Real j = MetaPhysicL::raw_value(_J[_qp]);
    const Real p = MetaPhysicL::raw_value(_pressure[_qp]);
    const Real h = _finite_difference_step;
    const Real plus = matchedLogMineralVolume(j + h, p, _skeleton_bulk_modulus,
        _mineral_bulk_modulus, _reference_solid_volume_fraction);
    const Real minus = matchedLogMineralVolume(j - h, p, _skeleton_bulk_modulus,
        _mineral_bulk_modulus, _reference_solid_volume_fraction);
    _biot_finite_difference[_qp] = 1.0 -
        _reference_solid_volume_fraction * (plus - minus) / (2.0 * h);
  }

}
