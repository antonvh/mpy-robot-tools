# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

# This code is meant to run on a robot with four rotocaster wheels
# The wheels are connected to ports A,B,E and F. C has a color sensor
# Connect to it using a steering wheel or app:
# https://play.google.com/store/apps/details?id=com.antonsmindstorms.mindstormsrc&hl=nl&gl=US

from time import sleep_ms
from projects.mpy_robot_tools.rc import RCReceiver, R_STICK_VER, L_STICK_HOR, R_STICK_HOR
from projects.mpy_robot_tools.helpers import clamp_int
from mindstorms import ColorSensor, Motor

ls = ColorSensor('C')
rcv = RCReceiver(name="roto")
flw = Motor("A") # Front Right Wheel
frw = Motor("B")
blw = Motor("E")
brw = Motor("F")

light = 100
while 1:
    if rcv.is_connected():
        speed, turn, strafe = rcv.controller_state(R_STICK_VER, R_STICK_HOR, L_STICK_HOR)
        if rcv.button_pressed(1):
            light = 100
        if rcv.button_pressed(2):
            light = 50
        if rcv.button_pressed(3):
            light = 0
        if rcv.button_pressed(8):
            break
        ls.light_up_all(light)
        flw.start(clamp_int(-speed - turn - strafe))
        frw.start(clamp_int( speed - turn - strafe))
        blw.start(clamp_int(-speed + turn - strafe))
        brw.start(clamp_int( speed + turn - strafe))

    else:
        flw.start_at_power(0)
        frw.start_at_power(0)
        blw.start_at_power(0)
        brw.start_at_power(0)
        print("Waiting for connection...")
        sleep_ms(300)
