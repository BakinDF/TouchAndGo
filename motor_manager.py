import RPi.GPIO as GPIO
from time import sleep
from threading import Thread
from random import random, choice

MOTOR_PIN_1 = 36
MOTOR_PIN_2 = 40
MOTOR_PIN_3 = 22
MOTOR_PIN_4 = 26
PINS = [MOTOR_PIN_1, MOTOR_PIN_2, MOTOR_PIN_3, MOTOR_PIN_4]


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
    IDLE = 0
    LOW = 0.2
    MEDIUM = 0.7
    HIGH = 0.05
    CRITICAL = 0.02

    MAX_VALUE = 1500
    MIN_VALUE = 500

    def __init__(self, *pins):
        GPIO.setmode(GPIO.BOARD)
        self.current_modes = dict()
        for pin in pins:
            self.current_modes[pin] = MotorManager.IDLE
            GPIO.setup(pin, GPIO.OUT)
        self.running = False

    def check_motor_id(self, motor_id):
        if motor_id not in self.current_modes.keys():
            raise ValueError

    def get_mode(self, motor_id):
        self.check_motor_id(motor_id)
        return self.current_modes[motor_id]

    def set_mode(self, motor_id, timeout):
        self.check_motor_id(motor_id)
        self.current_modes[motor_id] = timeout
        # print(f'{motor_id} mode changed to {timeout}')

    def start(self):
        self.running = True
        threads = [Thread(target=operate_motors,
                          args=(pin, self)).start() for pin in self.current_modes.keys()]

    def get_needed_mode(self, value):
        if str(value) == 'nan':
            return MotorManager.IDLE
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
        '''for i in range(30):
            motor_manager.set_mode(choice(PINS), choice([MotorManager.IDLE, MotorManager.LOW,
                                                         MotorManager.MEDIUM, MotorManager.HIGH,
                                                         MotorManager.CRITICAL]))
            sleep(random() * 2)
        raise KeyboardInterrupt'''

        # motor_manager.set_mode(MOTOR_PIN_1, MotorManager.LOW)
        # sleep(3)
        # motor_manager.set_all_idle()
        motor_manager.set_mode(MOTOR_PIN_1, MotorManager.MEDIUM)
        sleep(3)
        motor_manager.set_mode(MOTOR_PIN_2, MotorManager.MEDIUM)
        sleep(3)
        motor_manager.set_mode(MOTOR_PIN_3, MotorManager.HIGH)
        sleep(3)
        motor_manager.set_mode(MOTOR_PIN_4, MotorManager.HIGH)
        sleep(3)
        motor_manager.set_all_idle()

    finally:
        try:
            motor_manager.stop()
        except Exception:
            pass
        GPIO.cleanup()
