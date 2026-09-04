#pragma once

#include "Material.h"
#include "RankTwoTensor.h"

/** Applies the inverse Biot transform to P'' and assembles the total first Piola stress. */
class ADReferenceSolidStressMaterial : public Material
{
public:
  static InputParameters validParams();

  ADReferenceSolidStressMaterial(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  const ADMaterialProperty<RankTwoTensor> & _effective_first_piola;
  const ADMaterialProperty<RankTwoTensor> * _reference_prestress;
  const ADMaterialProperty<Real> & _solid_J;
  const ADMaterialProperty<RankTwoTensor> & _solid_F_inv;
  const ADMaterialProperty<RankTwoTensor> * _maxwell_cauchy_stress;

  const ADVariableValue & _equivalent_pressure;
  const ADVariableValue * _equivalent_pressure_enrichment;
  const ADMaterialProperty<Real> * _equivalent_pressure_total;
  const Real _constant_biot_coefficient;
  const ADMaterialProperty<Real> * _biot_coefficient;
  const bool _strip_biot_derivatives;

  ADMaterialProperty<RankTwoTensor> & _prime_first_piola;
  ADMaterialProperty<RankTwoTensor> & _total_first_piola;
};
