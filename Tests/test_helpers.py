from mpy_robot_tools.pybricks import Motor

def test_pbmotor():
    m = Motor('stub')
    assert m.angle() == 0
    m.reset_angle(50)
    assert m.angle() == 50
    m.track_target(90)
    assert m.angle() == 90