from projects.mpy_robot_tools.uartremote import *
from projects.mpy_robot_tools.motor_sync import Mechanism, linear_interpolation, AMHTimer
from projects.mpy_robot_tools.helpers import PBMotor
from hub import port
from utime import sleep_ms


ur=UartRemote('D')
port.D.pwm(100)

FRS=23 # Front Right Servo
FLS=25 # Front Left Servo
BLS=22 # etc..
BRS=21

servo_keyframes = [
    (0, -30),
    (2000, 30),
    (2500, -30),
]

lower_leg_keyframes = [
    (0, -40),
    (2000, -40),
    (2250, -90),
    (2500, -40)
]


frll = PBMotor('E') # f.ront r.ight l.ower l.eg
frs = PBMotor('stub')
flll = PBMotor('F') # inverted direction
fls = PBMotor('stub')
brll = PBMotor('A') # inverted direction
brs = PBMotor('stub')
blll = PBMotor('B')
bls = PBMotor('stub')

motors = [
    frs,
    frll,
    bls,
    blll,
    fls,
    flll,
    brs,
    brll,
]

funcs = [
    linear_interpolation(servo_keyframes, smoothing=1),
    linear_interpolation(lower_leg_keyframes, smoothing=1),
    linear_interpolation(servo_keyframes, smoothing=1, time_offset=625),
    linear_interpolation(lower_leg_keyframes, smoothing=1, time_offset=625),
    linear_interpolation(servo_keyframes, smoothing=1, time_offset=2*625),
    linear_interpolation(lower_leg_keyframes, smoothing=1, time_offset=2*625,scale=-1),
    linear_interpolation(servo_keyframes, smoothing=1, time_offset=3*625),
    linear_interpolation(lower_leg_keyframes, smoothing=1, time_offset=3*625,scale=-1),
]

m = Mechanism(motors, funcs)

t = AMHTimer()
while 1:
    m.update_motor_pwms(t.time)
    ur.call('set_angles', 'repr', {FRS:frs.angle(), FLS:fls.angle(), BRS:brs.angle(), BLS:bls.angle()})
