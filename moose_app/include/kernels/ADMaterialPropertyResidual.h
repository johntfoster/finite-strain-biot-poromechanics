#pragma once

#include "ADKernelValue.h"

/** Weak algebraic residual using an AD material property. */
class ADMaterialPropertyResidual : public ADKernelValue
{
public:
  static InputParameters validParams();

  ADMaterialPropertyResidual(const InputParameters & parameters);

protected:
  ADReal precomputeQpResidual() override;

  const ADMaterialProperty<Real> & _property;
  const Real _scale;
};
