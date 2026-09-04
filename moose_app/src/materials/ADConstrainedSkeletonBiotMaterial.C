#include "ADConstrainedSkeletonBiotMaterial.h"

#include "metaphysicl/raw_type.h"

#include <algorithm>
#include <cmath>

registerMooseObject("MulticomponentReactiveFlowApp", ADConstrainedSkeletonBiotMaterial);

InputParameters
ADConstrainedSkeletonBiotMaterial::validParams()
{
  InputParameters params = Material::validParams();
  params.addClassDescription(
      "Computes the production nonlinear Biot coefficient from local implicit constraints "
      "at each quadrature point. The material solves the implicit state derivative, forms "
      "the intrinsic skeleton density from the solid volume fraction and referential "
      "component masses, and returns the fixed-pressure coefficient with AD state dependence "
      "preserved.");
  params.addRequiredParam<std::vector<MaterialPropertyName>>(
      "constraint_residual_names", "Square local constraint residual vector R_i.");
  params.addRequiredParam<std::vector<std::string>>(
      "implicit_state_symbols",
      "Independent implicit-state symbols y_j used in derivative material property names.");
  params.addParam<std::vector<Real>>(
      "constraint_residual_scales",
      {},
      "Optional per-equation scales used only to form a dimensionless reported constraint norm. "
      "The implicit tangent continues to use the unscaled physical residuals.");
  params.addParam<MaterialPropertyName>(
      "jacobian_symbol",
      "solid_reference_J",
      "Independent constitutive symbol for J_s used in derivative material property names.");
  params.addParam<MaterialPropertyName>(
      "solid_jacobian_name", "solid_reference_J", "AD material property for J_s.");
  params.addRequiredParam<MaterialPropertyName>(
      "aggregate_solid_volume_fraction_name", "Aggregate skeleton solid volume fraction phi_s.");
  params.addRequiredParam<std::vector<MaterialPropertyName>>(
      "skeleton_component_reference_accumulation_names",
      "Registered skeleton solid component referential accumulations J_s rho_a^alpha.");
  params.addParam<std::vector<MaterialPropertyName>>(
      "constraint_jacobian_derivative_names",
      {},
      "Optional dR_i/dJ_s names. Defaults to derivative-property names from each residual "
      "and jacobian_symbol.");
  params.addParam<std::vector<MaterialPropertyName>>(
      "constraint_state_derivative_names",
      {},
      "Optional row-major dR_i/dy_j names. Defaults to derivative-property names from each "
      "residual and implicit_state_symbols.");
  params.addParam<MaterialPropertyName>(
      "volume_fraction_jacobian_derivative_name",
      "",
      "Optional partial(phi_s)/partial(J_s) at fixed implicit states.");
  params.addParam<std::vector<MaterialPropertyName>>(
      "volume_fraction_state_derivative_names",
      {},
      "Optional partial(phi_s)/partial(y_j) names.");
  params.addParam<bool>(
      "reference_accumulations_held_fixed",
      true,
      "If false, include derivatives of the referential component masses in the constrained "
      "mineral-state derivative. If true, fixed reaction-state/component masses are held "
      "fixed for the declared tangent.");
  params.addParam<std::vector<MaterialPropertyName>>(
      "component_reference_accumulation_jacobian_derivative_names",
      {},
      "Optional partial(J_s rho_a^alpha)/partial(J_s) names used when "
      "reference_accumulations_held_fixed=false.");
  params.addParam<std::vector<MaterialPropertyName>>(
      "component_reference_accumulation_state_derivative_names",
      {},
      "Optional row-major partial(J_s rho_a^alpha)/partial(y_j) names used when "
      "reference_accumulations_held_fixed=false.");
  params.addRequiredRangeCheckedParam<Real>(
      "reference_specific_volume",
      "reference_specific_volume > 0",
      "Reference phase specific volume v_s0=1/rho_s0, where rho_s0 is the bulk solid "
      "partial density used by the parent nonlinear Biot definition.");
  params.addRangeCheckedParam<Real>(
      "pivot_tolerance",
      1e-12,
      "pivot_tolerance>0",
      "Raw-value pivot tolerance for the local dense implicit tangent solve.");
  params.addParam<MaterialPropertyName>(
      "intrinsic_specific_volume_name",
      "solid_intrinsic_specific_volume",
      "Output intrinsic skeleton specific volume computed from the solid volume fraction "
      "and referential component masses.");
  params.addParam<MaterialPropertyName>(
      "intrinsic_specific_volume_jacobian_tangent_name",
      "solid_intrinsic_specific_volume_jacobian_tangent",
      "Output constrained fixed-pressure tangent of the intrinsic skeleton specific volume.");
  params.addParam<MaterialPropertyName>(
      "biot_coefficient_name", "solid_biot_coefficient", "Output AD Biot coefficient.");
  params.addParam<MaterialPropertyName>(
      "intrinsic_skeleton_density_name",
      "solid_intrinsic_skeleton_density",
      "Output intrinsic skeleton density.");
  params.addParam<MaterialPropertyName>(
      "constraint_norm_name",
      "solid_biot_constraint_norm",
      "Output Euclidean norm of the local constraint residual vector.");
  return params;
}

ADConstrainedSkeletonBiotMaterial::ADConstrainedSkeletonBiotMaterial(
    const InputParameters & parameters)
  : DerivativeMaterialInterface<Material>(parameters),
    _jacobian_symbol(getParam<MaterialPropertyName>("jacobian_symbol")),
    _state_symbols(getParam<std::vector<std::string>>("implicit_state_symbols")),
    _n_states(_state_symbols.size()),
    _reference_specific_volume(getParam<Real>("reference_specific_volume")),
    _pivot_tolerance(getParam<Real>("pivot_tolerance")),
    _reference_accumulations_held_fixed(getParam<bool>("reference_accumulations_held_fixed")),
    _solid_J(getADMaterialProperty<Real>("solid_jacobian_name")),
    _aggregate_solid_volume_fraction(
        getADMaterialProperty<Real>("aggregate_solid_volume_fraction_name")),
    _constraint_residual_scales(getParam<std::vector<Real>>("constraint_residual_scales")),
    _volume_fraction_jacobian_derivative(nullptr),
    _intrinsic_specific_volume(
        declareADProperty<Real>(getParam<MaterialPropertyName>("intrinsic_specific_volume_name"))),
    _intrinsic_specific_volume_jacobian_tangent(declareADProperty<Real>(
        getParam<MaterialPropertyName>("intrinsic_specific_volume_jacobian_tangent_name"))),
    _biot_coefficient(
        declareADProperty<Real>(getParam<MaterialPropertyName>("biot_coefficient_name"))),
    _intrinsic_skeleton_density(declareADProperty<Real>(
        getParam<MaterialPropertyName>("intrinsic_skeleton_density_name"))),
    _constraint_norm(
        declareADProperty<Real>(getParam<MaterialPropertyName>("constraint_norm_name")))
{
  const auto residual_names =
      getParam<std::vector<MaterialPropertyName>>("constraint_residual_names");
  const auto accumulation_names =
      getParam<std::vector<MaterialPropertyName>>("skeleton_component_reference_accumulation_names");
  if (_n_states == 0)
    paramError("implicit_state_symbols", "Supply at least one implicit state.");
  if (residual_names.size() != _n_states)
    paramError("constraint_residual_names",
               "The number of residuals must equal the number of implicit states.");
  if (!_constraint_residual_scales.empty() && _constraint_residual_scales.size() != _n_states)
    paramError("constraint_residual_scales", "Supply one scale per constraint residual.");
  if (accumulation_names.empty())
    paramError("skeleton_component_reference_accumulation_names",
               "Supply at least one registered skeleton component referential accumulation.");

  _constraint_residuals.reserve(_n_states);
  for (const auto & name : residual_names)
    _constraint_residuals.push_back(&getADMaterialProperty<Real>(name));
  _skeleton_component_reference_accumulations.reserve(accumulation_names.size());
  for (const auto & name : accumulation_names)
    _skeleton_component_reference_accumulations.push_back(&getADMaterialProperty<Real>(name));

  const auto supplied_rj =
      getParam<std::vector<MaterialPropertyName>>("constraint_jacobian_derivative_names");
  const auto rj_names = derivativeNames("",
                                        std::vector<std::string>(),
                                        supplied_rj,
                                        "constraint_jacobian_derivative_names");
  _constraint_jacobian_derivatives.reserve(_n_states);
  for (const auto i : make_range(_n_states))
  {
    const MaterialPropertyName name =
        supplied_rj.empty() ? derivativePropertyNameFirst(residual_names[i], _jacobian_symbol)
                            : rj_names[i];
    _constraint_jacobian_derivatives.push_back(&getADMaterialProperty<Real>(name));
  }

  const auto supplied_ry =
      getParam<std::vector<MaterialPropertyName>>("constraint_state_derivative_names");
  if (!supplied_ry.empty() && supplied_ry.size() != _n_states * _n_states)
    paramError("constraint_state_derivative_names",
               "Supply row-major n_states*n_states entries.");
  _constraint_state_derivatives.resize(_n_states);
  for (const auto i : make_range(_n_states))
  {
    _constraint_state_derivatives[i].reserve(_n_states);
    for (const auto j : make_range(_n_states))
    {
      const MaterialPropertyName name =
          supplied_ry.empty()
              ? derivativePropertyNameFirst(residual_names[i], _state_symbols[j])
              : supplied_ry[i * _n_states + j];
      _constraint_state_derivatives[i].push_back(&getADMaterialProperty<Real>(name));
    }
  }

  const auto supplied_phi_y =
      getParam<std::vector<MaterialPropertyName>>("volume_fraction_state_derivative_names");
  if (!supplied_phi_y.empty() && supplied_phi_y.size() != _n_states)
    paramError("volume_fraction_state_derivative_names", "Supply one entry per implicit state.");
  const auto phi_name = getParam<MaterialPropertyName>("aggregate_solid_volume_fraction_name");
  const bool phi_is_state =
      std::find(_state_symbols.begin(), _state_symbols.end(), phi_name) != _state_symbols.end();
  const auto supplied_phi_j =
      getParam<MaterialPropertyName>("volume_fraction_jacobian_derivative_name");
  if (!supplied_phi_j.empty())
    _volume_fraction_jacobian_derivative = &getADMaterialProperty<Real>(supplied_phi_j);
  else if (!phi_is_state)
    _volume_fraction_jacobian_derivative =
        &getADMaterialProperty<Real>(derivativePropertyNameFirst(phi_name, _jacobian_symbol));

  _volume_fraction_state_derivatives.reserve(_n_states);
  _volume_fraction_state_identity.reserve(_n_states);
  for (const auto j : make_range(_n_states))
  {
    if (supplied_phi_y.empty() && _state_symbols[j] == phi_name)
    {
      _volume_fraction_state_derivatives.push_back(nullptr);
      _volume_fraction_state_identity.push_back(true);
    }
    else
    {
      const MaterialPropertyName name =
          supplied_phi_y.empty() ? derivativePropertyNameFirst(phi_name, _state_symbols[j])
                                 : supplied_phi_y[j];
      _volume_fraction_state_derivatives.push_back(&getADMaterialProperty<Real>(name));
      _volume_fraction_state_identity.push_back(false);
    }
  }

  if (!_reference_accumulations_held_fixed)
  {
    const auto supplied_aj = getParam<std::vector<MaterialPropertyName>>(
        "component_reference_accumulation_jacobian_derivative_names");
    if (!supplied_aj.empty() && supplied_aj.size() != accumulation_names.size())
      paramError("component_reference_accumulation_jacobian_derivative_names",
                 "Supply one entry per component reference accumulation.");
    const auto supplied_ay = getParam<std::vector<MaterialPropertyName>>(
        "component_reference_accumulation_state_derivative_names");
    if (!supplied_ay.empty() && supplied_ay.size() != accumulation_names.size() * _n_states)
      paramError("component_reference_accumulation_state_derivative_names",
                 "Supply row-major n_accumulations*n_states entries.");

    _accumulation_jacobian_derivatives.reserve(accumulation_names.size());
    _accumulation_state_derivatives.resize(accumulation_names.size());
    _accumulation_state_identity.resize(accumulation_names.size());
    for (const auto a : make_range(accumulation_names.size()))
    {
      const bool accumulation_is_state =
          std::find(_state_symbols.begin(), _state_symbols.end(), accumulation_names[a]) !=
          _state_symbols.end();
      if (supplied_aj.empty() && accumulation_is_state)
        _accumulation_jacobian_derivatives.push_back(nullptr);
      else
        _accumulation_jacobian_derivatives.push_back(&getADMaterialProperty<Real>(
            supplied_aj.empty() ? derivativePropertyNameFirst(accumulation_names[a], _jacobian_symbol)
                                : supplied_aj[a]));

      _accumulation_state_derivatives[a].reserve(_n_states);
      _accumulation_state_identity[a].reserve(_n_states);
      for (const auto j : make_range(_n_states))
      {
        if (supplied_ay.empty() && _state_symbols[j] == accumulation_names[a])
        {
          _accumulation_state_derivatives[a].push_back(nullptr);
          _accumulation_state_identity[a].push_back(true);
        }
        else
        {
          const MaterialPropertyName name =
              supplied_ay.empty()
                  ? derivativePropertyNameFirst(accumulation_names[a], _state_symbols[j])
                  : supplied_ay[a * _n_states + j];
          _accumulation_state_derivatives[a].push_back(&getADMaterialProperty<Real>(name));
          _accumulation_state_identity[a].push_back(false);
        }
      }
    }
  }
}

std::vector<MaterialPropertyName>
ADConstrainedSkeletonBiotMaterial::derivativeNames(
    const MaterialPropertyName &,
    const std::vector<std::string> &,
    const std::vector<MaterialPropertyName> & supplied,
    const std::string & param_name) const
{
  if (!supplied.empty() && supplied.size() != _n_states)
    paramError(param_name, "Supply one entry per implicit state.");
  return supplied;
}

std::vector<ADReal>
ADConstrainedSkeletonBiotMaterial::solveImplicitTangent(
    std::vector<std::vector<ADReal>> matrix, std::vector<ADReal> rhs) const
{
  for (const auto k : make_range(_n_states))
  {
    unsigned int pivot = k;
    Real pivot_abs = std::abs(MetaPhysicL::raw_value(matrix[k][k]));
    for (unsigned int i = k + 1; i < _n_states; ++i)
    {
      const Real candidate = std::abs(MetaPhysicL::raw_value(matrix[i][k]));
      if (candidate > pivot_abs)
      {
        pivot = i;
        pivot_abs = candidate;
      }
    }
    if (pivot_abs <= _pivot_tolerance)
      mooseError("ADConstrainedSkeletonBiotMaterial encountered a singular local R_y tangent.");
    if (pivot != k)
    {
      std::swap(matrix[pivot], matrix[k]);
      std::swap(rhs[pivot], rhs[k]);
    }

    for (unsigned int i = k + 1; i < _n_states; ++i)
    {
      const ADReal factor = matrix[i][k] / matrix[k][k];
      matrix[i][k] = 0.0;
      for (unsigned int j = k + 1; j < _n_states; ++j)
        matrix[i][j] -= factor * matrix[k][j];
      rhs[i] -= factor * rhs[k];
    }
  }

  std::vector<ADReal> solution(_n_states, 0.0);
  for (int i = static_cast<int>(_n_states) - 1; i >= 0; --i)
  {
    ADReal value = rhs[i];
    for (unsigned int j = i + 1; j < _n_states; ++j)
      value -= matrix[i][j] * solution[j];
    solution[i] = value / matrix[i][i];
  }
  return solution;
}

void
ADConstrainedSkeletonBiotMaterial::computeQpProperties()
{
  std::vector<std::vector<ADReal>> ry(_n_states, std::vector<ADReal>(_n_states, 0.0));
  std::vector<ADReal> rhs(_n_states, 0.0);
  ADReal residual_square = 0.0;
  for (const auto i : make_range(_n_states))
  {
    const Real residual_scale =
        _constraint_residual_scales.empty() ? 1.0 : _constraint_residual_scales[i];
    residual_square += residual_scale * (*_constraint_residuals[i])[_qp] *
                       residual_scale * (*_constraint_residuals[i])[_qp];
    rhs[i] = -(*_constraint_jacobian_derivatives[i])[_qp];
    for (const auto j : make_range(_n_states))
      ry[i][j] = (*_constraint_state_derivatives[i][j])[_qp];
  }

  const auto y_jacobian = solveImplicitTangent(ry, rhs);

  ADReal phi_jacobian =
      _volume_fraction_jacobian_derivative ? (*_volume_fraction_jacobian_derivative)[_qp] : 0.0;
  for (const auto j : make_range(_n_states))
    phi_jacobian += (_volume_fraction_state_identity[j]
                         ? 1.0
                         : (*_volume_fraction_state_derivatives[j])[_qp]) *
                    y_jacobian[j];

  ADReal accumulation_sum = 0.0;
  for (const auto * accumulation : _skeleton_component_reference_accumulations)
    accumulation_sum += (*accumulation)[_qp];
  if (MetaPhysicL::raw_value(accumulation_sum) <= 0.0)
    mooseError("ADConstrainedSkeletonBiotMaterial requires positive skeleton component "
               "referential accumulation.");

  ADReal accumulation_sum_jacobian = 0.0;
  if (!_reference_accumulations_held_fixed)
    for (const auto a : make_range(_skeleton_component_reference_accumulations.size()))
    {
      ADReal accumulation_jacobian = _accumulation_jacobian_derivatives[a]
                                         ? (*_accumulation_jacobian_derivatives[a])[_qp]
                                         : 0.0;
      for (const auto j : make_range(_n_states))
        accumulation_jacobian += (_accumulation_state_identity[a][j]
                                      ? 1.0
                                      : (*_accumulation_state_derivatives[a][j])[_qp]) *
                                 y_jacobian[j];
      accumulation_sum_jacobian += accumulation_jacobian;
    }

  const ADReal & J = _solid_J[_qp];
  const ADReal & phi = _aggregate_solid_volume_fraction[_qp];
  _intrinsic_specific_volume[_qp] = J * phi / accumulation_sum;
  if (MetaPhysicL::raw_value(_intrinsic_specific_volume[_qp]) <= 0.0)
    mooseError("ADConstrainedSkeletonBiotMaterial computed nonpositive intrinsic skeleton "
               "specific volume.");

  _intrinsic_specific_volume_jacobian_tangent[_qp] =
      phi / accumulation_sum + J * phi_jacobian / accumulation_sum -
      J * phi * accumulation_sum_jacobian / (accumulation_sum * accumulation_sum);
  _biot_coefficient[_qp] =
      1.0 - _intrinsic_specific_volume_jacobian_tangent[_qp] / _reference_specific_volume;
  // rho_s = accumulation_sum / J is the current bulk solid partial density.  The
  // intrinsic skeleton density is instead the reciprocal of the intrinsic specific
  // volume, because phi_s must be divided out of the bulk density.
  _intrinsic_skeleton_density[_qp] =
      accumulation_sum / (J * phi);
  _constraint_norm[_qp] = std::sqrt(MetaPhysicL::raw_value(residual_square));
}
