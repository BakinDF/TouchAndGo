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
from motor_manager import *

print("You can press 'Q' to quit this script!")
time.sleep(2)

# Visualization settings
showDisparity = True
showUndistortedImages = False
showColorizedDistanceLine = True
stripImage = True

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

img_width = 640
img_height = 480
print("Image resolution: " + str(img_width) + " x " + str(img_height))

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

# initializing camera manager
man = CameraManager()
# initializing motor manager
motor_man = MotorManager(*PINS)
motor_man.start()

# Initialize interface windows
'''cv2.namedWindow("Image")
cv2.moveWindow("Image", 50, 100)
cv2.namedWindow("left")
cv2.moveWindow("left", 450, 100)
cv2.namedWindow("right")
cv2.moveWindow("right", 850, 100)'''

disparity = np.zeros((img_width, img_height), np.uint8)
sbm = cv2.StereoBM_create(numDisparities=0, blockSize=21)


def stereo_depth_map(rectified_pair):
    dmLeft = rectified_pair[0]
    dmRight = rectified_pair[1]
    disparity = sbm.compute(dmLeft, dmRight)
    if (showDisparity):
        disparity_grayscale = (disparity - autotune_min) * (65535.0 / (autotune_max - autotune_min))
        disparity_fixtype = cv2.convertScaleAbs(disparity_grayscale, alpha=(255.0 / 65535.0))
        disparity_color = cv2.applyColorMap(disparity_fixtype, cv2.COLORMAP_JET)
        cv2.imshow("Image", disparity_color)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            quit()
    return disparity


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

        # Taking a strip from our image for saving CPU (or using lidar-like mode)
        if stripImage:
            imgRcut = imgR[100:-100, :]
            imgLcut = imgL[100:-100, :]
        else:
            imgRcut = imgR
            imgLcut = imgL
        rectified_pair = (imgLcut, imgRcut)

        # Disparity map calculation
        native_disparity = stereo_depth_map(rectified_pair)
        maximized_line = native_disparity
        # calculation mean distance in each column excluding values below zero
        maxInColumns = []
        rotated_lines = np.rot90(maximized_line, k=-1)
        for i in range(len(rotated_lines)):
            arr = rotated_lines[i]
            maxInColumns.append(np.mean(arr[arr > 0]))
        # cutting off constant "nan" values because of preset disparity num (in DM calibration)
        # change slice indexes manualy for your calibration settings
        maxInColumns = maxInColumns[110:-20]

        quat_length = len(maxInColumns) // 4
        # calculating max value in each quater (num of motors==4) and setting motors' modes
        motor_man.set_mode(MOTOR_PIN_1, motor_man.get_needed_mode(np.amax(maxInColumns[:quat_length])))
        motor_man.set_mode(MOTOR_PIN_2, motor_man.get_needed_mode(np.amax(maxInColumns[quat_length:quat_length * 2])))
        motor_man.set_mode(MOTOR_PIN_3,
                           motor_man.get_needed_mode(np.amax(maxInColumns[quat_length * 2:quat_length * 3])))
        motor_man.set_mode(MOTOR_PIN_4, motor_man.get_needed_mode(np.amax(maxInColumns[quat_length * 3:])))
        print()

        if showColorizedDistanceLine or showUndistortedImages:
            # "Jumping colors" protection for depth map visualization
            if autotune_max < np.amax(maximized_line):
                autotune_max = np.amax(maximized_line)
            if autotune_min > np.amin(maximized_line):
                autotune_min = np.amin(maximized_line)
            # Colorizing final line
            res = [maxInColumns] * 40
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
    # it's strongly recommended to use
    # try-finally syntax to stop cameraand motor threads correctly
    man.stop()
    motor_man.set_all_idle()
    motor_man.stop()
    sleep(2)
