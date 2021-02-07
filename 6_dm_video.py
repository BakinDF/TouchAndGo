# Copyright (C) 2021 Denis Bakin a.k.a. MrEmgin
#
# This file is a part of TouchAndGo project for blind people.
# It was completed as an individual project in the 10th grade
#
# TouchAndGo is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# TouchAndGo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TouchAndGo tutorial.
# If not, see <http://www.gnu.org/licenses/>.
#
#          <><><> SPECIAL THANKS: <><><>
#
# Thanks for StereoPi tutorial https://github.com/realizator/stereopi-fisheye-robot
# for base concepts of stereovision in OpenCV

import time
import cv2
import numpy as np
import json
from datetime import datetime
from camera_manager import *

print("You can press Q to quit this script!")
time.sleep(2)

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

useStripe = False
dm_colors_autotune = True
disp_max = -100000
disp_min = 10000

# Camera settimgs
cam_width = 1280
cam_height = 480

# Final image capture settings
scale_ratio = 0.5

# Camera resolution height must be dividable by 16, and width by 32

# Buffer for captured image settings
img_width = 640
img_height = 480
print("Scaled image resolution: " + str(img_width) + " x " + str(img_height))

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
    global disp_max
    global disp_min
    dmLeft = rectified_pair[0].astype('uint8')
    dmRight = rectified_pair[1].astype('uint8')
    disparity = sbm.compute(dmLeft, dmRight)
    local_max = disparity.max()
    local_min = disparity.min()
    if (dm_colors_autotune):
        disp_max = max(local_max, disp_max)
        disp_min = min(local_min, disp_min)
        local_max = disp_max
        local_min = disp_min
        print(disp_max, disp_min)
    disparity_grayscale = (disparity - local_min) * (65535.0 / (local_max - local_min))
    # disparity_grayscale = (disparity+208)*(65535.0/1000.0) # test for jumping colors prevention
    disparity_fixtype = cv2.convertScaleAbs(disparity_grayscale, alpha=(255.0 / 65535.0))
    disparity_color = cv2.applyColorMap(disparity_fixtype, cv2.COLORMAP_JET)
    cv2.imshow("Image", disparity_color)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        quit()
    return disparity_color


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
    print('Parameters loaded from file ' + fName)


load_map_settings("3dmap_set.txt")
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

try:
    while 1:
        t1 = datetime.now()
        imgLeft, imgRight = man.get_stereo()
        imgLeft = cv2.cvtColor(imgLeft, cv2.COLOR_BGR2GRAY)
        imgRight = cv2.cvtColor(imgRight, cv2.COLOR_BGR2GRAY)
        imgL = cv2.remap(imgLeft, leftMapX, leftMapY, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        imgR = cv2.remap(imgRight, rightMapX, rightMapY, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

        if (useStripe):
            imgRcut = imgR[:img_height // 2, 100:img_width - 100]
            imgLcut = imgL[:img_height // 2, 100:img_width - 100]
        else:
            imgRcut = imgR
            imgLcut = imgL
        rectified_pair = (imgLcut, imgRcut)
        disparity = stereo_depth_map(rectified_pair)
        # show the frame
        cv2.imshow("left", imgLcut)
        cv2.imshow("right", imgRcut)
        key = cv2.waitKey(1) & 0xFF

        # Press 'Q' key to quit, or wait till all photos are taken
        if key == ord("q"):
            break

        t2 = datetime.now()
        print("DM build time: " + str(t2 - t1))

finally:
    # it's strongly recommended to use try-finally syntax to stop camera threads correctly
    man.stop()
    sleep(2)
