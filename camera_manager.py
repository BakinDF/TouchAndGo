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


import cv2
from threading import Thread
from time import sleep


# func for updating left image in thread
def renew_left(manager):
    try:
        while manager.running:
            success_l, left = manager.left_cap.read()
            manager.left_frame = left
    finally:
        manager.left_cap.release()


# func for updating right image in thread
def renew_right(manager):
    try:
        while manager.running:
            success_r, right = manager.right_cap.read()
            manager.right_frame = right
    finally:
        manager.right_cap.release()


class CameraManager:
    def __init__(self):
        self.left_cap = cv2.VideoCapture(2)
        self.right_cap = cv2.VideoCapture(0)
        self.left_cap.set(cv2.CAP_PROP_FPS, 10)
        self.right_cap.set(cv2.CAP_PROP_FPS, 10)
        try:
            assert self.left_cap.isOpened() and self.right_cap.isOpened()
        except AssertionError:
            self.left_cap.release()
            self.right_cap.release()
        self.left_frame = None
        self.right_frame = None

        self.running = False
        self.start()

    def start(self):
        self.running = True
        self.start_threads()
        sleep(1.)

    def start_threads(self):
        # starting 2 threads with funcs above and self argument
        Thread(target=renew_left, args=(self,)).start()
        Thread(target=renew_right, args=(self,)).start()

    def stop(self):
        self.running = False

    def get_stereo(self):
        return self.left_frame, self.right_frame

    def get_right(self):
        return self.right_frame

    def get_left(self):
        return self.left_frame
