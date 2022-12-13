# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

# This code is meant to run on an RC Transmitter model with LEGO MINDSTORMS Robot Inventor

# Building instructions for the transmitter:
# https://antonsmindstorms.com/product/remote-control-transmitter-with-mindstorms-51515/

from projects.mpy_robot_tools.helpers import PBMotor as Motor
from projects.mpy_robot_tools.helpers import Port, wait
from projects.mpy_robot_tools.bt import RCTransmitter, L_STICK_HOR, R_STICK_VER, SETTING1, L_TRIGGER

tx = RCTransmitter()
found = tx.connect(name="robot")

steer = Motor(Port.E)

trigger = Motor(Port.C)

trim = Motor(Port.B)
trim.run_target(300,0)

thumb = Motor(Port.A)

TRIGGER_CENTER = 40
THUMB_TARGET = 30

def scale_and_clamp(value, source_min=-100, source_max=100, target_min=-100, target_max=100):
    scaled_value = (float(value - source_min) / (source_max - source_min)) * (target_max - target_min) + target_min
    clamped_value = min(max(scaled_value, target_min), target_max)
    return round(clamped_value)

while 1:
    steer.track_target(0)
    trigger.track_target(TRIGGER_CENTER)
    thumb.track_target(THUMB_TARGET)

    # scale_and_clamp() makes sure data is in the range of -100,100 as much
    # as possible.
    steer_value = scale_and_clamp( steer.angle(), -85, 85 )
    throttle_value = scale_and_clamp( trigger.angle()-TRIGGER_CENTER, 18, -18)
    trim_value = trim.angle()
    thumb_value = scale_and_clamp( thumb.angle(), 15, 3, 0, 100 )

    tx.set_stick(L_STICK_HOR, steer_value )
    tx.set_stick(R_STICK_VER, throttle_value )
    tx.set_stick(SETTING1, trim_value )
    tx.set_stick(L_TRIGGER, thumb_value )

    tx.transmit()

    # print(data)
    # Limit data rate
    wait(15)