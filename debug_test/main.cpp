
#include <string>
#include <iostream>

#include "MappedOrganism.h"
#include "PlantVisualiser.h"

const double PI = 3.14159265358979323846;

int main()
{
  auto plant = std::make_shared<CPlantBox::MappedPlant>();
  const int leaf_resolution = 20;
  const int time = 8;
  plant->readParameters("F:/Work/Synavis/build_win/native_modules/photosynthesis/Release/param.xml");
  

  for(auto p : plant->getOrganRandomParameter(CPlantBox::Organism::OrganTypes::ot_leaf))
  {
    auto leaf = std::dynamic_pointer_cast<CPlantBox::LeafRandomParameter>(p);
    leaf->leafGeometryPhi = {-90.0, -80.0, -45.0, 0.0, 45.0, 90.0};
    // transform leafGeometryPhi to radians
    std::transform(leaf->leafGeometryPhi.begin(), leaf->leafGeometryPhi.end(), leaf->leafGeometryPhi.begin(), [](auto val) { return val * M_PI / 180.0; });
    leaf->leafGeometryX = {38.41053981,1.0 ,1.0, 0.3, 1.0, 38.41053981};
    leaf->createLeafRadialGeometry(leaf->leafGeometryPhi, leaf->leafGeometryX, 20);
  }
  plant->initialize();
  plant->simulate(time, false);
  auto vis = std::make_shared<CPlantBox::PlantVisualiser>(plant);
  std::cout << "Computing Geometry" << std::endl;
  vis->ComputeGeometryForOrganType(CPlantBox::Organism::ot_stem);
  vis->ComputeGeometryForOrganType(CPlantBox::Organism::ot_leaf);
  auto points = vis->GetGeometry();

  std::cout << "Generated points are "  << points.size() << std::endl;
}
