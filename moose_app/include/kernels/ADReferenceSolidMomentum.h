#pragma once

#include "ADKernel.h"

class Function;

/** Quasi-static solid-skeleton momentum component on the solid reference configuration. */
class ADReferenceSolidMomentum : public ADKernel
{
public:
  static InputParameters validParams();

  ADReferenceSolidMomentum(const InputParameters & parameters);

protected:
  ADReal computeQpResidual() override;

  const unsigned int _component;
  const unsigned int _dim;

  const ADMaterialProperty<RankTwoTensor> & _first_piola_stress;
  const ADMaterialProperty<Real> & _solid_J;

  std::vector<const ADVariableValue *> _current_volume_force;
  const Function & _reference_body_force;
};
