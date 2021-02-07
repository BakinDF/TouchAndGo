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

import os
import time
from datetime import datetime
from camera_manager import *

print("You can press 'Q' to quit this script.")

running = True
# Photo session settings
total_photos = 100  # Number of images to take

img_width = 640
img_height = 480

# setup whether we need to capture both images
write_left = True
write_right = True
print('capturing left, right: ', write_left, ', ', write_right, sep='')

path = './new_pairs/'
print('capturing to path:', path)

# initializing camera manager and waiting 1 secs for threads to start
man = CameraManager()
sleep(1)
# Lets start taking photos! 
counter = 0
t2 = datetime.now()
print("Starting photo sequence")
if not os.path.isdir('./pairs'):
    os.mkdir('./pairs')
try:
    i = 0
    while counter != total_photos:
        imgLeft, imgRight = man.get_stereo()
        # printing num of seconds
        print(i)
        if i >= 75:
            counter += 1
            leftName = path + 'left_' + str(counter).zfill(2) + '.png'
            rightName = path + 'right_' + str(counter).zfill(2) + '.png'
            if write_left:
                cv2.imwrite(leftName, imgLeft)
            if write_right:
                cv2.imwrite(rightName, imgRight)
            print(' [' + str(counter) + ' of ' + str(total_photos) + '] ' + leftName, rightName)
            i = 0
        # constantly showing last received images
        cv2.imshow("left", imgLeft)
        cv2.imshow("right", imgRight)

        # Draw cowntdown counter, seconds
        key = cv2.waitKey(1) & 0xFF

        # Press 'Q' key to quit, or wait till all photos are taken
        if key == ord("q") or counter == total_photos:
            break
        i += 1
    print("Photo sequence finished")
finally:
    # it's strongly recommended to use try-finally syntax to stop camera threads correctly
    man.stop()
    running = False
    sleep(1)
    print('threads stopped')
