#pragma once

#include "MooseError.h"
#include "metaphysicl/raw_type.h"
#include <cmath>

/** Matched logarithmic mineral state on the positive-tangent branch.
 * Solve in log(volume) to preserve positivity. Raw bracketing selects the branch;
 * Newton polishing restores first and nested second AD derivatives of the root.
 */
template <typename T>
T
matchedLogMineralVolume(const T & J, const T & pressure, double K, double Ks, double phi0)
{
  const double k = K / (phi0 * Ks);
  const double alpha = 1.0 - k;
  const double j = MetaPhysicL::raw_value(J);
  const double a = alpha * MetaPhysicL::raw_value(pressure) / Ks;
  if (!(j > 0.0) || !(alpha > 0.0))
    mooseError("Matched logarithmic mineral law requires J>0 and 0<K<phi_s0 K_s.");
  const double c = k * std::log(j);
  auto residual = [a, c](double x) { return x + a * std::exp(x) - c; };
  double lo = c;
  double hi = c;
  if (a < 0.0)
  {
    hi = std::log(-1.0 / a);
    if (!(hi - 1.0 - c > 0.0))
      mooseError("Matched logarithmic mineral law has no stable tensile root.");
  }
  else if (a > 0.0)
  {
    double step = 1.0;
    for (unsigned int i = 0; residual(lo) > 0.0 && i < 100; ++i)
    {
      lo = c - step;
      step *= 2.0;
    }
  }
  for (unsigned int i = 0; i < 100; ++i)
  {
    const double mid = 0.5 * (lo + hi);
    if (residual(mid) > 0.0)
      hi = mid;
    else
      lo = mid;
  }
  T x = 0.5 * (lo + hi);
  for (unsigned int i = 0; i < 3; ++i)
    x -= (x + alpha * pressure * exp(x) / Ks - k * log(J)) /
         (1.0 + alpha * pressure * exp(x) / Ks);
  const T z = exp(x);
  if (!(MetaPhysicL::raw_value(z) > 0.0) ||
      !(MetaPhysicL::raw_value(z) < std::exp(1.0)) ||
      !(1.0 + a * MetaPhysicL::raw_value(z) > 0.0))
    mooseError("Matched logarithmic mineral state is outside the positive-modulus branch.");
  return z;
}
