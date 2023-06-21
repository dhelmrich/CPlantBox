# open a folder and rename all files in it
# scheme: leaf_n.obj -> leaf_n+10.obj

import os
import sys
import natsort

# check if argument was provided
if len(sys.argv) < 3:
    print("Please provide a folder name and a number")
    exit()

# get folder name and number
folder = sys.argv[1]
number = int(sys.argv[2])

# check if folder exists
if not os.path.isdir(folder):
    print("Folder does not exist")
    exit()

# get all files in folder
files = os.listdir(folder)
# sort files naturally
files = natsort.natsorted(files, reverse=True)
# rename files
for file in files:
    # get file name
    name = file.split(".")[0]
    # get file extension
    ext = file.split(".")[1]
    # get file number
    num = int(name.split("_")[1])
    # rename file
    os.rename(folder + "/" + file, folder + "/" + name.split("_")[0] + "_" + str(num + number) + "." + ext)

print("Done")
