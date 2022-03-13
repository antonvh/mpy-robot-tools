# Mecanum wheel remote controlled LEGO MINDSTORMS Robot Inventor Robot.
# Using an LMS-ESP32 board. Get the board here:
# https://antonsmindstorms.com/product/wifi-python-esp32-board-for-mindstorms/

# The LMS-ESP32 runs our fork of bluepad with uartremote
# Get the firmware here: 
# https://github.com/antonvh/generic-lms-esp32-uart-fw

# Building instructions here:
# https://www.patreon.com/posts/60769850



from projects.mpy_robot_tools.helpers import clamp_int
from mindstorms import ColorSensor, Motor
from projects.mpy_robot_tools.serialtalk import SerialTalk
from projects.mpy_robot_tools.mshub import MSHubSerial
from hub import port

ur = SerialTalk( MSHubSerial('D'), timeout=20)
ls = ColorSensor('C')

flw = Motor("A") # Front Left Wheel
frw = Motor("B")
blw = Motor("E")
brw = Motor("F")

light = 100

while 1:
    ack, pad = ur.call('gamepad')
    if ack=="gamepadack":
        btns, dpad, left_x, left_y, right_x, right_y = pad
    else:
        btns, dpad, left_x, left_y, right_x, right_y = [0]*6
        print(ack, pad) # Debug
    speed = left_y/-5.12
    turn = left_x/5.12
    strafe = right_x/5.12

    ls.light_up_all(light)
    flw.start_at_power(clamp_int(-speed - turn - strafe))
    frw.start_at_power(clamp_int( speed - turn - strafe))
    blw.start_at_power(clamp_int(-speed + turn - strafe))
    brw.start_at_power(clamp_int( speed + turn - strafe))
