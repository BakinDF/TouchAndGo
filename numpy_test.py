import numpy as np
import cv2

#TODO change w and h
CHECKERBOARD = width, height = (6, 9)
#TODO fix dtype to float32
#TODO delete demension
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 1, 3), np.float32)
objp[:, 0, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
res_1 = []
for i in range(50):
    res_1.append(objp)

objp = np.zeros((height * width, 3), np.float32)
objp[:, :2] = np.mgrid[0:width, 0:height].T.reshape(-1, 2)
res_2 = []
for i in range(50):
    res_2.append(objp)

print(all(res_1[0] == res_2[0]))
#print(res_1[0] == res_2)
#print(res_2[0].shape)
#print(res_2 == res_1)