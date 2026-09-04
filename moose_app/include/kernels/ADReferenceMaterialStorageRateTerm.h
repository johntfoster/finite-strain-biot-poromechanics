#pragma once

#include "ADTimeKernelValue.h"

/** Atomic conservative storage term supplied as an AD reference-rate property. */
class ADReferenceMaterialStorageRateTerm : public ADTimeKernelValue
{
public:
  static InputParameters validParams();
  ADReferenceMaterialStorageRateTerm(const InputParameters & parameters);

protected:
  ADReal precomputeQpResidual() override;

  const ADMaterialProperty<Real> & _storage_rate;
  const Real _scale;
};
