"""root system length over time"""
import sys; sys.path.append("../../unix"); sys.path.append("../../src/"); sys.path.append("./"); sys.path.append("./src/")


import numpy as np
from tqdm import tqdm
import subprocess
import time

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
import vtk
from vtk.util import numpy_support as vn

filename = "./vis_example_plant_maize.xml"
output_folder = "./tresults/"

# if output_folder does not exist, create it
if not os.path.exists(output_folder):
  os.makedirs(output_folder)

output = output_folder+"vis_grow"

# remove all files in ./results/ first
autoremove = True
if autoremove :
  filelist = [ f for f in os.listdir(output_folder) if f.endswith(".vtp") and "vis_grow" in f ]
  for f in filelist:
    os.remove(os.path.join(output_folder, f))


# we build a rhizotron by subtracting a box from a larger box
interior = pb.SDF_PlantBox(2.0, 20.0, 24.0)
interior_np = np.array([[], []])
interior = pb.SDF_RotateTranslate(interior, pb.Vector3d(0, 0, 1))
exterior = pb.SDF_PlantBox(10.0, 40.0, 40.0)
rhizotron = pb.SDF_Difference(exterior, interior)
rhizotron = pb.SDF_RotateTranslate(rhizotron, 30, 0, pb.Vector3d(0, 0, 0))

leaf_res = 40
num_variations = 4
# create a plant
plant = pb.MappedPlant()
#plant.setGeometry(rhizotron)
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

def organvis(vis,data) :
  organs = vis.IdentifyOrgans()
  idmax = np.max(organs)
  idmin = np.min(organs)
  organs = vn.numpy_to_vtk(organs, deep=True, array_type=vtk.VTK_INT)
  organs.SetName("organ")
  data.GetPointData().AddArray(organs)

def SendOrWrite(data, i, organ:str) :
  if net_mode == 1 :
    dc.SendGeometry(data.GetPoints(), data.GetPolys(), organ, data.GetPointData().GetArray("normals"), data.GetPointData().GetTextureCoordinates())
  else :
    cpbvis.WritePolydataToFile(data, output + "_" + organ + "_" + str(i) + ".vtp")

if mode == 0 :
  setupparams(plant)
  plant.initialize()
  for i in tqdm(range(stime * time_resolution)) :
    # Simulate
    plant.simulate(1. / time_resolution, False)
    vis = pb.PlantVisualiser(plant)
    vis.SetVerbose(False)
    vis.SetGeometryResolution(8)
    vis.SetLeafResolution(leaf_res)
    vis.SetAddVerticalLeafOffset(True)
    vis.SetRandomVerticalLeafOffset(False)
    vis.SetOffsetFrequency(4.0)
    vis.SetVerticalLeafOffset(0.1)
    vis.SetLeafWidthScaleFactor(0.4)
    vis.ResetGeometry()
    #vis.ComputeGeometry()
    #organs = vis.IdentifyOrgans()
    #idmax = np.max(organs)
    #idmin = np.min(organs)
    #data = cpbvis.PolydataFromPlantGeometry(vis)
    #cpbvis.WritePolydataToFile(data, output + "_1_" + str(i) + ".vtp")
    vis.ComputeGeometryForOrganType(pb.leaf, True)
    data = cpbvis.PolydataFromPlantGeometry(vis)
    version = "_0_"
    cpbvis.WritePolydataToFile(data, output + "_leaf_" + version + str(i) + ".vtp")
    vis.ComputeGeometryForOrganType(pb.stem, True)
    data = cpbvis.PolydataFromPlantGeometry(vis)
    cpbvis.WritePolydataToFile(data, output + "_stem_" + version + str(i) + ".vtp")
    vis.ComputeGeometryForOrganType(pb.root, True)
    data = cpbvis.PolydataFromPlantGeometry(vis)
    cpbvis.WritePolydataToFile(data, output + "_root_" + version + str(i) + ".vtp")
  #endfor
elif mode == 1 :
  setupparams(plant)
  plant.initialize()
  plant.simulate(stime, False)
  vis.ResetGeometry()
  vis.ComputeGeometry()
  organs = vis.IdentifyOrgans()
  idmax = np.max(organs)
  idmin = np.min(organs)
  #vis.MapPropertyToColors(organs, idmin, idmax)
  #vis.ComputeGeometryForOrganType(pb.leaf, False)
  #vis.ComputeGeometryForOrganType(pb.stem, False)
  #vis.ComputeGeometry()
  # Write the geometry to file#
  data = cpbvis.PolydataFromPlantGeometry(vis)
  organs = vn.numpy_to_vtk(organs, deep=True, array_type=vtk.VTK_INT)
  organs.SetName("organ")
  data.GetPointData().AddArray(organs)
  cpbvis.WritePolydataToFile(data, output + ".vtp")
  print("Wrote " + output + ".vtp")
elif mode == 2 :
  variations = [[20,0,0],[-20,0,0], [0,20,0], [0,-20,0]]
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
    data = cpbvis.PolydataFromPlantGeometry(vis)
    points = data.GetPoints()
    for j in range(points.GetNumberOfPoints()) :
      points.SetPoint(j, points.GetPoint(j) + np.array(variations[i]))
    unix_time = time.time()
    SendOrWrite(data, i, "leaf")
    vis.ComputeGeometryForOrganType(pb.stem, True)
    data = cpbvis.PolydataFromPlantGeometry(vis)
    points = data.GetPoints()
    for j in range(points.GetNumberOfPoints()) :
      points.SetPoint(j, points.GetPoint(j) + np.array(variations[i]))
    SendOrWrite(data, i, "stem")
    vis.ComputeGeometryForOrganType(pb.root, True)
    data = cpbvis.PolydataFromPlantGeometry(vis)
    points = data.GetPoints()
    for j in range(points.GetNumberOfPoints()) :
      points.SetPoint(j, points.GetPoint(j) + np.array(variations[i]))
    SendOrWrite(data, i, "root")
    print(output + "_" + str(i) + ".vtp")
#end if


