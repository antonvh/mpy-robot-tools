from mpy_robot_tools.helpers import PBMotor

def test_pbmotor():
    m = PBMotor('stub')
    assert m.angle() == 0
    m.reset_angle(50)
    assert m.angle() == 50
    m.track_target(90)
    assert m.angle() == 90
    assert m.servo_pwm() == 115