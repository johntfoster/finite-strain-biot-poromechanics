//* This file is part of the nonlinear-Biot implicit-AD application.
//* SPDX-License-Identifier: LGPL-2.1-or-later

#include "ADDruckerPragerPoroplasticBiotMaterial.h"

#include "metaphysicl/raw_type.h"

#include <cmath>

registerMooseObject("MulticomponentReactiveFlowApp", ADDruckerPragerPoroplasticBiotMaterial);

InputParameters
ADDruckerPragerPoroplasticBiotMaterial::validParams()
{
  InputParameters params = Material::validParams();
  params.addClassDescription(
      "Drucker-Prager-type poroplastic return mapping on the single-prime Kirchhoff "
      "stress tau' = P''F^T + (1-B) p J I.  Ideal (constant-strength) DP surface "
      "f = q' - M p' <= 0 with flow potential g = q' - beta p' is integrated by the "
      "exact radial return Delta_gamma = f/(3G + M K beta), giving the plastic pore "
      "allocation a^p = exp(beta Delta_gamma).  Inactive branch collapses to the "
      "elastic trial (Delta_gamma = 0, a^p = 1).  Rate independent: no viscous "
      "regularization.");
  params.addRequiredCoupledVar("pressure", "Compression-positive pore pressure p.");
  params.addParam<MaterialPropertyName>(
      "deformation_gradient_name", "solid_reference_F", "Solid-reference deformation gradient F.");
  params.addParam<MaterialPropertyName>(
      "jacobian_name", "solid_reference_J", "Solid-reference Jacobian J_s.");
  params.addParam<MaterialPropertyName>("effective_first_piola_name",
                                        "solid_effective_first_piola",
                                        "Double-prime effective first Piola stress P''.");
  params.addParam<MaterialPropertyName>(
      "biot_coefficient_name",
      "solid_biot_coefficient",
      "Current implicit Biot coefficient B used in the single-prime reconstruction.");
  params.addRequiredRangeCheckedParam<Real>(
      "shear_modulus", "shear_modulus>0", "Drained isochoric shear modulus G.");
  params.addRequiredRangeCheckedParam<Real>(
      "skeleton_bulk_modulus", "skeleton_bulk_modulus>0", "Drained skeleton bulk modulus K_sk.");
  params.addParam<Real>("dp_friction_slope", 1.2, "DP friction slope M = mu + beta.");
  params.addParam<Real>("dp_dilation_slope", 0.4, "DP dilation slope beta (0 <= beta <= M).");
  params.addParam<Real>("dp_cohesion", 0.0, "DP cohesion (zero for cohesionless).");
  params.addParam<MaterialPropertyName>("plastic_pore_allocation_name",
                                        "plastic_pore_allocation",
                                        "Output plastic pore allocation a^p.");
  params.addParam<MaterialPropertyName>("plastic_multiplier_increment_name",
                                        "plastic_multiplier_increment",
                                        "Output plastic increment Delta_gamma.");
  params.addParam<MaterialPropertyName>(
      "yield_function_name", "plastic_yield_function", "Output DP yield function f.");
  params.addParam<MaterialPropertyName>("mean_effective_pressure_name",
                                        "plastic_mean_effective_pressure",
                                        "Output compressive-positive mean single-prime pressure p'.");
  params.addParam<MaterialPropertyName>("equivalent_shear_stress_name",
                                        "plastic_equivalent_shear_stress",
                                        "Output von Mises single-prime stress q'.");
  params.addParam<MaterialPropertyName>("effective_kirchhoff_stress_name",
                                        "solid_prime_kirchhoff_stress",
                                        "Output returned single-prime Kirchhoff stress tau'.");
  return params;
}

ADDruckerPragerPoroplasticBiotMaterial::ADDruckerPragerPoroplasticBiotMaterial(
    const InputParameters & parameters)
  : Material(parameters),
    _F(getADMaterialProperty<RankTwoTensor>("deformation_gradient_name")),
    _J(getADMaterialProperty<Real>("jacobian_name")),
    _effective_first_piola(getADMaterialProperty<RankTwoTensor>("effective_first_piola_name")),
    _biot_coefficient(getADMaterialProperty<Real>("biot_coefficient_name")),
    _pressure(adCoupledValue("pressure")),
    _shear_modulus(getParam<Real>("shear_modulus")),
    _skeleton_bulk(getParam<Real>("skeleton_bulk_modulus")),
    _friction_slope(getParam<Real>("dp_friction_slope")),
    _dilation_slope(getParam<Real>("dp_dilation_slope")),
    _cohesion(getParam<Real>("dp_cohesion")),
    _plastic_pore_allocation(
        declareADProperty<Real>(getParam<MaterialPropertyName>("plastic_pore_allocation_name"))),
    _plastic_multiplier_increment(declareADProperty<Real>(
        getParam<MaterialPropertyName>("plastic_multiplier_increment_name"))),
    _yield_function(
        declareADProperty<Real>(getParam<MaterialPropertyName>("yield_function_name"))),
    _mean_effective_pressure(
        declareADProperty<Real>(getParam<MaterialPropertyName>("mean_effective_pressure_name"))),
    _equivalent_shear_stress(
        declareADProperty<Real>(getParam<MaterialPropertyName>("equivalent_shear_stress_name"))),
    _effective_kirchhoff_stress(declareADProperty<RankTwoTensor>(
        getParam<MaterialPropertyName>("effective_kirchhoff_stress_name")))
{
}

void
ADDruckerPragerPoroplasticBiotMaterial::stressInvariants(const ADRankTwoTensor & tau,
                                                         ADReal & p,
                                                         ADReal & q) const
{
  using std::sqrt;
  const ADRankTwoTensor dev = tau.deviatoric();
  const ADReal dev2 = dev.doubleContraction(dev);
  p = -tau.trace() / 3.0;
  q = dev2 == 0.0 ? 0.0 : sqrt(1.5 * dev2);
}

void
ADDruckerPragerPoroplasticBiotMaterial::computeQpProperties()
{
  using std::exp;
  using MetaPhysicL::raw_value;

  const ADReal & J = _J[_qp];
  if (raw_value(J) <= 0.0)
    mooseError(name(), ": requires J_s>0.");

  // Double-prime Kirchhoff stress tau'' = P'' F^T, then single-prime trial
  // tau' = tau'' + (1 - B) p J I  (manuscript single-prime reconstruction).
  const ADRankTwoTensor tau_pp = _effective_first_piola[_qp] * _F[_qp].transpose();
  const ADReal p = _pressure[_qp];
  const ADRankTwoTensor I = RankTwoTensor(RankTwoTensor::initIdentity);
  ADRankTwoTensor iso = I;
  iso *= (1.0 - _biot_coefficient[_qp]) * p * J;
  const ADRankTwoTensor tau_prime_trial = tau_pp + iso;

  // Invariants (compressive-positive mean).
  ADReal p_trial = 0.0, q_trial = 0.0;
  stressInvariants(tau_prime_trial, p_trial, q_trial);

  const ADReal f_trial = q_trial - _friction_slope * p_trial - _cohesion;
  const ADRankTwoTensor dev_trial = tau_prime_trial.deviatoric();

  ADReal Delta_gamma = 0.0;
  ADReal a_p = 1.0;
  ADRankTwoTensor tau_prime_return = tau_prime_trial;

  if (raw_value(f_trial) > 0.0)
  {
    // Ideal (constant-strength) DP radial return, backward-Euler equivalent.
    // Flow potential g = q - beta p gives volumetric plastic rate tr(L^p)=-beta*gamma_dot,
    // so Delta_gamma = f_trial / (3G + M*K*beta).
    const ADReal denom =
        3.0 * _shear_modulus + _friction_slope * _skeleton_bulk * _dilation_slope;
    Delta_gamma = f_trial / denom;
    if (raw_value(Delta_gamma) < 0.0)
      Delta_gamma = 0.0;

    a_p = exp(_dilation_slope * Delta_gamma);

    ADReal p_out = 0.0, q_out = 0.0;
    q_out = q_trial - 3.0 * _shear_modulus * Delta_gamma;
    p_out = p_trial + _skeleton_bulk * _dilation_slope * Delta_gamma;

    // Returned deviator along the trial direction; returned mean from p_out.
    ADRankTwoTensor dev_ret = dev_trial;
    if (raw_value(q_trial) > 1.0e-30)
      dev_ret *= (q_out / q_trial);
    else
      dev_ret.zero();

    ADRankTwoTensor iso_ret = I;
    iso_ret *= -p_out;
    tau_prime_return = dev_ret + iso_ret;

    _mean_effective_pressure[_qp] = p_out;
    _equivalent_shear_stress[_qp] = q_out;
  }
  else
  {
    _mean_effective_pressure[_qp] = p_trial;
    _equivalent_shear_stress[_qp] = q_trial;
  }

  _plastic_multiplier_increment[_qp] = Delta_gamma;
  _plastic_pore_allocation[_qp] = a_p;
  _yield_function[_qp] = _equivalent_shear_stress[_qp] -
                         _friction_slope * _mean_effective_pressure[_qp] - _cohesion;
  _effective_kirchhoff_stress[_qp] = tau_prime_return;
}
