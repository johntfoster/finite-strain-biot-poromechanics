#pragma once

#include "DerivativeMaterialInterface.h"
#include "Material.h"

/**
 * Computes the nonlinear Biot coefficient from a constrained local implicit tangent.
 */
class ADConstrainedSkeletonBiotMaterial : public DerivativeMaterialInterface<Material>
{
public:
  static InputParameters validParams();

  ADConstrainedSkeletonBiotMaterial(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  std::vector<ADReal> solveImplicitTangent(std::vector<std::vector<ADReal>> matrix,
                                           std::vector<ADReal> rhs) const;
  std::vector<MaterialPropertyName>
  derivativeNames(const MaterialPropertyName & base,
                  const std::vector<std::string> & symbols,
                  const std::vector<MaterialPropertyName> & supplied,
                  const std::string & param_name) const;

  const MaterialPropertyName _jacobian_symbol;
  const std::vector<std::string> _state_symbols;
  const unsigned int _n_states;
  const Real _reference_specific_volume;
  const Real _pivot_tolerance;
  const bool _reference_accumulations_held_fixed;

  const ADMaterialProperty<Real> & _solid_J;
  const ADMaterialProperty<Real> & _aggregate_solid_volume_fraction;
  std::vector<const ADMaterialProperty<Real> *> _skeleton_component_reference_accumulations;

  std::vector<const ADMaterialProperty<Real> *> _constraint_residuals;
  const std::vector<Real> _constraint_residual_scales;
  std::vector<const ADMaterialProperty<Real> *> _constraint_jacobian_derivatives;
  std::vector<std::vector<const ADMaterialProperty<Real> *>> _constraint_state_derivatives;

  const ADMaterialProperty<Real> * _volume_fraction_jacobian_derivative;
  std::vector<const ADMaterialProperty<Real> *> _volume_fraction_state_derivatives;
  std::vector<bool> _volume_fraction_state_identity;

  std::vector<const ADMaterialProperty<Real> *> _accumulation_jacobian_derivatives;
  std::vector<std::vector<const ADMaterialProperty<Real> *>> _accumulation_state_derivatives;
  std::vector<std::vector<bool>> _accumulation_state_identity;

  ADMaterialProperty<Real> & _intrinsic_specific_volume;
  ADMaterialProperty<Real> & _intrinsic_specific_volume_jacobian_tangent;
  ADMaterialProperty<Real> & _biot_coefficient;
  ADMaterialProperty<Real> & _intrinsic_skeleton_density;
  ADMaterialProperty<Real> & _constraint_norm;
};
