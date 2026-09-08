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
      "regularization.  With biot_feedback = true the coefficient in the single-prime "
      "reconstruction is the implicit poroplastic coefficient B = 1 - (1 - B_el)/a^p "
      "solved consistently with the return map (fixed point over the trial mean, which "
      "depends on B through (1-B) p J I); a frozen-elastic reference pass (B = B_el) is "
      "reported alongside to isolate the B feedback.");
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
      "External Biot coefficient B used in the single-prime reconstruction when "
      "biot_feedback is false.");
  params.addParam<bool>("biot_feedback",
                        false,
                        "Solve the implicit poroplastic coefficient "
                        "B = 1 - (1 - B_el)/a^p consistently with the return map and use it "
                        "in the single-prime reconstruction.");
  params.addParam<MaterialPropertyName>(
      "elastic_biot_coefficient_name",
      "elastic_biot_closed_form",
      "Elastic (a^p = 1) Biot coefficient B_el used as the feedback base and the "
      "frozen-elastic reference.");
  params.addParam<Real>("biot_feedback_tolerance",
                        1.0e-10,
                        "Raw-value fixed-point tolerance for the implicit-B solve.");
  params.addParam<unsigned int>(
      "biot_feedback_max_iterations", 100, "Fixed-point iteration cap for the implicit-B solve.");
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
  params.addParam<MaterialPropertyName>("biot_coefficient_used_name",
                                        "poroplastic_biot_used",
                                        "Output Biot coefficient B used in the single-prime "
                                        "reconstruction.");
  params.addParam<MaterialPropertyName>("plastic_pore_allocation_reference_name",
                                        "plastic_pore_allocation_reference",
                                        "Output a^p from the frozen-elastic (B = B_el) reference pass.");
  params.addParam<MaterialPropertyName>("plastic_multiplier_increment_reference_name",
                                        "plastic_multiplier_increment_reference",
                                        "Output Delta_gamma from the frozen-elastic reference pass.");
  params.addParam<MaterialPropertyName>("mean_effective_pressure_reference_name",
                                        "mean_effective_pressure_reference",
                                        "Output returned compressive-mean p' of the frozen-elastic "
                                        "reference pass.");
  params.addParam<MaterialPropertyName>("equivalent_shear_stress_reference_name",
                                        "equivalent_shear_stress_reference",
                                        "Output returned equivalent shear q' of the frozen-elastic "
                                        "reference pass.");
  params.addParam<MaterialPropertyName>("plastic_pore_allocation_value_name",
                                        "plastic_pore_allocation_value",
                                        "Output the converged plastic pore allocation a^p as a "
                                        "plain (non-AD) value, for consumption as frozen history "
                                        "by the general-path tangent provider.");
  return params;
}

ADDruckerPragerPoroplasticBiotMaterial::ADDruckerPragerPoroplasticBiotMaterial(
    const InputParameters & parameters)
  : Material(parameters),
    _F(getADMaterialProperty<RankTwoTensor>("deformation_gradient_name")),
    _J(getADMaterialProperty<Real>("jacobian_name")),
    _effective_first_piola(getADMaterialProperty<RankTwoTensor>("effective_first_piola_name")),
    _biot_coefficient(nullptr),
    _elastic_biot(nullptr),
    _pressure(adCoupledValue("pressure")),
    _biot_feedback(getParam<bool>("biot_feedback")),
    _feedback_tol(getParam<Real>("biot_feedback_tolerance")),
    _feedback_max_it(getParam<unsigned int>("biot_feedback_max_iterations")),
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
        getParam<MaterialPropertyName>("effective_kirchhoff_stress_name"))),
    _biot_used(
        declareADProperty<Real>(getParam<MaterialPropertyName>("biot_coefficient_used_name"))),
    _a_p_ref(declareADProperty<Real>(
        getParam<MaterialPropertyName>("plastic_pore_allocation_reference_name"))),
    _dgamma_ref(declareADProperty<Real>(
        getParam<MaterialPropertyName>("plastic_multiplier_increment_reference_name"))),
    _mean_p_ref(declareADProperty<Real>(
        getParam<MaterialPropertyName>("mean_effective_pressure_reference_name"))),
    _q_ref(declareADProperty<Real>(
        getParam<MaterialPropertyName>("equivalent_shear_stress_reference_name"))),
    _a_p_value(declareProperty<Real>(
        getParam<MaterialPropertyName>("plastic_pore_allocation_value_name")))
{
  if (_biot_feedback)
    _elastic_biot =
        &getADMaterialProperty<Real>(getParam<MaterialPropertyName>("elastic_biot_coefficient_name"));
  else
    _biot_coefficient =
        &getADMaterialProperty<Real>(getParam<MaterialPropertyName>("biot_coefficient_name"));
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
  using std::abs;
  using std::exp;
  using MetaPhysicL::raw_value;

  const ADReal & J = _J[_qp];
  if (raw_value(J) <= 0.0)
    mooseError(name(), ": requires J_s>0.");

  // Double-prime Kirchhoff stress tau'' = P'' F^T.
  const ADRankTwoTensor tau_pp = _effective_first_piola[_qp] * _F[_qp].transpose();
  const ADReal p = _pressure[_qp];
  const ADRankTwoTensor I = RankTwoTensor(RankTwoTensor::initIdentity);

  // Single-prime trial stress at a given coefficient B:
  //   tau' = tau'' + (1 - B) p J I.
  auto trial_tau = [&](const ADReal & B) {
    ADRankTwoTensor iso = I;
    iso *= (1.0 - B) * p * J;
    return tau_pp + iso;
  };

  // Ideal (constant-strength) radial return for a fixed coefficient B.  On the
  // active branch Delta_gamma = f_trial / (3G + M K beta) (flow potential
  // g = q - beta p), a^p = exp(beta Delta_gamma), and the returned compressive
  // mean and equivalent shear follow; otherwise the step is elastic.
  auto fixed_B_return = [&](const ADReal & B,
                            ADReal & dg,
                            ADReal & ap,
                            ADReal & p_ret,
                            ADReal & q_ret,
                            ADReal & f_tr) {
    const ADRankTwoTensor tau_trial = trial_tau(B);
    ADReal p_trial = 0.0, q_trial = 0.0;
    stressInvariants(tau_trial, p_trial, q_trial);
    f_tr = q_trial - _friction_slope * p_trial - _cohesion;
    dg = 0.0;
    ap = 1.0;
    p_ret = p_trial;
    q_ret = q_trial;
    if (raw_value(f_tr) > 0.0)
    {
      const ADReal denom =
          3.0 * _shear_modulus + _friction_slope * _skeleton_bulk * _dilation_slope;
      dg = f_tr / denom;
      if (raw_value(dg) < 0.0)
        dg = 0.0;
      ap = exp(_dilation_slope * dg);
      q_ret = q_trial - 3.0 * _shear_modulus * dg;
      p_ret = p_trial + _skeleton_bulk * _dilation_slope * dg;
    }
  };

  ADReal B_used; // coefficient used in the single-prime reconstruction
  ADReal dg = 0.0, ap = 1.0, p_out = 0.0, q_out = 0.0, f_tr = 0.0;
  ADReal dg_ref = 0.0, ap_ref = 1.0, p_out_ref = 0.0, q_out_ref = 0.0;

  if (_biot_feedback)
  {
    const ADReal B_el = (*_elastic_biot)[_qp];

    // Frozen-elastic reference: the same return with B held at the elastic
    // coefficient, the value a model that neglects the inelastic correction
    // would use in the driving stress.
    fixed_B_return(B_el, dg_ref, ap_ref, p_out_ref, q_out_ref, f_tr);
    _a_p_ref[_qp] = ap_ref;
    _dgamma_ref[_qp] = dg_ref;
    _mean_p_ref[_qp] = p_out_ref;
    _q_ref[_qp] = q_out_ref;

    // Implicit coefficient: B = 1 - (1 - B_el)/a^p, with a^p set by the return
    // whose trial mean depends on B through (1-B) p J I.  Fixed point on B.
    ADReal B = B_el;
    if (raw_value(f_tr) > 0.0)
    {
      for (unsigned int it = 0; it < _feedback_max_it; ++it)
      {
        ADReal f_trial = 0.0;
        fixed_B_return(B, dg, ap, p_out, q_out, f_trial);
        if (raw_value(f_trial) <= 0.0)
        {
          B = B_el;
          dg = 0.0;
          ap = 1.0;
          break;
        }
        const ADReal B_new = 1.0 - (1.0 - B_el) / ap;
        if (raw_value(abs(B_new - B)) < _feedback_tol)
        {
          B = B_new;
          break;
        }
        B = B_new;
      }
      // Final consistent state at the converged coefficient.
      fixed_B_return(B, dg, ap, p_out, q_out, f_tr);
    }
    else
    {
      dg = 0.0;
      ap = 1.0;
      p_out = p_out_ref;
      q_out = q_out_ref;
    }
    B_used = B;
  }
  else
  {
    B_used = (*_biot_coefficient)[_qp];
    fixed_B_return(B_used, dg, ap, p_out, q_out, f_tr);
    _a_p_ref[_qp] = ap;
    _dgamma_ref[_qp] = dg;
    _mean_p_ref[_qp] = p_out;
    _q_ref[_qp] = q_out;
  }

  // Returned single-prime Kirchhoff stress: deviator along the trial direction
  // scaled to the returned equivalent shear, isotropic part from the returned
  // compressive mean.
  ADRankTwoTensor tau_prime_return = trial_tau(B_used);
  if (raw_value(f_tr) > 0.0)
  {
    const ADRankTwoTensor tau_trial = trial_tau(B_used);
    const ADRankTwoTensor dev_trial = tau_trial.deviatoric();
    ADReal p_trial = 0.0, q_trial = 0.0;
    stressInvariants(tau_trial, p_trial, q_trial);
    ADRankTwoTensor dev_ret = dev_trial;
    if (raw_value(q_trial) > 1.0e-30)
      dev_ret *= (q_out / q_trial);
    else
      dev_ret.zero();
    ADRankTwoTensor iso_ret = I;
    iso_ret *= -p_out;
    tau_prime_return = dev_ret + iso_ret;
  }

  _plastic_multiplier_increment[_qp] = dg;
  _plastic_pore_allocation[_qp] = ap;
  _mean_effective_pressure[_qp] = p_out;
  _equivalent_shear_stress[_qp] = q_out;
  _yield_function[_qp] = q_out - _friction_slope * p_out - _cohesion;
  _biot_used[_qp] = B_used;
  _effective_kirchhoff_stress[_qp] = tau_prime_return;
  _a_p_value[_qp] = raw_value(ap);
}
