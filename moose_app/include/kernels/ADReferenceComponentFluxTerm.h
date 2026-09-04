#pragma once

#include "ADKernel.h"

/** Atomic weak-divergence term for one named reference component flux. */
class ADReferenceComponentFluxTerm : public ADKernel
{
public:
  static InputParameters validParams();
  ADReferenceComponentFluxTerm(const InputParameters & parameters);

protected:
  ADReal computeQpResidual() override;

  const ADMaterialProperty<RealVectorValue> & _reference_flux;
  const Real _scale;
};
