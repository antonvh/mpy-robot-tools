# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

# This code is meant as a boilerplate for your remote control project.
# Connect to it using a steering wheel or app:
# https://play.google.com/store/apps/details?id=com.antonsmindstorms.mindstormsrc&hl=nl&gl=US

from projects.mpy_robot_tools.rc import (
    RCReceiver, L_STICK_HOR, L_STICK_VER, R_STICK_HOR, R_STICK_VER,
    L_TRIGGER, R_TRIGGER, SETTING1, SETTING2)
from projects.mpy_robot_tools.helpers import clamp_int
from mindstorms import MSHub, ColorSensor, Motor, DistanceSensor
from mindstorms.control import wait_for_seconds
import math

# Create your objects here.
rcv = RCReceiver(name="robot")
ma = Motor("A")
hub = MSHub()

# Write your program here.
while True: # Forever
    if rcv.is_connected():
        speed, turn = rcv.controller_state(R_STICK_VER, R_STICK_HOR)
        if rcv.button_pressed(1):
            hub.speaker.beep()
        ma.start_at_power(clamp_int(speed))

    else:
        # Stop all motors when not connected
        ma.stop()
        print("Waiting for connection...")
        wait_for_seconds(0.3) # async wait, better than sleep_ms
