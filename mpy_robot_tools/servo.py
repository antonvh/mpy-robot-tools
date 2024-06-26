try:
    from machine import Pin, PWM
except:
    # Import failed. Not on micropython
    pass

def scale(val, src, dst):
    """
    Returns the given value scaled from the scale of src to the scale of dst.

    :param val: Value to scale. Ex: 75
    :type val: int or float
    :param src: Original range. Ex: (0.0, 99.0)
    :type src: tuple
    :param dst: Target range. Ex: (-1.0, +1.0)
    :type dst: tuple
    :return: Scaled value. Ex: 0.5
    """
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

class Servo:
    """Controls a hobby servo with 2000 microsecond pwm

        :param pin: Servo pin number
        :type pin: int
    """
    zero = 1500
    cw90 = 2000
    ccw90 = 1000

    def __init__(self, pin) -> None:
        
        self.servo = PWM(Pin(pin), freq=50)

    def pwm(self, pwm):
        """Timing in microseconds
        1500 is neutral, 2000 is far right, 1000 is far left.
        https://en.wikipedia.org/wiki/Servo_control#/media/File:Servomotor_Timing_Diagram.svg


        :param pwm: microseconds pwm.
        :type pwm: int
        """
        ONE_US = 1024 / 20000
        self.servo.duty(round(pwm * ONE_US))

    def angle(self, angle):
        angle = min(max(angle, -90), 90)
        pwm = scale(angle, (-90, 90), (self.ccw90, self.cw90))
        self.pwm(pwm)
