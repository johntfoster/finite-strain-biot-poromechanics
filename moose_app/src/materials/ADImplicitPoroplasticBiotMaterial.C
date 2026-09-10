//* SPDX-License-Identifier: LGPL-2.1-or-later
#include "ADImplicitPoroplasticBiotMaterial.h"
#include "ChainedADReal.h"
#include "MatchedLogMineralState.h"
#include "metaphysicl/raw_type.h"
#include <array>
#include <cmath>
#include <limits>

registerMooseObject("MulticomponentReactiveFlowApp", ADImplicitPoroplasticBiotMaterial);

namespace ImplicitPoroplastic
{
using MetaPhysicL::raw_value;
template <typename T>
using Matrix = std::array<T, 9>;
template <typename T>
Matrix<T>
identity()
{
  Matrix<T> a{};
  a[0] = a[4] = a[8] = 1.;
  return a;
}
template <typename T>
Matrix<T>
transpose(const Matrix<T> & a)
{
  Matrix<T> b{};
  for (unsigned i = 0; i < 3; ++i)
    for (unsigned j = 0; j < 3; ++j)
      b[3 * i + j] = a[3 * j + i];
  return b;
}
template <typename T>
Matrix<T>
multiply(const Matrix<T> & a, const Matrix<T> & b)
{
  Matrix<T> c{};
  for (unsigned i = 0; i < 3; ++i)
    for (unsigned j = 0; j < 3; ++j)
      for (unsigned k = 0; k < 3; ++k)
        c[3 * i + j] += a[3 * i + k] * b[3 * k + j];
  return c;
}
template <typename T>
T
determinant(const Matrix<T> & a)
{
  return a[0] * (a[4] * a[8] - a[5] * a[7]) - a[1] * (a[3] * a[8] - a[5] * a[6]) +
         a[2] * (a[3] * a[7] - a[4] * a[6]);
}
template <typename T>
Matrix<T>
inverse(const Matrix<T> & a)
{
  const T d = determinant(a);
  Matrix<T> b{{a[4] * a[8] - a[5] * a[7],
               a[2] * a[7] - a[1] * a[8],
               a[1] * a[5] - a[2] * a[4],
               a[5] * a[6] - a[3] * a[8],
               a[0] * a[8] - a[2] * a[6],
               a[2] * a[3] - a[0] * a[5],
               a[3] * a[7] - a[4] * a[6],
               a[1] * a[6] - a[0] * a[7],
               a[0] * a[4] - a[1] * a[3]}};
  for (auto & x : b)
    x /= d;
  return b;
}
template <typename T>
Matrix<T>
exponential(Matrix<T> a)
{
  // Scaling and squaring with a converged Taylor polynomial applies to all
  // symmetric increments, including three distinct principal values.
  Real norm = 0.;
  for (const auto & x : a)
    norm += std::abs(raw_value(x));
  const unsigned squares = norm > 0.5 ? unsigned(std::ceil(std::log2(norm / 0.5))) : 0;
  for (auto & x : a)
    x /= std::pow(2., squares);
  auto sum = identity<T>();
  auto term = sum;
  for (unsigned k = 1; k <= 20; ++k)
  {
    term = multiply(term, a);
    for (unsigned i = 0; i < 9; ++i)
    {
      term[i] /= Real(k);
      sum[i] += term[i];
    }
  }
  for (unsigned k = 0; k < squares; ++k)
    sum = multiply(sum, sum);
  return sum;
}
struct Parameters
{
  Real G, K, Ks, phi0, M, beta, cohesion;
  bool frozen_reference;
};
template <typename T>
struct State
{
  std::array<T, 7> residual{};
  Matrix<T> Fp{}, Fe{}, tau{}, P{};
  T ap{}, B{}, B_el{}, ratio{}, phi{}, mean{}, q{}, yield{};
};

template <typename T>
State<T>
evaluate(const Matrix<T> & F,
         const Matrix<T> & Fpold,
         const T & p,
         const std::array<T, 7> & x,
         const Parameters & c)
{
  using std::log;
  using std::pow;
  using std::sqrt;
  State<T> s;
  const Matrix<T> W{{x[0], x[3], x[4], x[3], x[1], x[5], x[4], x[5], x[2]}};
  s.Fp = multiply(exponential(W), Fpold);
  s.ap = determinant(s.Fp);
  s.Fe = multiply(F, inverse(s.Fp));
  const T J = determinant(F), Je = determinant(s.Fe), logJe = log(Je);
  const Real alpha = 1. - c.K / (c.phi0 * c.Ks);
  const T z = matchedLogMineralVolume(Je, p, c.K, c.Ks, c.phi0);
  const T D = c.Ks + alpha * p * z;
  s.ratio = 1. / z;
  s.phi = c.phi0 * z / J;

  // Closed solution of the fixed-p, fixed-reference-mass, fixed-Fp tangent.
  // d(log Je)/dJ = 1/J: the denominator uses total J even in plastic states.
  s.B = 1. - c.K * z / (J * D);
  const T virgin_z = matchedLogMineralVolume(J, p, c.K, c.Ks, c.phi0);
  s.B_el = 1. - c.K * virgin_z / (J * (c.Ks + alpha * p * virgin_z));

  const auto FeinvT = transpose(inverse(s.Fe));
  T I1 = 0.;
  for (const auto & value : s.Fe)
    I1 += value * value;
  const T volumetric = c.K * (logJe + alpha * p * p * z * z / (c.Ks * D));
  Matrix<T> Pe{};
  for (unsigned i = 0; i < 9; ++i)
    Pe[i] = c.G * pow(Je, -2. / 3.) * (s.Fe[i] - I1 / 3. * FeinvT[i]) + volumetric * FeinvT[i];
  s.tau = multiply(Pe, transpose(s.Fe));
  const T Bused = c.frozen_reference ? s.B_el : s.B;
  for (unsigned i = 0; i < 3; ++i)
    s.tau[4 * i] += (1. - Bused) * p * J;
  const auto M = multiply(multiply(transpose(s.Fe), s.tau), FeinvT);
  s.mean = -(M[0] + M[4] + M[8]) / 3.;
  auto dev = M;
  for (unsigned i = 0; i < 3; ++i)
    dev[4 * i] += s.mean;
  T norm2 = 0.;
  for (const auto & value : dev)
    norm2 += value * value;
  s.q = raw_value(norm2) > 1.e-40 ? sqrt(1.5 * norm2) : T(0.);
  s.yield = s.q - c.M * s.mean - c.cohesion;
  const unsigned index[6] = {0, 4, 8, 1, 2, 5};
  for (unsigned k = 0; k < 6; ++k)
  {
    const T direction = raw_value(s.q) > 1.e-20 ? 1.5 * dev[index[k]] / s.q : T(0.);
    s.residual[k] = x[k] - x[6] * (direction + (k < 3 ? c.beta / 3. : 0.));
  }
  s.residual[6] = s.yield / c.G;
  auto total_tau = s.tau;
  for (unsigned i = 0; i < 3; ++i)
    total_tau[4 * i] -= p * J;
  s.P = multiply(total_tau, transpose(inverse(F)));
  return s;
}

Real
norm(const std::array<ADReal, 7> & r)
{
  Real value = 0.;
  for (const auto & x : r)
  {
    const Real component = std::abs(raw_value(x));
    if (!std::isfinite(component))
      return std::numeric_limits<Real>::infinity();
    value = std::max(value, component);
  }
  return value;
}
std::array<ADReal, 7>
solve(std::array<std::array<ADReal, 7>, 7> A, std::array<ADReal, 7> rhs)
{
  for (unsigned k = 0; k < 7; ++k)
  {
    unsigned pivot = k;
    for (unsigned i = k + 1; i < 7; ++i)
      if (std::abs(raw_value(A[i][k])) > std::abs(raw_value(A[pivot][k])))
        pivot = i;
    if (std::abs(raw_value(A[pivot][k])) < 1.e-14)
      mooseError("Implicit poroplastic update: singular local Jacobian.");
    std::swap(A[k], A[pivot]);
    std::swap(rhs[k], rhs[pivot]);
    for (unsigned i = k + 1; i < 7; ++i)
    {
      const ADReal factor = A[i][k] / A[k][k];
      for (unsigned j = k + 1; j < 7; ++j)
        A[i][j] -= factor * A[k][j];
      rhs[i] -= factor * rhs[k];
    }
  }
  std::array<ADReal, 7> x{};
  for (int i = 6; i >= 0; --i)
  {
    x[i] = rhs[i];
    for (unsigned j = i + 1; j < 7; ++j)
      x[i] -= A[i][j] * x[j];
    x[i] /= A[i][i];
  }
  return x;
}
} // namespace ImplicitPoroplastic

InputParameters
ADImplicitPoroplasticBiotMaterial::validParams()
{
  auto params = Material::validParams();
  params.addClassDescription(
      "Implicit isotropic poroplastic update on the smooth Drucker-Prager cone; "
      "conserves reference solid mass and retains current-state AD derivatives.");
  params.addRequiredCoupledVar("pressure", "Pore pressure.");
  params.addParam<MaterialPropertyName>(
      "deformation_gradient_name", "solid_reference_F", "Total F.");
  params.addRequiredRangeCheckedParam<Real>("shear_modulus", "shear_modulus>0", "G.");
  params.addRequiredRangeCheckedParam<Real>(
      "skeleton_bulk_modulus", "skeleton_bulk_modulus>0", "K.");
  params.addRequiredRangeCheckedParam<Real>(
      "mineral_bulk_modulus", "mineral_bulk_modulus>0", "Ks.");
  params.addRequiredRangeCheckedParam<Real>(
      "reference_solid_volume_fraction",
      "reference_solid_volume_fraction>0 & reference_solid_volume_fraction<1",
      "Reference solid fraction.");
  params.addParam<Real>("dp_friction_slope", 0.6, "Friction slope M.");
  params.addParam<Real>("dp_dilation_slope", 0.4, "Dilation slope beta.");
  params.addParam<Real>("dp_cohesion", 0., "Cohesion.");
  params.addParam<bool>(
      "use_elastic_coefficient_in_trial",
      false,
      "Diagnostic comparison using the virgin coefficient at total J in the driving stress.");
  return params;
}
ADImplicitPoroplasticBiotMaterial::ADImplicitPoroplasticBiotMaterial(const InputParameters & p)
  : Material(p),
    _F(getADMaterialProperty<RankTwoTensor>("deformation_gradient_name")),
    _pressure(adCoupledValue("pressure")),
    _G(getParam<Real>("shear_modulus")),
    _K(getParam<Real>("skeleton_bulk_modulus")),
    _Ks(getParam<Real>("mineral_bulk_modulus")),
    _phi0(getParam<Real>("reference_solid_volume_fraction")),
    _M(getParam<Real>("dp_friction_slope")),
    _beta(getParam<Real>("dp_dilation_slope")),
    _cohesion(getParam<Real>("dp_cohesion")),
    _frozen_reference(getParam<bool>("use_elastic_coefficient_in_trial")),
    _Fp_history(declareProperty<RankTwoTensor>("implicit_plastic_history")),
    _Fp_old(getMaterialPropertyOld<RankTwoTensor>("implicit_plastic_history")),
    _Fp(declareADProperty<RankTwoTensor>("implicit_plastic_Fp")),
    _Fe(declareADProperty<RankTwoTensor>("implicit_plastic_Fe")),
    _tau(declareADProperty<RankTwoTensor>("implicit_plastic_tau_prime")),
    _P(declareADProperty<RankTwoTensor>("implicit_plastic_total_P")),
    _ap(declareADProperty<Real>("plastic_pore_allocation")),
    _B(declareADProperty<Real>("poroplastic_biot_coefficient")),
    _B_el(declareADProperty<Real>("plastic_elastic_biot_coefficient")),
    _ratio(declareADProperty<Real>("implicit_plastic_density_ratio")),
    _phi(declareADProperty<Real>("implicit_plastic_solid_fraction")),
    _gamma(declareADProperty<Real>("plastic_multiplier_increment")),
    _yield(declareADProperty<Real>("plastic_yield_function")),
    _flow_error(declareADProperty<Real>("implicit_plastic_flow_error")),
    _mean(declareADProperty<Real>("plastic_mean_effective_pressure")),
    _q(declareADProperty<Real>("plastic_equivalent_shear_stress")),
    _mass_error(declareADProperty<Real>("implicit_plastic_mass_error"))
{
  if (_K >= _phi0 * _Ks)
    paramError("skeleton_bulk_modulus", "Require K < phi_s0 Ks for stable mineral storage.");
  if (_M < 0. || _beta < 0. || _beta > _M || _cohesion < 0.)
    paramError("dp_dilation_slope", "Require 0 <= beta <= M and nonnegative cohesion.");
}
void
ADImplicitPoroplasticBiotMaterial::initQpStatefulProperties()
{
  _Fp_history[_qp] = RankTwoTensor(RankTwoTensor::initIdentity);
}
void
ADImplicitPoroplasticBiotMaterial::computeQpProperties()
{
  using namespace ImplicitPoroplastic;
  Matrix<ADReal> F{}, old{};
  for (unsigned i = 0; i < 3; ++i)
    for (unsigned j = 0; j < 3; ++j)
    {
      F[3 * i + j] = _F[_qp](i, j);
      old[3 * i + j] = _Fp_old[_qp](i, j);
    }
  if (raw_value(determinant(F)) <= 0. || raw_value(determinant(old)) <= 0.)
    mooseError(name(), ": requires positive total and previous plastic Jacobians.");
  const Parameters c{_G, _K, _Ks, _phi0, _M, _beta, _cohesion, _frozen_reference};
  std::array<ADReal, 7> x{};
  auto state = evaluate(F, old, _pressure[_qp], x, c);
  if (raw_value(state.yield) > 1.e-11 * _G)
  {
    Matrix<ChainedADReal> chained_F{}, chained_old{};
    for (unsigned i = 0; i < 9; ++i)
    {
      chained_F[i] = ChainedADReal(F[i]);
      chained_old[i] = ChainedADReal(old[i]);
    }
    bool converged = false;
    for (unsigned iteration = 0; iteration < 40; ++iteration)
    {
      std::array<std::array<ADReal, 7>, 7> A{};
      for (unsigned column = 0; column < 7; ++column)
      {
        std::array<ChainedADReal, 7> seeded{};
        for (unsigned j = 0; j < 7; ++j)
          seeded[j] = ChainedADReal(x[j], ADReal(j == column ? 1. : 0.));
        const auto residual =
            evaluate(chained_F, chained_old, ChainedADReal(_pressure[_qp]), seeded, c).residual;
        for (unsigned row = 0; row < 7; ++row)
          A[row][column] = residual[row].derivatives();
      }
      const auto correction = solve(A, state.residual);
      const Real current_norm = norm(state.residual);
      Real step = 1.;
      bool accepted = false;
      for (unsigned search = 0; search < 18; ++search)
      {
        auto trial = x;
        for (unsigned j = 0; j < 7; ++j)
          trial[j] -= step * correction[j];
        if (raw_value(trial[6]) >= 0.)
        {
          auto candidate = evaluate(F, old, _pressure[_qp], trial, c);
          const Real candidate_norm = norm(candidate.residual);
          if (std::isfinite(candidate_norm) &&
              (candidate_norm < current_norm || candidate_norm < 1.e-12))
          {
            x = trial;
            state = candidate;
            accepted = true;
            break;
          }
        }
        step *= 0.5;
      }
      if (!accepted)
        mooseError(name(), ": local line search failed on smooth cone branch.");
      if (norm(state.residual) < 1.e-12 && norm(correction) < 1.e-10)
      {
        converged = true;
        break;
      }
    }
    if (!converged)
      mooseError(name(), ": local poroplastic Newton solve did not converge.");
    if (raw_value(state.q) < 1.e-10 * _G)
      mooseError(name(), ": cone apex requires a separate constitutive branch.");
  }
  if (raw_value(state.phi) <= 0. || raw_value(state.phi) >= 1.)
    mooseError(name(), ": solid fraction outside (0,1).");
  for (unsigned i = 0; i < 3; ++i)
    for (unsigned j = 0; j < 3; ++j)
    {
      const unsigned k = 3 * i + j;
      _Fp[_qp](i, j) = state.Fp[k];
      _Fe[_qp](i, j) = state.Fe[k];
      _tau[_qp](i, j) = state.tau[k];
      _P[_qp](i, j) = state.P[k];
      _Fp_history[_qp](i, j) = raw_value(state.Fp[k]);
    }
  _ap[_qp] = state.ap;
  _B[_qp] = state.B;
  _B_el[_qp] = state.B_el;
  _ratio[_qp] = state.ratio;
  _phi[_qp] = state.phi;
  _gamma[_qp] = x[6];
  _yield[_qp] = state.yield;
  _mean[_qp] = state.mean;
  _q[_qp] = state.q;
  ADReal flow_error = 0.;
  for (unsigned i = 0; i < 6; ++i)
    flow_error += state.residual[i] * state.residual[i];
  _flow_error[_qp] = flow_error;
  _mass_error[_qp] = determinant(F) * state.phi * state.ratio - _phi0;
}
