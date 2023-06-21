"""root system length over time"""
import sys; sys.path.append("../../unix"); sys.path.append("../../src/"); sys.path.append("./"); sys.path.append("./src/")


import numpy as np
from tqdm import tqdm
import subprocess

# save pwd
import os
pwd = os.getcwd()
os.chdir("../../unix")
# make and save the error output in a string
print("Compiling the source code...")
try :
  output_ = subprocess.check_output(["make", "-j4"], stderr=subprocess.STDOUT)
except subprocess.CalledProcessError as e:
  output_ = e.output
# print the error if there is any
if "error" in output_.decode("utf-8"):
  print("Error in compiling the source code:")
  print(output_.decode("utf-8"))
  sys.exit()
# back to pwd
os.chdir(pwd)


import plantbox as pb
import visualisation.vtk_plot as vp
import visualisation.vis_tools as cpbvis

filename = "./vis_example_plant_maize.xml"
output_folder = "./results/"
output = output_folder+"vis_grow"

# remove all files in ./results/ first
filelist = [ f for f in os.listdir(output_folder) if f.endswith(".vtp") and "vis_grow" in f ]
for f in filelist:
  os.remove(os.path.join(output_folder, f))


# we build a rhizotron by subtracting a box from a larger box
interior = pb.SDF_PlantBox(2.0, 20.0, 24.0)
interior_np = np.array([[], []])
interior = pb.SDF_RotateTranslate(interior, pb.Vector3d(0, 0, 1))
exterior = pb.SDF_PlantBox(10.0, 40.0, 40.0)
rhizotron = pb.SDF_Difference(exterior, interior)


time = 28
leaf_res = 30
# create a plant
plant = pb.MappedPlant()
plant.setGeometry(rhizotron)
plant.readParameters(filename)
vis = pb.PlantVisualiser(plant)
vis.SetVerbose(False)

time = 20
time_resolution = 2
mode = 0 # 0 = time, 1 = end

for p in plant.getOrganRandomParameter(pb.stem):
  p.r = 0.758517633
  p.lb = 4
  # p.delayLat = 4
  p.lmax = (time-7)*p.r
  p.dx = 0.1
for p in plant.getOrganRandomParameter(pb.leaf):
  p.la,  p.lmax = 38.41053981, 38.41053981
  #p.theta = 0.2 # 0.2
  p.theta = 0.01
  p.tropismT = 1 # 6: Anti-gravitropism to gravitropism
  p.areaMax = 54.45388021  # cm2, area reached when length = lmax
  phi = np.array([-90,-80, -45, 0., 45, 90]) / 180. * np.pi    
  l = np.array([38.41053981,1 ,1, 0.3, 1, 38.41053981]) #distance from leaf center
  p.leafGeometryPhi = phi
  p.leafGeometryX = l
  #p.tropismN = 5
  p.tropismS = 0.08
  p.tropismAge = 5 #< age at which tropism switch occures, only used if p.tropismT = 6
  p.createLeafRadialGeometry(phi,l,leaf_res)

# Initialize
plant.initialize()
vis.SetGeometryResolution(8)
vis.SetLeafResolution(leaf_res)
vis.SetConfinedTo(pb.Vector3d(-10, -1.0, -23), pb.Vector3d(10, 1.0, 1.0))

if mode == 0 :
  for i in tqdm(range(time * time_resolution), desc="Sim+Vis", unit="day", unit_scale=True) :
    # Simulate
    plant.simulate(1. / time_resolution, False)
    vis.ComputeGeometryForOrganType(pb.leaf, True)
    data = cpbvis.PolydataFromPlantGeometry(vis)
    cpbvis.WritePolydataToFile(data, output + "_leaf_" + str(i) + ".vtp")
    vis.ComputeGeometryForOrganType(pb.stem, True)
    data = cpbvis.PolydataFromPlantGeometry(vis)
    cpbvis.WritePolydataToFile(data, output + "_stem_" + str(i) + ".vtp")
    vis.ComputeGeometryForOrganType(pb.root, True)
    data = cpbvis.PolydataFromPlantGeometry(vis)
    cpbvis.WritePolydataToFile(data, output + "_root_" + str(i) + ".vtp")
  #endfor
elif mode == 1 :
  plant.simulate(time, False)
  vis.ResetGeometry()
  vis.ComputeGeometry()
  node_ids = vis.GetNodeIds()
  idmax = np.max(node_ids)
  idmin = np.min(node_ids)
  vis.MapPropertyToColors(node_ids, idmin, idmax)
  #vis.ComputeGeometryForOrganType(pb.leaf, False)
  #vis.ComputeGeometryForOrganType(pb.stem, False)
  #vis.ComputeGeometry()
  # Write the geometry to file#
  data = cpbvis.PolydataFromPlantGeometry(vis)
  cpbvis.WritePolydataToFile(data, output + ".vtp")

