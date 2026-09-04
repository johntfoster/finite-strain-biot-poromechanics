#pragma once

#include "Material.h"
#include "RankTwoTensor.h"

/**
 * Darcy mass flux for the single-water Biot specialization.
 */
class ADBiotDarcyReferenceFluxMaterial : public Material
{
public:
  static InputParameters validParams();

  ADBiotDarcyReferenceFluxMaterial(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  const ADMaterialProperty<Real> & _solid_J;
  const ADMaterialProperty<RankTwoTensor> & _inverse_deformation_gradient;
  const ADVariableGradient & _pressure_gradient;
  const ADMaterialProperty<Real> & _intrinsic_density;
  const Real _permeability;
  const Real _viscosity;

  ADMaterialProperty<RankTwoTensor> & _reference_mobility;
  ADMaterialProperty<RealVectorValue> & _reference_mass_flux;
};
