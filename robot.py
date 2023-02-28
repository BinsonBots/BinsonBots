from typing import Tuple
from RPi import GPIO as gpio
import atexit


DEFAULT_SPEED_LIMIT: float = 0.7


PWM_FREQ: int = 100


def clamp(x: float, a: float, b: float) -> float:
    """Clamps a float value, x, between a (lower bound) and b (upper bound).

Parameters:
    x (float) -- the value to clamp
    a (float) -- the lower bound
    b (float) -- the upper bound

Raises:
    ValueError -- thrown if a > b"""

    if a > b:
        raise ValueError()

    elif x < a:
        return a

    elif x > b:
        return b

    else:
        return x


class Robot:

    def __init__(self,
                 speed_limit: float = DEFAULT_SPEED_LIMIT,
                 pin_pwm_left: int = 18,
                 pin_pwm_right: int = 15,
                 pin_direc_left: int = 24,
                 pin_direc_right: int = 23):

        # Set attributes

        self.pins_pwm_lr: Tuple[int, int] = (pin_pwm_left, pin_pwm_right)
        self.pins_direc_lr: Tuple[int, int] = (pin_direc_left, pin_direc_right)

        self.__speed_limit = speed_limit

        # Set GPIO numbering to BCM

        gpio.setmode(gpio.BCM)

        # Set up PWM pins

        self.pwms_lr = []

        for pin_pwm in self.pins_pwm_lr:

            gpio.setup(pin_pwm, gpio.OUT)

            pwm = gpio.PWM(pin_pwm, PWM_FREQ)
            pwm.start(0)

            self.pwms_lr.append(pwm)

        # Set up direction pins

        for pin_direc in self.pins_direc_lr:
            gpio.setup(pin_direc, gpio.OUT)
            gpio.output(pin_direc, 1)

        # Register shutdown to run on termination

        atexit.register(self.__shutdown)

    def wheel_speed(self, left: float, right: float) -> None:
        """Sets the speeds of the robot's wheels.

Parameters:
    left - the speed for the left wheels (can be positive or negative)
    right - the speed for the right wheels (can be positive or negative)
"""

        # Clamp speed by speed limit

        left = clamp(left, -self.__speed_limit, self.__speed_limit)
        right = clamp(right, -self.__speed_limit, self.__speed_limit)

        # Set direction pin outputs

        if left > 0:
            gpio.output(self.pins_direc_lr[0], 0)
        else:
            gpio.output(self.pins_direc_lr[0], 1)

        if right > 0:
            gpio.output(self.pins_direc_lr[1], 0)
        else:
            gpio.output(self.pins_direc_lr[1], 1)

        # Set PWM pin duty cycles (to change speed)

        left_duty_cycle: float = abs(left) * 100
        right_duty_cycle: float = abs(right) * 100

        self.pwms_lr[0].ChangeDutyCycle(left_duty_cycle)
        self.pwms_lr[1].ChangeDutyCycle(right_duty_cycle)

    def stop_wheels(self) -> None:
        """Sets both wheels' speeds to zero"""
        self.wheel_speed(0, 0)

    def __shutdown(self) -> None:

        try:
            self.stop_wheels()
        except Exception as e:
            print(f"Failed to stop wheels:\n{e}")

        print("Robot shut-down")
