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

    def track_target(self, t):
        self.__angle = t
    

class PBMotor():
    """
    Universal motor with universal methods
    so we can write helpers platform agnostic.
    this class takes any motor type object as parameter
    and runs it pybricks-style, with the pybricks motor methods
    """
    __MSHUB = const(0)
    __PYBRICKS = const(1)
    
    def __init__(self, motor):
        motor_dir = dir(motor)
        if '_motor_wrapper' in motor_dir:
            self.motor = motor._motor_wrapper.motor
            self.kind = self.__MSHUB
        elif 'get' in motor_dir:
            self.motor = motor
            self.kind = self.__MSHUB
        elif 'run_angle' in motor_dir:
            self.motor = motor
            self.kind = self.__PYBRICKS
        elif 'upper' in motor_dir:
            # We have a string
            if motor in 'ABCDEFGH':
                self.kind = self.__MSHUB
                self.motor = eval("port."+motor+".motor")
            else:
                self.kind = 1
                self.motor = MotorStub()
        else:
            print("Unknown motor type")
            # We should probably raise an IOerror here
        self.reset_angle()
        self.timer = Timer()

    def dc(self, duty):
        if self.kind == self.__MSHUB:
            self.motor.pwm(clamp_int(duty))
        elif self.kind == self.__PYBRICKS:
            self.motor.dc(duty)

    def abs_angle(self):
        return self.motor.get()[2]

    def angle(self):
        if self.kind == self.__MSHUB:
            return self.motor.get()[1]
        elif self.kind == self.__PYBRICKS:
            return self.motor.angle()

    def servo_pwm(self):
        return clamp_int(scale(
            self.motor.angle(), 
            (-90, 90),
            (40, 115)
            ), 40, 115)

    def reset_angle(self, *args):
        # Pass 0 to set current position to zero
        # Without arguments this resets to the absolute encoder position
        if self.kind == self.__MSHUB:
            if len(args) == 0:
                absolute_position = self.motor.get()[2]
                if absolute_position > 180:
                    absolute_position -= 360
                self.motor.preset(absolute_position)
            else:
                self.motor.preset(args[0])
        elif self.kind == self.__PYBRICKS:
            self.motor.reset_angle(*args)

    def track_target(self, target, gain=1.5):
        if self.kind == self.__MSHUB:
            # If track target isn't called again within 500ms, fall back to run_to_position
            self.timer.init(
                mode=Timer.ONE_SHOT, 
                period=500, 
                callback=lambda x: self.motor.run_to_position(target))
            track_target(self.motor, target, gain)
            
        elif self.kind == self.__PYBRICKS:
            self.motor.track_target(target)