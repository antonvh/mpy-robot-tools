# Import from pybricks because I moved these classes there
# This ensures backward compatibility
from .pybricks import wait, Port
from .pybricks import UltrasonicSensor as PBUltrasonicSensor
from .pybricks import Motor as PBMotor

def clamp_int(n, floor=-100, ceiling=100):
    """Limits input number to the range of -100, 100
    and returns an integer

    :param n: input number
    :type n: int or floar
    :param floor: lowest limit >= , defaults to -100
    :type floor: int, optional
    :param ceiling: highest limit <=, defaults to 100
    :type ceiling: int, optional
    :return: clamped number
    :rtype: int
    """
    return max(min(round(n), ceiling), floor)


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


def wait_until(func: function, condition=True):
    """Calls input function every 10ms until it returns the wanted condition.

    :param func: Function to test against condition
    :type func: function
    :param condition: condition to stop waiting, defaults to True
    :type condition: bool, optional
    """
    while not func() == condition:
        wait(10)
