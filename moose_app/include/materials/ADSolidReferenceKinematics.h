#pragma once

#include "Material.h"
#include "RankTwoTensor.h"

class ADSolidReferenceKinematics : public Material
{
public:
  static InputParameters validParams();

  ADSolidReferenceKinematics(const InputParameters & parameters);

protected:
  void initQpStatefulProperties() override { computeQpProperties(); }
  void computeQpProperties() override;

  const unsigned int _ndisp;
  std::vector<const ADVariableGradient *> _grad_disp;
  std::vector<const VariableGradient *> _grad_disp_dot;
  std::vector<const VariableValue *> _disp_dot_du;

  ADMaterialProperty<RankTwoTensor> & _F;
  ADMaterialProperty<Real> & _J;
  ADMaterialProperty<Real> & _J_dot;
  ADMaterialProperty<RankTwoTensor> & _F_inv;
  ADMaterialProperty<RankTwoTensor> & _J_F_inv;
};
