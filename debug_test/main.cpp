
#include <string>
#include <iostream>

#include "MappedOrganism.h"
#include "PlantVisualiser.h"

const double PI = 3.14159265358979323846;

int main()
{

  auto plant = std::make_shared<CPlantBox::MappedPlant>();
  const int leaf_resolution = 20;
  const int time = 20;
  plant->readParameters("C:/Work/CPlantBox/tutorial/examples/vis_example_plant_maize.xml");

  plant->initialize();
  plant->simulate(time, true);
  auto vis = std::make_shared<CPlantBox::PlantVisualiser>(plant);
  std::cout << "Computing Geometry" << std::endl;
  vis->ComputeGeometryForOrganType(CPlantBox::Organism::ot_leaf);
  auto points = vis->GetGeometry();

  std::cout << "Generated points are "  << points.size() << std::endl;
}
