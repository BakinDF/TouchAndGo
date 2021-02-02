import RPi.GPIO as GPIO
from time import sleep
from threading import Thread

MOTOR_PIN_1 = 40
MOTOR_PIN_2 = 38
MOTOR_PIN_3 = 36
MOTOR_PIN_4 = 32
PINS = [MOTOR_PIN_1, MOTOR_PIN_2, MOTOR_PIN_3, MOTOR_PIN_4]


def operate_motors(motor_id, manager):
    on = True
    while manager.running:
        timeout = manager.current_modes[motor_id]
        if not timeout:
            GPIO.output(motor_id, GPIO.LOW)
            sleep(0.5)
            continue
        if on:
            GPIO.output(motor_id, GPIO.LOW)
            on = False
        else:
            GPIO.output(motor_id, GPIO.HIGH)
            on = True
        sleep(timeout)


class MotorManager:
    IDLE = 0
    LOW = 0.1
    MEDIUM = 0.02
    HIGH = 0.01
    CRITICAL = 0.003

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
        print(f'{motor_id} mode changed to {timeout}')

    def start(self):
        self.running = True
        threads = [Thread(target=operate_motors,
                          args=(pin, self)).start() for pin in self.current_modes.keys()]

    def stop(self):
        self.running = False
        sleep(0.5)


try:
    motor_manager = MotorManager(*PINS[:-2])
    motor_manager.start()
    print('manager started')
    motor_manager.set_mode(MOTOR_PIN_1, MotorManager.MEDIUM)
    motor_manager.set_mode(MOTOR_PIN_2, MotorManager.LOW)
    sleep(10)
    motor_manager.stop()
    print('stopped')
    raise KeyboardInterrupt
except KeyboardInterrupt:
    try:
        motor_manager.stop()
    except Exception:
        pass
    GPIO.cleanup()
