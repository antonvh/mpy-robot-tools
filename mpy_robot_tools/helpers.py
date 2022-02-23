from machine import Timer
from micropython import const
try:
    from hub import port
except:
    from .hub_stub import port

def clamp_int(n, floor=-100, ceiling=100):
    return max(min(int(n),ceiling),floor)

def track_target(motor, target=0, gain=1.5):
    m_pos = motor.get()[1]
    motor.pwm(
        clamp_int((m_pos-target)*-gain)
    )
    return m_pos

def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.

    val: float or int
    src: tuple
    dst: tuple

    example: print scale(99, (0.0, 99.0), (-1.0, +1.0))
    """
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]




class PBMotor():
    """
    Universal motor with universal methods
    so we can write helpers platform agnostic.
    this class takes any motor type object as parameter
    and runs it pybricks-style, with the pybricks motor methods
    """
    
    def __init__(self, motor):
        motor_dir = dir(motor)
        if '_motor_wrapper' in motor_dir:
            self.control = MSHubControl(motor._motor_wrapper.motor)
        elif 'get' in motor_dir:
            self.control = MSHubControl(motor)
        elif 'run_angle' in motor_dir:
            self.control = motor
        elif 'upper' in motor_dir:
            # We have a string
            if motor in 'ABCDEFGH':
                self.control = MSHubControl(eval("port."+motor+".motor"))
            else:
                self.control = MotorStub()
        else:
            print("Unknown motor type")
            # We should probably raise an IOerror here
        self.reset_angle()

    def dc(self, duty):
        self.control.dc(duty)

    def angle(self):
        return self.control.angle()

    def reset_angle(self, *args):
        # Pass 0 to set current position to zero
        # Without arguments this resets to the absolute encoder position
        self.control.reset_angle(*args)

    def track_target(self, *args, **kwargs):
        self.control.track_target(*args, **kwargs)

    def stop(self):
        self.control.dc(0)

class MSHubControl():
    """
    add the control class to PB motor to stay in line with the namespace
    here I just want to call motor.control.done() to check if it is
    still running.
    """
    def __init__(self, motor) -> None:
        self.motor = motor
        self.motor.mode([(1, 0), (2, 0), (3, 0), (0, 0)])
        self.timer = Timer()

    def dc(self, duty):
        self.motor.pwm(clamp_int(duty))

    def done(self):
        return self.motor.get()[3] == 0

    def abs_angle(self):
        return self.motor.get()[2]

    def reset_angle(self, *args):
        if len(args) == 0:
            absolute_position = self.motor.get()[2]
            if absolute_position > 180:
                absolute_position -= 360
            self.motor.preset(absolute_position)
        else:
            self.motor.preset(args[0])

    def angle(self):
        return self.motor.get()[1]

    def track_target(self, target=0, gain=1.5):
        # If track target isn't called again within 500ms, fall back to run_to_position
        self.timer.init(
            mode=Timer.ONE_SHOT, 
            period=500, 
            callback=lambda x: self.motor.run_to_position(round(target)))
        track_target(self.motor, target, gain)

class MotorStub():
    __angle = 0

    def dc(self, n):
        self.dc = n

    def angle(self):
        return self.__angle

    def reset_angle(self, *args):
        if args:
            self.__angle = args[0]
        else:
            self.__angle = 0

    def track_target(self, t, **kwargs):
        self.__angle = round(t)

    def done(self):
        return True