#include "ADReferenceComponentFluxTerm.h"

registerMooseObject("MulticomponentReactiveFlowApp", ADReferenceComponentFluxTerm);

InputParameters
ADReferenceComponentFluxTerm::validParams()
{
  InputParameters params = ADKernel::validParams();
  params.addClassDescription(
      "Atomic reference-flux contribution -Grad(test) dot W. Instantiate independently for "
      "phase advection, unresolved dispersion, molecular diffusion, or any other mass flux in "
      "the reference component balances. A solid-phase deck omits bulk advection and supplies "
      "only J F^{-1} j_disp and J F^{-1} j_diff for "
      "eq:solid_reference_solid_component_balance.");
  params.addRequiredParam<MaterialPropertyName>("reference_flux_name",
                                                 "AD reference component-flux property.");
  params.addParam<Real>("scale", 1.0, "Signed flux multiplier.");
  return params;
}

ADReferenceComponentFluxTerm::ADReferenceComponentFluxTerm(const InputParameters & parameters)
  : ADKernel(parameters),
    _reference_flux(getADMaterialProperty<RealVectorValue>("reference_flux_name")),
    _scale(getParam<Real>("scale"))
{
}

ADReal
ADReferenceComponentFluxTerm::computeQpResidual()
{
  return -_scale * _grad_test[_i][_qp] * _reference_flux[_qp];
}
