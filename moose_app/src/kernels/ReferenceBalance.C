// SPDX-License-Identifier: Apache-2.0
#include "ReferenceBalance.h"
registerMooseObject("MulticomponentReactiveFlowApp",ReferenceMomentum);
registerMooseObject("MulticomponentReactiveFlowApp",ReferenceFluidMass);
InputParameters ReferenceMomentum::validParams(){auto p=ADKernel::validParams();p.addRequiredParam<unsigned>("component","Momentum component");return p;}
ReferenceMomentum::ReferenceMomentum(const InputParameters &p):ADKernel(p),_component(getParam<unsigned>("component")),_P(getADMaterialProperty<ADRankTwoTensor>("first_piola")){}
ADReal ReferenceMomentum::computeQpResidual(){ADReal r=0;for(unsigned j=0;j<3;++j)r+=_grad_test[_i][_qp](j)*_P[_qp](_component,j);return r;}
InputParameters ReferenceFluidMass::validParams(){return ADKernel::validParams();}
ReferenceFluidMass::ReferenceFluidMass(const InputParameters &p):ADKernel(p),_mass(getADMaterialProperty<Real>("fluid_mass")),_old(getMaterialPropertyOld<Real>("fluid_mass")),_flux(getADMaterialProperty<RealVectorValue>("mass_flux")){}
ADReal ReferenceFluidMass::computeQpResidual(){return _test[_i][_qp]*(_mass[_qp]-_old[_qp])/_dt-_grad_test[_i][_qp]*_flux[_qp];}
