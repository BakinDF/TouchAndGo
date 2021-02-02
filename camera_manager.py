import cv2
from threading import Thread
from time import sleep


def renew_all(manager):
    try:
        while manager.running:
            success_r, right = manager.right_cap.read()
            success_l, left = manager.left_cap.read()
            manager.right_frame = right
            manager.left_frame = left
            sleep(0.02)
    finally:
        manager.left_cap.release()
        manager.right_cap.release()


class CameraManager:
    def __init__(self):
        self.left_cap = cv2.VideoCapture(0)
        self.right_cap = cv2.VideoCapture(2)
        # self.left_cap.set(cv2.CAP_PROP_FPS, 30)
        # self.right_cap.set(cv2.CAP_PROP_FPS, 30)
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
        Thread(target=renew_all, args=(self,)).start()

    def stop(self):
        self.running = False

    def get_stereo(self):
        return self.left_frame, self.right_frame

    def get_right(self):
        return self.right_frame

    def get_left(self):
        return self.left_frame
