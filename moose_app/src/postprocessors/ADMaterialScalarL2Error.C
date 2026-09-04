#include "ADMaterialScalarL2Error.h"

#include "Function.h"
#include "metaphysicl/raw_type.h"

#include <cmath>

registerMooseObject("MulticomponentReactiveFlowApp", ADMaterialScalarL2Error);

InputParameters
ADMaterialScalarL2Error::validParams()
{
  InputParameters params = ElementIntegralPostprocessor::validParams();
  params.addRequiredParam<MaterialPropertyName>("property", "AD scalar material property.");
  params.addRequiredParam<FunctionName>("function", "Analytic function to compare against.");
  params.addClassDescription(
      "Computes the L2 error between an AD scalar material property and an analytic function.");
  return params;
}

ADMaterialScalarL2Error::ADMaterialScalarL2Error(const InputParameters & parameters)
  : ElementIntegralPostprocessor(parameters),
    _property(getADMaterialProperty<Real>(getParam<MaterialPropertyName>("property"))),
    _function(getFunction("function"))
{
}

Real
ADMaterialScalarL2Error::getValue() const
{
  return std::sqrt(ElementIntegralPostprocessor::getValue());
}

Real
ADMaterialScalarL2Error::computeQpIntegral()
{
  const Real diff = MetaPhysicL::raw_value(_property[_qp]) - _function.value(_t, _q_point[_qp]);
  return diff * diff;
}
