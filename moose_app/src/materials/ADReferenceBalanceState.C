#include "ADReferenceBalanceState.h"
registerMooseObject("MulticomponentReactiveFlowApp", ADReferenceBalanceState);
InputParameters
ADReferenceBalanceState::validParams()
{
  auto p = Material::validParams();
  p.addParam<MaterialPropertyName>("stress", "reference_solid_total_first_piola", "Total first Piola stress.");
  return p;
}
ADReferenceBalanceState::ADReferenceBalanceState(const InputParameters & p)
  : Material(p),
    _stress(getADMaterialProperty<RankTwoTensor>("stress")),
    _accumulation(getADMaterialProperty<Real>("water_reference_accumulation")),
    _flux(getADMaterialProperty<RealVectorValue>("water_reference_mass_flux")),
    _old(getMaterialPropertyOld<Real>("fluid_mass")),
    _P(declareADProperty<ADRankTwoTensor>("first_piola")),
    _mass(declareADProperty<Real>("fluid_mass")),
    _mass_flux(declareADProperty<RealVectorValue>("mass_flux")),
    _rate(declareADProperty<Real>("water_reference_discrete_storage_rate"))
{
  // Promote every upstream initialization dependency to stateful storage.
  // MOOSE calls initialization hooks only for stateful materials, in dependency order.
  getMaterialPropertyOld<RankTwoTensor>("solid_reference_F");
  getMaterialPropertyOld<Real>("solid_spatial_mass_ratio");
  getMaterialPropertyOld<Real>("solid_volume_fraction");
  getMaterialPropertyOld<Real>("water_reference_accumulation");
}

void
ADReferenceBalanceState::initQpStatefulProperties()
{
  // Dependencies are initialized in material order using the actual initial fields.
  _mass[_qp] = _accumulation[_qp];
}
void
ADReferenceBalanceState::computeQpProperties()
{
  _P[_qp] = _stress[_qp];
  _mass[_qp] = _accumulation[_qp];
  _mass_flux[_qp] = _flux[_qp];
  _rate[_qp] = _dt > 0. ? (_mass[_qp] - _old[_qp]) / _dt : ADReal(0.);
}
