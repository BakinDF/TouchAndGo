import numpy as np
import os
from datetime import datetime
from camera_manager import *

man = CameraManager()

print("You can press 'Q' to quit this script.")
# File for captured image
filename = './scenes/'

# Final image capture settings
scale_ratio = 0.5

img_width = 640
img_height = 480

counter = 0
avgtime = 0
# Capture frames from the camera

try:
    while True:
        counter += 1
        t0 = datetime.now()
        # cv2.imshow("pair", frame)
        # key = cv2.waitKey()
        # if the `q` key was pressed, break from the loop and save last image
        # if key == ord("q"):
        '''print("Average time between frames: " + str(avgtime))
        print("Frames: " + str(counter) + " Time: " + str(timediff.total_seconds()) + " Average FPS: " + str(
            counter / timediff.total_seconds()))'''
        if (os.path.isdir("./scenes") == False):
            os.makedirs("./scenes")
        frame_left, frame_right = man.get_stereo()
        # cv2.imwrite(filename + 'image_right.png', frame_right)
        # cv2.imwrite(filename + 'image_left.png', frame_left)
        double_img = np.concatenate((frame_left, frame_right), axis=1)
        cv2.imshow('stereoimage', double_img)
        # cv2.imwrite(filename + 'double_image.png', double_img)
        t1 = datetime.now()
        # print('time to write', t1 - t0)
        # print('finished')
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
finally:
    man.stop()
    print('stopped')
