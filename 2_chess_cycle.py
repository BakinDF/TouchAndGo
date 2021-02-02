import os
import time
from datetime import datetime
from camera_manager import *


# User quit method message 
print("You can press 'Q' to quit this script.")

running = True
# Photo session settings
total_photos = 50  # Number of images to take
countdown = 5  # Interval for count-down timer, seconds
font = cv2.FONT_HERSHEY_SIMPLEX  # Cowntdown timer font

# Buffer for captured image settings
img_width = 640
img_height = 480

write_left = True
write_right = True
print('capturing left, right: ', write_left, ', ', write_right, sep='')

path = './pairs/'
print('capturing to path:', path)

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
        t1 = datetime.now()
        # cntdwn_timer = countdown - int ((t1-t2).total_seconds())
        imgLeft, imgRight = man.get_stereo()
        # If cowntdown is zero - let's record next image
        # if cntdwn_timer == -1:
        print(i)
        if i >= 100:
            print('write')
            counter += 1
            leftName = path + 'left_' + str(counter).zfill(2) + '.png'
            rightName = path + 'right_' + str(counter).zfill(2) + '.png'
            if write_left:
                cv2.imwrite(leftName, imgLeft)
            if write_right:
                cv2.imwrite(rightName, imgRight)
            print(' [' + str(counter) + ' of ' + str(total_photos) + '] ' + leftName, rightName)
            t2 = datetime.now()
            time.sleep(1)
            cntdwn_timer = 0  # To avoid "-1" timer display
            i = 0

        cv2.imshow("left", imgLeft)
        cv2.imshow("right", imgRight)

        # Draw cowntdown counter, seconds
        key = cv2.waitKey(1) & 0xFF

        # Press 'Q' key to quit, or wait till all photos are taken
        if (key == ord("q")) | (counter == total_photos):
            break
        i += 1
    print("Photo sequence finished")
finally:
    man.stop()
    running = False
    sleep(1)
    print('threads stopped')
