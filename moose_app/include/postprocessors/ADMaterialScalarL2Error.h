#pragma once

#include "ElementIntegralPostprocessor.h"

class Function;

class ADMaterialScalarL2Error : public ElementIntegralPostprocessor
{
public:
  static InputParameters validParams();

  ADMaterialScalarL2Error(const InputParameters & parameters);

  Real getValue() const override;

protected:
  Real computeQpIntegral() override;

  const ADMaterialProperty<Real> & _property;
  const Function & _function;
};
