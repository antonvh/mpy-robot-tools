
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
