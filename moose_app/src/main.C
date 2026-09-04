#include "MooseMain.h"
#include "NonlinearBiotADApp.h"

int
main(int argc, char * argv[])
{
  return Moose::main<NonlinearBiotADApp>(argc, argv);
}
