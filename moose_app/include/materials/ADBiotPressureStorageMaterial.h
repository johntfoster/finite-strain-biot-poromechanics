#pragma once

#include "Material.h"

/**
 * Exact single-water mass storage pulled to the solid reference.
 *
 * The conserved accumulation is J_s (1-phi_s) rhobar_f(p).  The material
 * evaluates the constant-bulk-modulus fluid EOS and its complete AD material
 * time rate so the transient residual does not require a prescribed Biot
 * storage modulus.
 */
class ADBiotPressureStorageMaterial : public Material
{
public:
  static InputParameters validParams();

  ADBiotPressureStorageMaterial(const InputParameters & parameters);

protected:
  void initQpStatefulProperties() override { computeQpProperties(); }
  void computeQpProperties() override;

  const ADVariableValue & _pressure;
  const ADVariableValue * _pressure_dot;
  const ADMaterialProperty<Real> & _solid_J;
  const ADMaterialProperty<Real> & _solid_J_dot;
  const ADMaterialProperty<Real> & _solid_volume_fraction;
  const ADMaterialProperty<Real> & _solid_volume_fraction_dot;
  const Real _reference_density;
  const Real _reference_pressure;
  const Real _fluid_bulk_modulus;

  ADMaterialProperty<Real> & _intrinsic_density;
  ADMaterialProperty<Real> & _reference_accumulation;
  ADMaterialProperty<Real> & _storage_rate;
};
