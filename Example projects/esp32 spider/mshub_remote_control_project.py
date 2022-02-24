# Install mpy-robot-tools
# Then paste this script into an empty Python LEGO MINDSTORMS Project in the LEGO App.


from projects.mpy_robot_tools.uartremote import *
from projects.mpy_robot_tools.motor_sync import linear_interpolation, Mechanism, AMHTimer
from projects.mpy_robot_tools.helpers import PBMotor
from projects.mpy_robot_tools.rc import RCReceiver, R_STICK_VER, L_STICK_HOR, L_STICK_VER, R_STICK_HOR
from hub import port
from mindstorms import DistanceSensor

head = DistanceSensor('C')
head.light_up_all()

ur=UartRemote('D')
port.D.pwm(100)

FRS=23 # Front Right Servo
FLS=25 # Front Left Servo
BLS=22 # etc..
BRS=21

servo_keyframes_f = [
    (0, -60),
    (2000, 10),
    (2500, -60),
]

servo_keyframes_b = [
    (0, -10),
    (2000, 60),
    (2500, -10),
]

lower_leg_keyframes = [
    (0, -40),
    (2000, -40),
    (2250, -100),
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

left_servos = Mechanism(
    [fls, bls], 
    [linear_interpolation(servo_keyframes_f, smoothing=1, time_offset=1*625), 
     linear_interpolation(servo_keyframes_b, smoothing=1, time_offset=0)]
    )

left_lower_legs = Mechanism(
    [flll, blll],
    [linear_interpolation(lower_leg_keyframes, smoothing=1, time_offset=1*625,scale=-1),
     linear_interpolation(lower_leg_keyframes, smoothing=1, time_offset=0),]
)

right_servos = Mechanism(
    [frs, brs],
    [linear_interpolation(servo_keyframes_f, smoothing=1, time_offset=3*625),
     linear_interpolation(servo_keyframes_b, smoothing=1, time_offset=2*625),]
)

right_lower_legs = Mechanism(
    [frll, brll],
    [linear_interpolation(lower_leg_keyframes, smoothing=1, time_offset=3*625),
     linear_interpolation(lower_leg_keyframes, smoothing=1, time_offset=2*625,scale=-1),]
)

timer = AMHTimer()
# right_timer = AMHTimer()
rcv = RCReceiver()

while 1:
    if rcv.is_connected():
        speed, turn = rcv.controller_state(L_STICK_VER, L_STICK_HOR)
        if abs(turn) < 85:
            if speed > 0:
                timer.rate = (speed**2+turn**2)**0.5 * 15
            else:
                timer.rate = (speed**2+turn**2)**0.5 * -15
            left_ticks = right_ticks = timer.time
            if turn > 0:
                r_scale = 1 - turn/85
                l_scale = 1
            else:
                l_scale = 1 + turn/85
                r_scale = 1
        else:
            timer.rate = turn * 15
            left_ticks = timer.time
            right_ticks = -timer.time
            l_scale = r_scale = 1

        left_servos.update_motor_pwms(left_ticks, scale=l_scale)
        right_servos.update_motor_pwms(right_ticks, scale=r_scale)
        left_lower_legs.update_motor_pwms(left_ticks)
        right_lower_legs.update_motor_pwms(right_ticks)
        ur.call('set_angles', 'repr', {FRS:frs.angle(), FLS:fls.angle(), BRS:brs.angle(), BLS:bls.angle()})
    else:
        left_servos.stop()
        right_servos.stop()
        left_lower_legs.stop()
        right_lower_legs.stop()
