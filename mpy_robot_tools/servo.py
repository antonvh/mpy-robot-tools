from machine import Pin, PWM
from .helpers import clamp_int, scale

class Servo():
    zero = 1500
    cw90 = 2000
    ccw90 = 1000
    def __init__(self, pin) -> None:
        self.servo = PWM(Pin(pin),freq=50)

    def pwm(self, pwm):
        # Timing in microseconds
        # https://en.wikipedia.org/wiki/Servo_control#/media/File:Servomotor_Timing_Diagram.svg
        # 1500 is neutral, 2000 is far right, 1000 is far left.
        ONE_US = 1024/20000
        self.servo.duty(round(pwm*ONE_US))

    def angle(self, angle):
        angle = clamp_int(angle,-90,90)
        pwm = scale(angle, (-90,90), (self.ccw90, self.cw90))
        self.pwm(pwm)
