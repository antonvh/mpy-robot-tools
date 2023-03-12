# Import from pybricks because I moved these classes there
# This ensures backward compatibility
from .pybricks import (clamp_int, wait, track_target,
                       Port)
from .pybricks import UltrasonicSensor as PBUltrasonicSensor
from .pybricks import Motor as PBMotor


def scale(val, src, dst):
    """Scales the given value from the scale of src to the scale of dst.

    Args:
        val (float | int): ....
        src (tuple): ....
        dst (tuple):

    Return:
        Scaled value.

    Example:
        print scale(99, (0.0, 99.0), (-1.0, +1.0))
    """
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def wait_until(function, condition=True):
    while not function() == condition:
        wait(10)