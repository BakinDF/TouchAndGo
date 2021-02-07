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

import RPi.GPIO as GPIO
from time import sleep
from threading import Thread
from random import random, choice

MOTOR_PIN_1 = 36
MOTOR_PIN_2 = 40
MOTOR_PIN_3 = 22
MOTOR_PIN_4 = 26
PINS = [MOTOR_PIN_1, MOTOR_PIN_2, MOTOR_PIN_3, MOTOR_PIN_4]


# turning on motor for constant time but with custom frequency (timeout)
def operate_motors(motor_id, manager):
    on = True
    while manager.running:
        timeout = manager.current_modes[motor_id]
        if abs(timeout) < 0.001:
            GPIO.output(motor_id, GPIO.LOW)
            sleep(0.5)
            continue
        if on:
            GPIO.output(motor_id, GPIO.LOW)
            on = False
            sleep(timeout)
        else:
            GPIO.output(motor_id, GPIO.HIGH)
            on = True
            sleep(0.01)
    GPIO.output(motor_id, GPIO.LOW)


class MotorManager:
    # vars preset for faster customisation
    IDLE = 0
    LOW = 0.2
    MEDIUM = 0.7
    HIGH = 0.05
    CRITICAL = 0.02

    MAX_VALUE = 1500
    MIN_VALUE = 500

    def __init__(self, *pins):
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        self.current_modes = dict()
        for pin in pins:
            self.current_modes[pin] = MotorManager.IDLE
            GPIO.setup(pin, GPIO.OUT)
        self.running = False

    def check_motor_id(self, motor_id):
        if motor_id not in self.current_modes.keys():
            print('wrong motor id:', motor_id)
            raise ValueError

    def get_mode(self, motor_id):
        self.check_motor_id(motor_id)
        return self.current_modes[motor_id]

    def set_mode(self, motor_id, timeout):
        self.check_motor_id(motor_id)
        self.current_modes[motor_id] = timeout
        # print(f'{motor_id} mode changed to {timeout}')

    def start(self):
        # starting threads for each motor
        self.running = True
        threads = [Thread(target=operate_motors,
                          args=(pin, self)).start() for pin in self.current_modes.keys()]

    def get_needed_mode(self, value):
        # calculating motor mode from value
        if str(value) == 'nan':
            return MotorManager.IDLE
        # ratio is calculated as a percentage of all appropriate (min and max) values
        ratio = (value - MotorManager.MIN_VALUE) / (MotorManager.MAX_VALUE - MotorManager.MIN_VALUE)
        if ratio < 0:
            print('wrong min value', value)
            raise ValueError
        if ratio > 1:
            print('wrong max value', value)
            raise ValueError

        print(ratio, end='   ')
        if ratio <= 0.25:
            return MotorManager.IDLE
        elif ratio <= 0.4:
            return MotorManager.LOW
        elif ratio <= 0.55:
            return MotorManager.MEDIUM
        elif ratio <= 0.7:
            return MotorManager.HIGH
        return MotorManager.CRITICAL

    def set_all_idle(self):
        for i in self.current_modes.keys():
            self.set_mode(i, MotorManager.IDLE)

    def stop(self):
        self.running = False
        sleep(1.5)


if __name__ == '__main__':
    try:
        motor_manager = MotorManager(*PINS)
        motor_manager.start()
        print('manager started')
        # comment down to 141 line and uncomment the rest to customly test motors
        for i in range(30):
            motor_manager.set_mode(choice(PINS), choice([MotorManager.IDLE, MotorManager.LOW,
                                                         MotorManager.MEDIUM, MotorManager.HIGH,
                                                         MotorManager.CRITICAL]))
            sleep(random() * 2)
        raise KeyboardInterrupt

        '''
        motor_manager.set_mode(MOTOR_PIN_1, MotorManager.MEDIUM)
        sleep(3)
        motor_manager.set_all_idle()
        motor_manager.set_mode(MOTOR_PIN_2, MotorManager.MEDIUM)
        sleep(3)
        motor_manager.set_all_idle()
        motor_manager.set_mode(MOTOR_PIN_3, MotorManager.MEDIUM)
        sleep(3)
        motor_manager.set_all_idle()
        motor_manager.set_mode(MOTOR_PIN_4, MotorManager.MEDIUM)
        sleep(3)
        motor_manager.set_all_idle()'''

    finally:
        # it's still stringly recommended to use try-funally syntax to stop motor manager
        try:
            motor_manager.stop()
        finally:
            GPIO.cleanup()
