#!/usr/bin/env micropython
"""Provides a Pybricks-like API for SPIKE2 and LEGO MINDSTORMS Robot Inventor.

Motors are initialized with their relative encoder zeroed to their absolute zero.
You can use SI units to control motors and sensors.
Motors can run in the background with wait=False

"""
__author__ = "Anton Vanhoucke"
__copyright__ = "Copyright 2023, Antons Mindstorms"
__credits__ = ["Pybricks.com"]
__license__ = "MIT"
__version__ = "1.0.0"
__status__ = "Production"

from machine import Timer
from time import sleep

try:
    from hub import port
except:
    from .hub_stub import port


def __clamp_int(n, floor=-100, ceiling=100):
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


def wait(duration_ms):
    """Sleep in miliseconds.

    :param duration_ms: duration (ms)
    :type duration_ms: int or float
    """
    sleep(duration_ms / 1000)


class Port:
    """Enumerator for Port names"""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"


class Direction:
    """Enumerator for Directions"""

    CLOCKWISE = 1
    COUNTERCLOCKWISE = -1


class Stop:
    """Enumerator for Stop modes"""

    BRAKE = 0
    COAST = 1
    HOLD = 2


class ForceSensor:
    def __init__(self, sensor_port):
        self.sensor = eval("port." + sensor_port + ".device")
        _ = self.force()  # Try the sensor

    def force(self):
        return self.sensor.get()[0]

    def pressed(self):
        return self.force() != 0


class UltrasonicSensor:
    """Pybricks-style ultrasonic sensor"""

    def __init__(self, sensor_port):
        """

        Args:
            sensor_port (str): Port to which the sensor is connected

        """
        self.sensor = eval("port." + sensor_port + ".device")
        self.lights = USLights(self.sensor)
        _ = self.distance()  # Test sensor

    def distance(self):
        """Measures the distance between the sensor and an object using ultrasonic sound waves.

        Return:
            Measured distance. If no valid distance was measured, it returns 2000 mm.

        """

        dist = self.sensor.get()[0]
        if dist is None:
            return 2000
        else:
            return dist * 10


class USLights:
    """Ultrasonic sensor lights helper."""

    def __init__(self, sensor) -> None:
        self.sensor = sensor

    def on(self, brightness=100):
        """Turns on the lights at the specified brightness.

        Args:
            brightness (tuple | int): Brightness of each light, in the order shown above. If you give one brightness
            value instead of a tuple, all lights get the same brightness.

        """

        if type(brightness) == int:
            lights = [__clamp_int(brightness / 10, floor=0, ceiling=10)] * 4
        elif len(brightness) == 4:
            lights = [__clamp_int(l / 10, floor=0, ceiling=10) for l in brightness]
        else:
            lights = (10, 10, 10, 10)
        self.sensor.mode(5, bytes(lights))
        self.sensor.mode(0)

    def off(self):
        """Turns off all the lights."""
        self.on(0)


class Motor:
    """Universal motor with universal methods to write agnostic platform helpers.

    This class takes any motor type object as parameter and runs it pybricks-style, with the pybricks motor methods.
    """

    def __init__(self, motor, direction=1):
        motor_dir = dir(motor)
        if "_motor_wrapper" in motor_dir:
            self.control = __MSHubControl(motor._motor_wrapper.motor)
        elif "get" in motor_dir:
            self.control = __MSHubControl(motor)
        elif "run_angle" in motor_dir:
            self.control = motor
        elif "upper" in motor_dir:
            # We have a string or item from the Port enumerator
            if motor in "ABCDEFGH":
                self.control = __MSHubControl(eval("port." + motor + ".motor"))
            else:
                self.control = __MotorStub()
        else:
            print("Unknown motor type")
            # We should probably raise an IOerror here
        self.control.DIRECTION = direction
        self.reset_angle()

    def dc(self, duty):
        """Sets the motor's dc."""
        self.control.dc(duty)

    def angle(self):
        """Returns the motor's angle."""
        return self.control.angle()

    def reset_angle(self, *args):
        """Reset motor's angle.

        :param angle: Pass 0 to set current position to zero. Without arguments this resets to the absolute
            encoder position
        :type angle: int

        """

        self.control.reset_angle(*args)

    def track_target(self, *args, **kwargs):
        """Call this method in closed loop to ensure a motor
        moves to this angle target.

        :param target: target angle, defaults to 0
        :type target: int, optional
        :param gain: motor power proportional to error, defaults to 1.5
        :type gain: float, optional
        """
        self.control.track_target(*args, **kwargs)

    def run(self, speed):
        """Runs the motor at the specified speed.

        Args:
            speed (int?): speed value.
        """
        self.control.run(speed)

    def run_time(self, speed, time, wait=True, stop=Stop.BRAKE):
        """Runs the motor at the specified speed.

        Args:
            speed (int): Speed value.
            time (float): Time in milliseconds.
            wait (bool): ..... Default value True.

        """
        self.control.run_time(speed, time, wait)

    def run_angle(self, speed, rotation_angle, wait=True, stop=Stop.BRAKE):
        """Runs the motor at a particular rotation angle and speed.

        Args:
            speed (int): Speed value.
            rotation_angle (int): Angle value.
            wait (bool): ..... Default value True.

        """
        self.control.run_angle(speed, rotation_angle, wait)

    def run_target(self, speed, target_angle, wait=True, stop=Stop.BRAKE):
        """Runs the motor at a particular target angle and speed.

        Args:
            speed (int): Speed value.
            target_angle (int): Angle value.
            wait (bool): ..... Default value True.

        """
        self.control.run_target(speed, target_angle, wait)

    def run_until_stalled(self, *args, **kwargs):
        return self.control.run_until_stalled(*args, **kwargs)

    def speed(self):
        return self.control.speed()

    def stop(self):
        """Stops the motor."""
        self.dc(0)


class __MSHubControl:
    """Defines a controller for the PBMotor class.
    On SPIKE2 and Robot Inventor.
    """

    DIRECTION = 1
    DESIGN_SPEED = 905  # deg/s

    def __init__(self, motor) -> None:
        self.motor = motor
        # speed_pct, rel_pos, abs_pos, pwm
        self.motor.mode([(1, 0), (2, 0), (3, 0), (0, 0)])
        self.timer = Timer()

    def _pct_2_angular_speed(self, pct_speed):
        return round(pct_speed * self.DESIGN_SPEED / 100) * self.DIRECTION

    def _angular_2_pct_speed(self, angular_speed):
        return __clamp_int(angular_speed / self.DESIGN_SPEED * 100) * self.DIRECTION

    def dc(self, duty):
        self.motor.pwm(__clamp_int(duty * self.DIRECTION))

    def run(self, speed):
        self.motor.run_at_speed(self._angular_2_pct_speed(speed))

    def run_time(self, speed, time, wait=True):
        if wait:
            self.run(speed)
            sleep(time / 1000)
            self.dc(0)
        else:
            self.timer.init(
                mode=Timer.ONE_SHOT, period=time, callback=lambda x: self.motor.dc(0)
            )
            self.run(speed)

    def run_angle(self, speed, rotation_angle, wait=True):
        # run_for_degrees ignores sign on rotation angle, and only looks at speed for direction
        rotation_angle *= self.DIRECTION
        if rotation_angle < 0:
            direction = -1
        else:
            direction = 1
        self.motor.run_for_degrees(
            rotation_angle, abs(self._angular_2_pct_speed(speed)) * direction
        )
        if wait:
            sleep(0.05)
            while not self.done():
                sleep(0.015)

    def run_target(self, speed, target_angle, wait=True):
        # run_top_position ignores sign on speed, and only looks at angle for direction
        self.motor.run_to_position(
            round(target_angle * self.DIRECTION), self._angular_2_pct_speed(speed)
        )
        if wait:
            sleep(0.05)
            while not self.done():
                sleep(0.015)

    def run_until_stalled(self, speed, duty_limit=100):
        duty_limit = abs(duty_limit)
        self.run(speed)
        wait(100)
        while 1:
            speed_pct, rel_pos, abs_pos, pwm = self.motor.get()
            if speed_pct == 0:
                break
            if abs(pwm) > duty_limit:
                break
            wait(10)
        self.dc(0)
        return rel_pos

    def done(self):
        return self.motor.get()[3] == 0  # or self.motor.get()[0] == 0

    def abs_angle(self):
        return self.motor.get()[2] * self.DIRECTION

    def reset_angle(self, *args):
        if len(args) == 0:
            abs_pos = self.motor.get()[2]
            if abs_pos > 180:
                abs_pos -= 360
            tgt = abs_pos
        else:
            tgt = args[0]
        # Ensure angle is set
        while not self.motor.get()[1] == tgt:
            self.motor.preset(tgt)
            wait(10)

    def angle(self):
        return self.motor.get()[1] * self.DIRECTION

    def speed(self):
        return self._pct_2_angular_speed(self.motor.get()[0])

    def track_target(self, target=0, gain=1.5):
        # If track target isn't called again within 500ms, fall back to run_to_position
        self.timer.init(
            mode=Timer.ONE_SHOT,
            period=500,
            callback=lambda x: self.motor.run_to_position(round(target), 100),
        )
        m_pos = self.motor.get()[1]
        self.motor.pwm(__clamp_int((m_pos - target) * -gain))


class __MotorStub:
    __angle = 0
    __dc = 0
    __speed = 0
    __busy = False
    DIRECTION = 1

    def __init__(self) -> None:
        self.timer = Timer()

    def run(self, speed):
        self.__speed = speed

    def dc(self, n):
        self.__dc = n

    def angle(self):
        return self.__angle

    def run_until_stalled(self, *args):
        pass

    def speed(self):
        return self.__speed

    def reset_angle(self, *args):
        if args:
            self.__angle = args[0]
        else:
            self.__angle = 0

    def track_target(self, t, **kwargs):
        self.__angle = round(t)

    def done(self):
        return not self.__busy

    def stop(self):
        self.__speed = 0
        self.__busy = False

    def run_time(self, speed, time, wait=True):
        self.__speed = speed
        self.__busy = True
        if wait:
            sleep(time / 1000)
            self.stop()
        else:
            self.timer.init(
                mode=Timer.ONE_SHOT, period=time, callback=lambda x: self.stop()
            )
        self.__angle += round(speed * time / 1000)

    def run_angle(self, speed, rotation_angle, wait=True):
        self.run_time(speed, rotation_angle / speed * 1000, wait)

    def run_target(self, speed, target_angle, wait=True):
        self.run_angle(speed, target_angle - self.__angle, wait)

    def abs_angle(self):
        return self.__angle % 360


class DriveBase:
    straight_speed = 300
    straight_acceleration = 0
    turn_rate = 0
    turn_acceleration = 0

    def __init__(self, l_motor: Motor, r_motor: Motor, wheel_diameter, axle_width):
        self.l_motor = l_motor
        self.r_motor = r_motor
        self.mm_to_deg = 360 / (wheel_diameter * 3.1415)
        self.axle_width = axle_width
        self.wheel_diameter = wheel_diameter
        self.turn_rate = self.straight_speed * self.axle_width / self.wheel_diameter

    def straight(self, distance):
        self.l_motor.run_angle(
            self.straight_speed, self.mm_to_deg * distance, wait=False
        )
        self.r_motor.run_angle(
            self.straight_speed, self.mm_to_deg * distance, wait=True
        )

    def curve(self, radius, degrees):
        inner_dist = abs(degrees) / 360 * (radius - self.axle_width / 2) * 2 * 3.1415
        outer_dist = abs(degrees) / 360 * (radius + self.axle_width / 2) * 2 * 3.1415
        if degrees < 0:
            self.r_motor.run_angle(
                self.straight_speed, outer_dist * self.mm_to_deg, wait=False
            )
            self.l_motor.run_angle(
                abs(inner_dist) / abs(outer_dist) * self.straight_speed,
                inner_dist * self.mm_to_deg,
                wait=True,
            )
        else:
            self.l_motor.run_angle(
                self.straight_speed, outer_dist * self.mm_to_deg, wait=False
            )
            self.r_motor.run_angle(
                abs(inner_dist) / abs(outer_dist) * self.straight_speed,
                inner_dist * self.mm_to_deg,
                wait=True,
            )

    def drive(self, speed, turn_rate):
        """
        Start driving at speed (mm/s) with turn rate (deg/s)
        """
        turn_speed = turn_rate * self.axle_width / self.wheel_diameter
        self.l_motor.run(speed + turn_speed)
        self.r_motor.run(speed - turn_speed)

    def stop(self):
        self.l_motor.stop()
        self.r_motor.stop()

    def settings(self, *args):
        if len(args) == 4:
            (
                self.straight_speed,
                self.straight_acceleration,
                self.turn_rate,
                self.turn_acceleration,
            ) = args
        else:
            return (
                self.straight_speed,
                self.straight_acceleration,
                self.turn_rate,
                self.turn_acceleration,
            )
