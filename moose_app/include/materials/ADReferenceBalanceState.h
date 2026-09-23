#pragma once
#include "Material.h"
#include "RankTwoTensor.h"
/** Constitutive property interface for the common reference balance kernels. */
class ADReferenceBalanceState : public Material
{
public:
  static InputParameters validParams();
  ADReferenceBalanceState(const InputParameters &);
protected:
  void initQpStatefulProperties() override;
  void computeQpProperties() override;
  const ADMaterialProperty<RankTwoTensor> & _stress;
  const ADMaterialProperty<Real> & _accumulation;
  const ADMaterialProperty<RealVectorValue> & _flux;
  const MaterialProperty<Real> & _old;
  ADMaterialProperty<ADRankTwoTensor> & _P;
  ADMaterialProperty<Real> & _mass;
  ADMaterialProperty<RealVectorValue> & _mass_flux;
  ADMaterialProperty<Real> & _rate;
};
