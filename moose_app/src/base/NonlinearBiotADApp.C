#include "NonlinearBiotADApp.h"

#include "AppFactory.h"
#include "Moose.h"
#include "MooseSyntax.h"
#include "SolidMechanicsApp.h"

InputParameters
NonlinearBiotADApp::validParams()
{
  InputParameters params = MooseApp::validParams();
  params.set<bool>("use_legacy_material_output") = false;
  params.set<bool>("use_legacy_initial_residual_evaluation_behavior") = false;
  return params;
}

registerKnownLabel("NonlinearBiotADApp");
registerKnownLabel("MulticomponentReactiveFlowApp");

NonlinearBiotADApp::NonlinearBiotADApp(const InputParameters & parameters) : MooseApp(parameters)
{
  NonlinearBiotADApp::registerAll(_factory, _action_factory, _syntax);
}

NonlinearBiotADApp::~NonlinearBiotADApp() {}

void
NonlinearBiotADApp::registerAll(Factory & factory,
                                ActionFactory & action_factory,
                                Syntax & syntax)
{
  SolidMechanicsApp::registerAll(factory, action_factory, syntax);
  Registry::registerObjectsTo(factory, {"MulticomponentReactiveFlowApp"});
}

void
NonlinearBiotADApp::registerApps()
{
  registerApp(NonlinearBiotADApp);
}

extern "C" void
NonlinearBiotADApp__registerAll(Factory & factory, ActionFactory & action_factory, Syntax & syntax)
{
  NonlinearBiotADApp::registerAll(factory, action_factory, syntax);
}

extern "C" void
NonlinearBiotADApp__registerApps()
{
  NonlinearBiotADApp::registerApps();
}
