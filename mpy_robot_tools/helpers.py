from machine import Timer

def clamp_int(n, floor=-100, ceiling=100):
    return max(min(int(n),ceiling),floor)

def track_target(motor, target=0, gain=1.5):
    m_pos = motor.get()[1]
    motor.pwm(
        clamp_int((m_pos-target)*-gain)
    )
    return m_pos


__MSHUB = 0
__PYBRICKS = 1

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
            self.motor = motor._motor_wrapper.motor
            self.type = __MSHUB
        elif 'get' in motor_dir:
            self.motor = motor
            self.type = __MSHUB
        elif 'run_angle' in motor_dir:
            self.motor = motor
            self.type = __PYBRICKS
        else:
            print("Unknown motor type")
            # We should probably rais an IOerror here

    def dc(self, duty):
        if self.type == __MSHUB:
            self.motor.pwm(clamp_int(duty))
        elif self.type == __PYBRICKS:
            self.motor.dc(duty)

    def reset_angle(self, *args):
        # Pass 0 to set current position to zero
        # Without arguments this resets to the absolute encoder position
        if self.type == __MSHUB:
            if len(args) == 0:
                absolute_position = self.motor.get()[2]
                if absolute_position > 180:
                    absolute_position -= 360
                self.motor.preset(absolute_position)
            else:
                self.motor.preset(args[0])
        elif self.type == __PYBRICKS:
            self.motor.reset_angle(*args)

    def track_target(self, target, gain=1.5):
        if self.type == __MSHUB:
            track_target(self.motor, target, gain)
            # This timer should be overwritten and reset if you call track target again within 500ms
            self.t = Timer(mode=Timer.ONE_SHOT, period=500, callback=lambda x:self.motor.run_to_position(target))
            # Just checking.
            print("Ran to position")
        elif self.type == __PYBRICKS:
            self.motor.track_target(target)