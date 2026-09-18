//* SPDX-License-Identifier: LGPL-2.1-or-later
#pragma once
#include "NodalSum.h"

/** Sum nodal degrees of freedom, excluding interpolation-only geometry nodes. */
class NodalDofSum : public NodalSum
{
public:
  static InputParameters validParams();
  NodalDofSum(const InputParameters & parameters) : NodalSum(parameters) {}
  void execute() override;
};
