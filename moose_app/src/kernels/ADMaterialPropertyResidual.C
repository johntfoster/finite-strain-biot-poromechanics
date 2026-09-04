#include "ADMaterialPropertyResidual.h"

registerMooseObject("MulticomponentReactiveFlowApp", ADMaterialPropertyResidual);

InputParameters
ADMaterialPropertyResidual::validParams()
{
  InputParameters params = ADKernelValue::validParams();
  params.addClassDescription(
      "Adds an AD material property directly as a weak algebraic residual. This is used for "
      "flash, closure, and diagnostic equations whose residual is assembled by a material.");
  params.addRequiredParam<MaterialPropertyName>("property", "Material property used as the residual.");
  params.addParam<Real>("scale", 1.0, "Constant multiplier applied to the residual.");
  return params;
}

ADMaterialPropertyResidual::ADMaterialPropertyResidual(const InputParameters & parameters)
  : ADKernelValue(parameters),
    _property(getADMaterialProperty<Real>("property")),
    _scale(getParam<Real>("scale"))
{
}

ADReal
ADMaterialPropertyResidual::precomputeQpResidual()
{
  return _scale * _property[_qp];
}
