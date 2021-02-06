# Copyright (C) 2019 Eugene a.k.a. Realizator, stereopi.com, virt2real team
#
# This file is part of StereoPi tutorial scripts.
#
# StereoPi tutorial is free software: you can redistribute it 
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
#
# StereoPi tutorial is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with StereoPi tutorial.  
# If not, see <http://www.gnu.org/licenses/>.
#
#          <><><> SPECIAL THANKS: <><><>
#
# Thanks to Adrian and http://pyimagesearch.com, as a lot of
# code in this tutorial was taken from his lessons.
#  
# Thanks to RPi-tankbot project: https://github.com/Kheiden/RPi-tankbot
#
# Thanks to rakali project: https://github.com/sthysel/rakali


import time
import cv2
import numpy as np
import json
from datetime import datetime
from camera_manager import *

print("You can press 'Q' to quit this script!")
time.sleep(5)

# Visualization settings
showDisparity = True
showUndistortedImages = True
showColorizedDistanceLine = True

# Depth map default preset
SWS = 5
PFS = 5
PFC = 29
MDS = -30
NOD = 160
TTH = 100
UR = 10
SR = 14
SPWS = 100

# Camera settimgs
cam_width = 1280
cam_height = 480

# Final image capture settings
scale_ratio = 0.5

# Buffer for captured image settings
img_width = 640
img_height = 480
print("Scaled image resolution: " + str(img_width) + " x " + str(img_height))

# Depth Map colors autotune
autotune_min = 10000000
autotune_max = -10000000

# 3D points settings
focal_length = 165.0  # taken from K matrix
tx = 65  # taken from K matrix after calibration
q = np.array([
    [1, 0, 0, -img_width / 2],
    [0, 1, 0, -img_height / 2],
    [0, 0, 0, focal_length],
    [0, 0, -1 / tx, 0]
])

man = CameraManager()

# Initialize interface windows
cv2.namedWindow("Image")
cv2.moveWindow("Image", 50, 100)
cv2.namedWindow("left")
cv2.moveWindow("left", 450, 100)
cv2.namedWindow("right")
cv2.moveWindow("right", 850, 100)

disparity = np.zeros((img_width, img_height), np.uint8)
sbm = cv2.StereoBM_create(numDisparities=0, blockSize=21)


def stereo_depth_map(rectified_pair):
    dmLeft = rectified_pair[0]
    dmRight = rectified_pair[1]
    disparity = sbm.compute(dmLeft, dmRight)
    local_max = disparity.max()
    local_min = disparity.min()
    # print(local_max, local_min)
    disparity_grayscale = (disparity - autotune_min) * (65535.0 / (autotune_max - autotune_min))
    disparity_fixtype = cv2.convertScaleAbs(disparity_grayscale, alpha=(255.0 / 65535.0))
    disparity_color = cv2.applyColorMap(disparity_fixtype, cv2.COLORMAP_JET)
    if (showDisparity):
        cv2.imshow("Image", disparity_color)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            quit()
    return disparity_color, disparity_fixtype, disparity


def load_map_settings(fName):
    global SWS, PFS, PFC, MDS, NOD, TTH, UR, SR, SPWS, loading_settings
    print('Loading parameters from file...')
    f = open(fName, 'r')
    data = json.load(f)
    SWS = data['SADWindowSize']
    PFS = data['preFilterSize']
    PFC = data['preFilterCap']
    MDS = data['minDisparity']
    NOD = data['numberOfDisparities']
    TTH = data['textureThreshold']
    UR = data['uniquenessRatio']
    SR = data['speckleRange']
    SPWS = data['speckleWindowSize']
    # sbm.setSADWindowSize(SWS)
    sbm.setPreFilterType(1)
    sbm.setPreFilterSize(PFS)
    sbm.setPreFilterCap(PFC)
    sbm.setMinDisparity(MDS)
    sbm.setNumDisparities(NOD)
    sbm.setTextureThreshold(TTH)
    sbm.setUniquenessRatio(UR)
    sbm.setSpeckleRange(SR)
    sbm.setSpeckleWindowSize(SPWS)
    f.close()
    print('Depth map settings has been loaded from the file ' + fName)


# Loading depth map settings
load_map_settings("3dmap_set.txt")

# Loading stereoscopic calibration data
try:
    npzfile = np.load('./calibration_data/{}p/stereo_camera_calibration.npz'.format(img_height))
except:
    print("Camera calibration data not found in cache, file ",
          './calibration_data/{}p/stereo_camera_calibration.npz'.format(img_height))
    exit(0)

imageSize = tuple(npzfile['imageSize'])
leftMapX = npzfile['leftMapX']
leftMapY = npzfile['leftMapY']
rightMapX = npzfile['rightMapX']
rightMapY = npzfile['rightMapY']
QQ = npzfile['dispartityToDepthMap']

map_width = 640
map_height = 480

min_y = 10000
max_y = -10000
min_x = 10000
max_x = -10000
# Capture the frames from the camera
try:
    while 1:
        t1 = datetime.now()
        imgLeft, imgRight = man.get_stereo()
        imgLeft = cv2.cvtColor(imgLeft, cv2.COLOR_BGR2GRAY)
        imgRight = cv2.cvtColor(imgRight, cv2.COLOR_BGR2GRAY)
        imgL = cv2.remap(imgLeft, leftMapX, leftMapY, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        imgR = cv2.remap(imgRight, rightMapX, rightMapY, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

        # Taking a strip from our image for lidar-like mode (and saving CPU)
        # imgRcut = imgR[100:600, 60:550]
        # imgLcut = imgL[100:600, 60:550]
        imgRcut = imgR
        imgLcut = imgL
        rectified_pair = (imgLcut, imgRcut)

        # Disparity map calculation
        disparity, disparity_bw, native_disparity = stereo_depth_map(rectified_pair)
        print('max:', np.amax(native_disparity))
        print('min:', np.amin(native_disparity))
        maximized_line = native_disparity

        maxInColumns = []
        rotated_lines = np.rot90(maximized_line)
        for i in range(len(maximized_line)):
            arr = rotated_lines[i]
            maxInColumns.append(np.mean(arr[arr != -288]))
        maxInColumns = maxInColumns.reverse()
        res = []
        for i in range(80):
            res.append(maxInColumns)
        # np.mean(maximized_line, 0) * 2

        # "Jumping colors" protection for depth map visualization
        if autotune_max < np.amax(maximized_line):
            autotune_max = np.amax(maximized_line)
        if autotune_min > np.amin(maximized_line):
            autotune_min = np.amin(maximized_line)

        # Choose "closest" points in each column
        # maximized_line = maxInColumns

        # Colorizing final line
        max_line_tune = (res - autotune_min) * (65535.0 / (autotune_max - autotune_min))
        max_line_gray = cv2.convertScaleAbs(max_line_tune, alpha=(255.0 / 65535.0))

        # Change map_zoom to adjust visible range!
        max_line_color = cv2.applyColorMap(max_line_gray, cv2.COLORMAP_JET)

        # show the frame
        # print ("Autotune: min =", autotune_min, " max =", autotune_max)
        if (showUndistortedImages):
            cv2.imshow("left", imgLcut)
            cv2.imshow("right", imgRcut)
        if (showColorizedDistanceLine):
            cv2.imshow("Max distance line", max_line_color)
        t2 = datetime.now()
        print("DM build time: " + str(t2 - t1))
finally:
    man.stop()
    sleep(2)
