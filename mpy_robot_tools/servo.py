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
    """Class to control a hobby servo.
    By default 1500 is neutral (0º), 2000 is far right (90º), 1000 is far left (-90º).
    https://en.wikipedia.org/wiki/Servo_control#/media/File:Servomotor_Timing_Diagram.svg

    Args:
        pin (int): IO Pin for the servo data line.
        min_pulse (int, optional): Min pulse width in µs for a 2ms frame. Defaults to 1000.
        max_pulse (int, optional): Max pulse width in µs for a 2ms frame. Defaults to 2000.
        min_angle (int, optional): Minimum angle at min pulse. Defaults to -90.
        max_angle (int, optional): Maximum angle at max pulse. Defaults to 90.
    """
    

    def __init__(self, pin, min_pulse = 1000, max_pulse = 2000, min_angle=-90, max_angle=90) -> None:
        
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.servo = PWM(Pin(pin), freq=50)

    def pwm(self, pwm):
        """Set servo pulse width in µs for a 2ms frame
        
        :param pwm: microseconds pulse width.
        :type pwm: int or float
        """
        ONE_US = 1024 / 20000
        pwm = min(max(pwm, self.min_pulse), self.max_pulse)
        self.servo.duty(round(pwm * ONE_US))

    def angle(self, angle:float) -> None:
        """Set servo angle. Values are capped between min_angle and max_angle, as set at init.

        Args:
            angle (float or int): target angle for the servo.
        """
        angle = min(max(angle, self.min_angle), self.max_angle)
        pwm = scale(angle, (self.min_angle, self.max_angle), (self.min_pulse, self.max_pulse))
        self.pwm(pwm)
