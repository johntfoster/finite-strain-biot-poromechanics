#pragma once
#include "ADKernel.h"
#include "RankTwoTensor.h"
class ReferenceMomentum:public ADKernel
{
public: static InputParameters validParams();ReferenceMomentum(const InputParameters &);
protected: ADReal computeQpResidual() override;unsigned _component;const ADMaterialProperty<ADRankTwoTensor> &_P;
};
class ReferenceFluidMass:public ADKernel
{
public: static InputParameters validParams();ReferenceFluidMass(const InputParameters &);
protected: ADReal computeQpResidual() override;const ADMaterialProperty<Real> &_mass;const MaterialProperty<Real> &_old;const ADMaterialProperty<RealVectorValue> &_flux;
};
