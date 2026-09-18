//* SPDX-License-Identifier: LGPL-2.1-or-later
#include "NodalDofSum.h"
#include "MooseVariableBase.h"
#include "SystemBase.h"
registerMooseObject("MulticomponentReactiveFlowApp", NodalDofSum);
InputParameters
NodalDofSum::validParams()
{
  auto params = NodalSum::validParams();
  params.addClassDescription("Sums values only on nodes carrying degrees of freedom of the selected variable.");
  return params;
}
void
NodalDofSum::execute()
{
  // A Q1 field on QUAD9 has values at midside geometry nodes but no DOFs there.
  if (_current_node->n_dofs(_var->sys().number(), _var->number()))
    NodalSum::execute();
}
