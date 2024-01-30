"""root system length over time"""
import sys; sys.path.append("../../unix"); sys.path.append("../../src/"); sys.path.append("./"); sys.path.append("./src/")

import os
import numpy as np
from tqdm import tqdm
import subprocess
import time


import plantbox as pb
import visualisation.vtk_plot as vp
import visualisation.vis_tools as cpbvis
import vtk
from vtk.util import numpy_support as vn

filename = "./vis_example_plant_maize.xml"
output_folder = "./tresults/"

# if output_folder does not exist, create it
if not os.path.exists(output_folder):
  os.makedirs(output_folder)

output = output_folder+"vis_grow"


leaf_res = 40
num_variations = 500
# create a plant
plant = pb.MappedPlant()
plant.readParameters(filename)
vis = pb.PlantVisualiser(plant)

stime = 25
time_resolution = 2
mode = 2 # 0 = time, 1 = end, 2 = variation
net_mode = 0 # 0 = no net, 1 = net
vis.SetVerbose(mode == 1)

if net_mode == 1 :
  cpbvis.CheckForSynavis()
  dc = synavis.DataConnector()

def setupparams(plant) :
  for p in plant.getOrganRandomParameter(pb.stem):
    if p == None :
      continue
    p.r = 0.758517633
    p.lb = 4
    #p.delayLat = 4
    p.lmax = (stime-5)*p.r
    p.dx = 0.1
  for p in plant.getOrganRandomParameter(pb.leaf):
    if p == None :
      continue
    p.la,  p.lmax = 38.41053981, 38.41053981
    p.la = 20
    p.lmax = 20
    #p.theta = 0.2 # 0.2
    p.theta = 0.001
    #p.thetas = 0.1
    p.RotBeta = 0.8
    p.dx = 0.2
    p.tropismT = 1 # 6: Anti-gravitropism to gravitropism
    #p.areaMax = 54.45388021  # cm2, area reached when length = lmax
    p.areaMax = 28  # cm2, area reached when length = lmax
    phi = np.array([-90,-80, -45, 0., 45, 90]) / 180. * np.pi    
    l = np.array([38.41053981,1 ,1, 0.3, 1, 38.41053981]) #distance from leaf center
    l /= np.linalg.norm(l)
    l *= p.lmax
    p.leafGeometryPhi = phi
    p.leafGeometryX = l
    #p.tropismN = 5
    p.tropismS = 0.08
    p.tropismAge = 5 #< age at which tropism switch occures, only used if p.tropismT = 6
    p.createLeafRadialGeometry(phi,l,leaf_res)

# Initialize
#plant.initialize()
#plant.simulate(10,False)
vis.SetGeometryResolution(8)
vis.SetLeafResolution(leaf_res)
vis.SetAddVerticalLeafOffset(True)
#vis.SetConfinedTo(pb.Vector3d(-10, -1.0, -23), pb.Vector3d(10, 1.0, 1.0))

leaf_areas = []

for i in range(num_variations) :
  plant = pb.MappedPlant()
  #plant.setGeometry(rhizotron)
  plant.readParameters(filename)
  setupparams(plant)
  vis = pb.PlantVisualiser(plant)
  plant.initialize()
  vis.SetGeometryResolution(8)
  vis.SetLeafResolution(leaf_res)
  vis.SetAddVerticalLeafOffset(False)
  vis.SetRandomVerticalLeafOffset(False)
  vis.SetOffsetFrequency(4.0)
  vis.SetVerticalLeafOffset(0.1)
  vis.SetLeafWidthScaleFactor(0.4)
  #vis.SetConfinedTo(pb.Vector3d(-10, -1.0, -23), pb.Vector3d(10, 1.0, 1.0))
  plant.simulate(stime, False)
  vis.ResetGeometry()
  vis.SetVerbose(False)
  vis.ComputeGeometryForOrganType(pb.leaf, True)
  cell_data = np.array(vis.GetGeometryIndices()).astype(np.int64)
  cell_data = np.reshape(cell_data, (cell_data.shape[0]//3, 3))
  geom = np.array(vis.GetGeometry()).astype(np.float64)
  geom = np.reshape(geom, (geom.shape[0]//3, 3))
  # compute leaf areas
  triangle_areas = []
  for j in range(cell_data.shape[0]) :
    # get vertices of triangle
    v1 = geom[cell_data[j,0],:]
    v2 = geom[cell_data[j,1],:]
    v3 = geom[cell_data[j,2],:]
    # compute area
    a = np.linalg.norm(np.cross(v2-v1, v3-v1))/2
    triangle_areas.append(a)
  # end for
  leaf_areas.append(np.sum(triangle_areas))
#end for

leaf_areas = np.array(leaf_areas)
print(leaf_areas)
# write to csv
with open(output_folder+"leaf_areas.csv", "w") as f :
  for i in range(leaf_areas.shape[0]) :
    # if german locale is used, replace . with ,
    entry = str(leaf_areas[i])
    entry = entry.replace(".", ",")
    f.write(entry+"\n")
  # end for

# plot as histogram
import matplotlib.pyplot as plt
plt.hist(leaf_areas, bins=20)
plt.savefig(output_folder+"leaf_areas.pdf", bbox_inches='tight', dpi=300)
plt.close()



