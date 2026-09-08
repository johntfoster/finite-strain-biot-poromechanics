//* This file is part of the nonlinear-Biot implicit-AD application.
//* SPDX-License-Identifier: LGPL-2.1-or-later

#include "ADTensorialPoroplasticBiotMaterial.h"

#include "metaphysicl/raw_type.h"

#include <cmath>

registerMooseObject("MulticomponentReactiveFlowApp", ADTensorialPoroplasticBiotMaterial);

InputParameters
ADTensorialPoroplasticBiotMaterial::validParams()
{
  InputParameters params = Material::validParams();
  params.addClassDescription(
      "Stateful finite-deformation multiplicative ideal Drucker-Prager return mapping "
      "(canonical inelastic update): F = F^e F^p with stored aggregate plastic factor F^p "
      "(det F^p = a^p).  Elastic trial F^e_tr = F (F^p_n)^-1; drained skeleton and mineral "
      "response evaluated on the trial; ideal DP radial return updating the isochoric and "
      "pore-allocation mechanisms by the exact symmetric exponential.  Inactive trial => "
      "elastic step with frozen plastic state (immediate elastic unloading; reload re-yield).");
  params.addRequiredCoupledVar("pressure", "Compression-positive pore pressure p.");
  params.addParam<MaterialPropertyName>(
      "deformation_gradient_name", "solid_reference_F", "Solid-reference deformation gradient F.");
  params.addParam<MaterialPropertyName>(
      "jacobian_name", "solid_reference_J", "Solid-reference Jacobian J = det F.");
  params.addRequiredRangeCheckedParam<Real>(
      "shear_modulus", "shear_modulus>0", "Drained isochoric shear modulus G.");
  params.addRequiredRangeCheckedParam<Real>(
      "skeleton_bulk_modulus", "skeleton_bulk_modulus>0", "Drained skeleton bulk modulus K_sk.");
  params.addRequiredRangeCheckedParam<Real>(
      "mineral_bulk_modulus", "mineral_bulk_modulus>0", "Mineral bulk modulus K_s.");
  params.addRequiredRangeCheckedParam<Real>("reference_solid_volume_fraction",
                                            "reference_solid_volume_fraction>0 & "
                                            "reference_solid_volume_fraction<1",
                                            "Reference solid volume fraction phi_s0.");
  params.addParam<Real>("dp_friction_slope", 1.2, "DP friction slope M.");
  params.addParam<Real>("dp_dilation_slope", 0.4, "DP dilation slope beta (0 <= beta <= M).");
  params.addParam<Real>("dp_cohesion", 0.0, "DP cohesion (zero for cohesionless).");
  params.addParam<bool>("use_elastic_coefficient_in_trial",
                        false,
                        "Frozen-elastic reference: use the elastic coefficient B_el (a^p = 1) "
                        "in the single-prime reconstruction instead of the pore-allocation-"
                        "corrected coefficient, isolating the coefficient feedback at nonzero "
                        "pore pressure.  The plastic mechanism is otherwise unchanged.");
  return params;
}

ADTensorialPoroplasticBiotMaterial::ADTensorialPoroplasticBiotMaterial(
    const InputParameters & parameters)
  : Material(parameters),
    _F(getADMaterialProperty<RankTwoTensor>("deformation_gradient_name")),
    _J(getADMaterialProperty<Real>("jacobian_name")),
    _pressure(adCoupledValue("pressure")),
    _shear_modulus(getParam<Real>("shear_modulus")),
    _skeleton_bulk(getParam<Real>("skeleton_bulk_modulus")),
    _mineral_bulk(getParam<Real>("mineral_bulk_modulus")),
    _phi_s0(getParam<Real>("reference_solid_volume_fraction")),
    _friction_slope(getParam<Real>("dp_friction_slope")),
    _dilation_slope(getParam<Real>("dp_dilation_slope")),
    _cohesion(getParam<Real>("dp_cohesion")),
    _use_elastic_coefficient_in_trial(getParam<bool>("use_elastic_coefficient_in_trial")),
    _F_p(declareProperty<RankTwoTensor>("plastic_F_p")),
    _F_p_old(getMaterialPropertyOld<RankTwoTensor>("plastic_F_p")),
    _a_p(declareProperty<Real>("plastic_a_p")),
    _a_p_old(getMaterialPropertyOld<Real>("plastic_a_p")),
    _a_p_out(declareADProperty<Real>("plastic_pore_allocation")),
    _a_p_value(declareProperty<Real>("plastic_pore_allocation_value")),
    _increment(declareADProperty<Real>("plastic_multiplier_increment")),
    _yield_function(declareADProperty<Real>("plastic_yield_function")),
    _mean_pressure(declareADProperty<Real>("plastic_mean_effective_pressure")),
    _equiv_shear(declareADProperty<Real>("plastic_equivalent_shear_stress")),
    _biot(declareADProperty<Real>("poroplastic_biot_coefficient")),
    _biot_elastic(declareADProperty<Real>("plastic_elastic_biot_coefficient")),
    _elastic_trial(declareADProperty<RankTwoTensor>("plastic_elastic_trial_F")),
    _kirchhoff(declareADProperty<RankTwoTensor>("solid_prime_kirchhoff_stress"))
{
}

void
ADTensorialPoroplasticBiotMaterial::stressInvariants(const ADRankTwoTensor & tau,
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
ADTensorialPoroplasticBiotMaterial::initQpStatefulProperties()
{
  _F_p[_qp] = RankTwoTensor(RankTwoTensor::initIdentity);
  _a_p[_qp] = 1.0;
  _a_p_value[_qp] = 1.0;
}

void
ADTensorialPoroplasticBiotMaterial::computeQpProperties()
{
  using std::exp;
  using std::log;
  using std::sqrt;
  using MetaPhysicL::raw_value;

  const ADRankTwoTensor & F = _F[_qp];
  const ADReal & J = _J[_qp];
  if (raw_value(J) <= 0.0)
    mooseError(name(), ": requires J>0.");
  const ADReal p = _pressure[_qp];

  // Plastic history; virgin if unset (a^p = 0 marks uninitialized).
  RankTwoTensor Fp_old;
  Real ap_old = raw_value(_a_p_old[_qp]);
  if (ap_old > 0.0)
    Fp_old = _F_p_old[_qp];
  else
  {
    ap_old = 1.0;
    Fp_old = RankTwoTensor(RankTwoTensor::initIdentity);
  }
  if (ap_old <= 0.0)
    mooseError(name(), ": requires stored a^p > 0.");
  const Real detFp_old = Fp_old.det();
  if (detFp_old <= 0.0)
    mooseError(name(), ": requires det(F^p_n) > 0.");

  const RankTwoTensor I2 = RankTwoTensor(RankTwoTensor::initIdentity);

  // Elastic trial: F^e_tr = F (F^p_n)^-1.
  const ADRankTwoTensor Fe_tr = F * Fp_old.inverse();
  const ADReal Je = Fe_tr.det();
  if (raw_value(Je) <= 0.0)
    mooseError(name(), ": requires det(F^e_tr) > 0.");
  _elastic_trial[_qp] = Fe_tr;

  // Drained skeleton + mineral response on the elastic trial (repository
  // decoupled potential; first-loading limit Fe_tr = F reproduces the elastic
  // verification response).
  const ADReal log_Je = log(Je);
  const ADReal q = -_skeleton_bulk * log_Je / (_phi_s0 * Je);
  const ADReal q_jacobian = -_skeleton_bulk * (1.0 - log_Je) / (_phi_s0 * Je * Je);
  const ADRankTwoTensor Fe_inv_T = Fe_tr.inverse().transpose();
  const ADReal I1 = Fe_tr.doubleContraction(Fe_tr);
  const ADReal Jm23 = pow(Je, -2.0 / 3.0);
  const ADRankTwoTensor skeleton_first_piola =
      _shear_modulus * Jm23 * (Fe_tr - (I1 / 3.0) * Fe_inv_T) +
      _skeleton_bulk * log_Je * Fe_inv_T;

  const ADReal density_inverse = exp(-(p + q) / _mineral_bulk);
  const ADReal density_inverse_at_zero = exp(-q / _mineral_bulk);
  const ADRankTwoTensor q_deformation_gradient = q_jacobian * Je * Fe_inv_T;
  const ADRankTwoTensor effective_first_piola =
      skeleton_first_piola +
      _phi_s0 * (density_inverse - density_inverse_at_zero +
                 p * density_inverse / _mineral_bulk) *
          q_deformation_gradient;

  // Double-prime and single-prime Kirchhoff stresses on the elastic trial.
  const ADRankTwoTensor tau_pp = effective_first_piola * Fe_tr.transpose();

  // Elastic coefficient of the same drained skeleton and mineral evaluated at
  // the *total* deformation J (route-A convention: the value the step would
  // take if it were elastic).  The pore-allocation correction
  //   B = 1 - (1 - B_el(J))/a^p
  // with B_el at total J is the reduced closed form verified against the
  // general fixed-history fixed-pressure tangent of the active plastic local
  // system; the single-prime reconstruction uses the same coefficient at the
  // frozen (previous) allocation.
  const ADReal q_tot = -_skeleton_bulk * log(J) / (_phi_s0 * J);
  const ADReal q_jacobian_tot = -_skeleton_bulk * (1.0 - log(J)) / (_phi_s0 * J * J);
  const ADReal ratio_tot = exp((p + q_tot) / _mineral_bulk);
  const ADReal B_el_tot = 1.0 + _phi_s0 * q_jacobian_tot / (_mineral_bulk * ratio_tot);
  // Coefficient used in the single-prime reconstruction: the pore-allocation-
  // corrected coefficient at the frozen (previous) allocation, or (in the
  // frozen-elastic reference) the elastic coefficient B_el.
  const ADReal B_used = _use_elastic_coefficient_in_trial
                            ? B_el_tot
                            : 1.0 - (1.0 - B_el_tot) / ap_old;

  ADRankTwoTensor iso = I2;
  iso *= (1.0 - B_used) * p * J;
  const ADRankTwoTensor tau_tr = tau_pp + iso;

  ADReal p_tr = 0.0, q_tr = 0.0;
  stressInvariants(tau_tr, p_tr, q_tr);
  const ADRankTwoTensor dev_tr = tau_tr.deviatoric();
  const ADReal f_tr = q_tr - _friction_slope * p_tr - _cohesion;

  ADReal dg = 0.0;
  RankTwoTensor Fp_new = Fp_old;
  Real ap_new = ap_old;
  ADRankTwoTensor tau_ret = tau_tr;
  ADReal p_out = p_tr, q_out = q_tr;

  if (raw_value(f_tr) > 0.0)
  {
    const ADReal denom =
        3.0 * _shear_modulus + _friction_slope * _skeleton_bulk * _dilation_slope;
    dg = f_tr / denom;
    if (raw_value(dg) < 0.0)
      dg = 0.0;

    q_out = q_tr - 3.0 * _shear_modulus * dg;
    p_out = p_tr + _skeleton_bulk * _dilation_slope * dg;

    // Flow increment in the aggregate plastic frame:
    //   W = dg * ( (3/2) dev(tau'_tr)/q_tr + (beta/3) I ).
    ADRankTwoTensor Ndev = dev_tr;
    if (raw_value(q_tr) > 1.0e-30)
      Ndev *= (1.5 * dg / q_tr);
    else
      Ndev.zero();
    ADRankTwoTensor Wsp = I2;
    Wsp *= (_dilation_slope * dg / 3.0);
    const ADRankTwoTensor W = Ndev + Wsp;

    // Exact exponential of the symmetric increment:
    // exp(W) = exp(sI) [ I + (sinh(phi)/phi) A + (cosh(phi)-1)/phi^2 A^2 ],
    // A = dev(W) traceless, sI = tr(W)/3, phi^2 = tr(A A)/2.
    const ADRankTwoTensor A = W.deviatoric();
    const ADReal sI = W.trace() / 3.0;
    const ADReal phi2 = 0.5 * A.doubleContraction(A);
    ADReal shp, chp;
    if (raw_value(phi2) < 1.0e-14)
    {
      shp = 1.0 + phi2 / 6.0;
      chp = 0.5 + phi2 / 24.0;
    }
    else
    {
      const ADReal phi = sqrt(phi2);
      shp = sinh(phi) / phi;
      chp = (cosh(phi) - 1.0) / phi2;
    }
    ADRankTwoTensor Mexp = I2 + shp * A + chp * (A * A);
    Mexp *= exp(sI);
    Fp_new = raw_value(Mexp * Fp_old); // raw tensor for stored history
    ap_new = Fp_new.det();

    // Returned stress: deviator along the trial direction, isotropic part from
    // the returned compressive mean.
    ADRankTwoTensor dev_ret = dev_tr;
    if (raw_value(q_tr) > 1.0e-30)
      dev_ret *= (q_out / q_tr);
    else
      dev_ret.zero();
    ADRankTwoTensor iso_ret = I2;
    iso_ret *= -p_out;
    tau_ret = dev_ret + iso_ret;
  }

  // Store history (raw values; history is frozen for the AD tangent).
  _F_p[_qp] = Fp_new;
  _a_p[_qp] = ap_new;
  _a_p_value[_qp] = ap_new;

  // Diagnostics.  Reported coefficient uses the total-J elastic base and the
  // current plastic pore allocation (route-A closed form, eq. 4.x).
  _a_p_out[_qp] = ap_new;
  _increment[_qp] = dg;
  _yield_function[_qp] = q_out - _friction_slope * p_out - _cohesion;
  _mean_pressure[_qp] = p_out;
  _equiv_shear[_qp] = q_out;
  _biot[_qp] = 1.0 - (1.0 - B_el_tot) / ap_new;
  _biot_elastic[_qp] = B_el_tot;
  _kirchhoff[_qp] = tau_ret;
}
