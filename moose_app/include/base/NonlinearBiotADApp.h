#pragma once

#include "MooseApp.h"

class NonlinearBiotADApp : public MooseApp
{
public:
  static InputParameters validParams();

  NonlinearBiotADApp(const InputParameters & parameters);
  virtual ~NonlinearBiotADApp();

  static void registerApps();
  static void registerAll(Factory & factory, ActionFactory & action_factory, Syntax & syntax);
};
