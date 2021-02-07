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


import numpy as np
import os
from datetime import datetime
from camera_manager import *

# initialising camera manager
man = CameraManager()

print("You can press 'Q' to quit this script.")
# Path for captured image
filename = './scenes/'

img_width = 640
img_height = 480

counter = 0
# Capture frames from the camera to path
folder_to_capture = './test_pairs/'
i = 1
try:
    while True:
        counter += 1
        if (os.path.isdir("./scenes") == False):
            os.makedirs("./scenes")
        frame_left, frame_right = man.get_stereo()
        # creating and showing stereopair
        double_img = np.concatenate((frame_left, frame_right), axis=1)
        cv2.imshow('stereoimage', double_img)

        # cv2.imwrite(filename + 'double_image.png', double_img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        # if 'c' pressed, capturing photos
        if key == ord('c'):
            if not os.path.isdir(folder_to_capture):
                os.mkdir(folder_to_capture)
            cv2.imwrite(folder_to_capture + str(i).rjust(2, '0') + 'L.png', frame_left)
            cv2.imwrite(folder_to_capture + str(i).rjust(2, '0') + 'R.png', frame_right)
            i += 1
finally:
    # it's strongly recommended to use try-finally syntax to stop camera threads correctly
    man.stop()
    print('stopped')
