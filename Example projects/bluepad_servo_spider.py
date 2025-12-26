# PS4 gamepad remote controlled spider
# Using an LMS-ESP32 board and four Geekservos
# Get the board here:
# https://antonsmindstorms.com/product/wifi-python-esp32-board-for-mindstorms/

# The LMS-ESP32 runs our fork of bluepad with uartremote
# Get the firmware here:
# https://github.com/antonvh/generic-lms-esp32-uart-fw

# Get the building instructions here:
# https://www.patreon.com/posts/62344422

from projects.mpy_robot_tools.motor_sync import (
    linear_interpolation,
    Mechanism,
    AMHTimer,
)
from projects.mpy_robot_tools.helpers import PBMotor
from projects.mpy_robot_tools.serialtalk import SerialTalk
from projects.mpy_robot_tools.serialtalk.mshub import MSHubSerial
from hub import port
from mindstorms import DistanceSensor

head = DistanceSensor("C")

# Open connection to ESP32 and add 100% power (8V) to it.
ur = SerialTalk(MSHubSerial("D", power=100), timeout=20)

# This is just to remember the order of the servos
FRS = 3  # Front Right Servo
FLS = 4  # Front Left Servo
BLS = 2  # etc..
BRS = 1

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

lower_leg_keyframes = [(0, -40), (2000, -40), (2250, -100), (2500, -40)]


frll = PBMotor("E")  # f.ront r.ight l.ower l.eg
frs = PBMotor("stub")
flll = PBMotor("F")  # inverted direction
fls = PBMotor("stub")
brll = PBMotor("A")  # inverted direction
brs = PBMotor("stub")
blll = PBMotor("B")
bls = PBMotor("stub")

left_servos = Mechanism(
    [fls, bls],
    [
        linear_interpolation(servo_keyframes_f, smoothing=1, time_offset=1 * 625),
        linear_interpolation(servo_keyframes_b, smoothing=1, time_offset=0),
    ],
)

left_lower_legs = Mechanism(
    [flll, blll],
    [
        linear_interpolation(
            lower_leg_keyframes, smoothing=1, time_offset=1 * 625, scale=-1
        ),
        linear_interpolation(lower_leg_keyframes, smoothing=1, time_offset=0),
    ],
)

right_servos = Mechanism(
    [frs, brs],
    [
        linear_interpolation(servo_keyframes_f, smoothing=1, time_offset=3 * 625),
        linear_interpolation(servo_keyframes_b, smoothing=1, time_offset=2 * 625),
    ],
)

right_lower_legs = Mechanism(
    [frll, brll],
    [
        linear_interpolation(lower_leg_keyframes, smoothing=1, time_offset=3 * 625),
        linear_interpolation(
            lower_leg_keyframes, smoothing=1, time_offset=2 * 625, scale=-1
        ),
    ],
)

timer = AMHTimer()
button_timer = AMHTimer()
left_eye = 100
right_eye = 100
while 1:
    ack, pad = ur.call(
        "servos_gp", "4i", brs.angle(), bls.angle(), frs.angle(), fls.angle()
    )
    if ack == "servos_gpack":
        btns, dpad, left_x, left_y, right_x, right_y = pad
    else:
        btns, dpad, left_x, left_y, right_x, right_y = [0] * 6
        print(ack, pad)  # Debug

    speed = left_y / -5.12
    turn = left_x / 5.12

    if abs(turn) < 85:
        # We're moving straight, or with a slight cruve
        if speed > 0:
            timer.rate = (speed**2 + turn**2) ** 0.5 * 15
        else:
            timer.rate = (speed**2 + turn**2) ** 0.5 * -15
        left_ticks = right_ticks = timer.time
        if turn > 0:
            r_scale = 1 - turn / 85
            l_scale = 1
        else:
            l_scale = 1 + turn / 85
            r_scale = 1
    else:
        # We're rotating in place.
        timer.rate = turn * 15
        left_ticks = timer.time
        right_ticks = -timer.time
        l_scale = r_scale = 1

    left_servos.update_motor_pwms(left_ticks, scale=l_scale)
    right_servos.update_motor_pwms(right_ticks, scale=r_scale)
    left_lower_legs.update_motor_pwms(left_ticks)
    right_lower_legs.update_motor_pwms(right_ticks)

    # Now update the eyes
    # Don't look at buttons until 400ms has pass since the last buttonpress
    if button_timer.time > 400:
        if dpad & 1:  # UP is pressed.
            left_eye += 10
            right_eye += 10
            button_timer.reset()
        if dpad & 4:  # LEFT is pressed
            if left_eye == 100:
                left_eye = 0
            else:
                left_eye = 100
            button_timer.reset()
        if dpad & 2:  # DOWN is pressed
            left_eye -= 10
            right_eye -= 10
            button_timer.reset()
        if dpad & 8:  # RIGHT is pressed
            if right_eye == 100:
                right_eye = 0
            else:
                right_eye = 100
            button_timer.reset()

    # Cap the values of both eyes
    if right_eye < 0:
        right_eye = 0
    if right_eye > 100:
        right_eye = 100
    if left_eye < 0:
        left_eye = 0
    if left_eye > 100:
        left_eye = 100

    head.light_up(right_eye, left_eye, right_eye, left_eye)
