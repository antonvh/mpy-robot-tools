try:
    from machine import Pin, PWM
except:
    # Import failed. Not on micropython
    pass

from .helpers import clamp_int, scale

class Servo():
    """ Defines a hobby servo
    """
    zero = 1500
    cw90 = 2000
    ccw90 = 1000
    def __init__(self, pin) -> None:
        """Instantiate servo on pin

        :param pin: pin number
        :type pin: int
        """
        self.servo = PWM(Pin(pin),freq=50)

    def pwm(self, pwm):
        """Timing in microseconds
        1500 is neutral, 2000 is far right, 1000 is far left.
        https://en.wikipedia.org/wiki/Servo_control#/media/File:Servomotor_Timing_Diagram.svg
        

        :param pwm: microseconds pwm. 
        :type pwm: int
        """
        ONE_US = 1024/20000
        self.servo.duty(round(pwm*ONE_US))

    def angle(self, angle):
        angle = clamp_int(angle,-90,90)
        pwm = scale(angle, (-90,90), (self.ccw90, self.cw90))
        self.pwm(pwm)
