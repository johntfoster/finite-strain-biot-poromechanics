#pragma once

#include "Material.h"

/**
 * Source-free single-component solid partial-density balance pulled to the solid reference.
 *
 * The numerical field stores the current solid partial density divided by its
 * reference value. The material exposes the corresponding normalized
 * referential solid mass and its complete AD material time rate.
 */
class ADBinarySolidSpatialMassMaterial : public Material
{
public:
  static InputParameters validParams();

  ADBinarySolidSpatialMassMaterial(const InputParameters & parameters);

protected:
  void initQpStatefulProperties() override { computeQpProperties(); }
  void computeQpProperties() override;

  const ADMaterialProperty<Real> & _J;
  const ADMaterialProperty<Real> & _J_dot;
  ADMaterialProperty<Real> & _solid_spatial_mass_ratio;
  ADMaterialProperty<Real> & _solid_spatial_mass_ratio_dot;

  ADMaterialProperty<Real> & _reference_component_accumulation;
  ADMaterialProperty<Real> & _reference_component_storage_rate;
};
