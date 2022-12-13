# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

# This code is meant to run on a hotrod model with LEGO MINDSTORMS Robot Inventor,
# in combination with the Transmitter model and code

# Building instructions for the transmitter:
# https://antonsmindstorms.com/product/remote-control-transmitter-with-mindstorms-51515/
#
# Building instructions for the hot rod:
# https://antonsmindstorms.com/product/remote-controlled-hot-rod-with-51515/


from hub import sound
from projects.mpy_robot_tools.rc import RCReceiver, R_STICK_VER, L_STICK_HOR, SETTING1, L_TRIGGER
from projects.mpy_robot_tools.helpers import PBMotor as Motor
from projects.mpy_robot_tools.helpers import Port, wait

rcv = RCReceiver(name="robot")

steer = Motor(Port.F)
propulsion = Motor(Port.E)

steer.run_until_stalled(100, duty_limit=30)
steer.reset_angle(200)

while 1:
    if rcv.is_connected():
        steer_target, speed_target, trim, thumb = rcv.controller_state(L_STICK_HOR, R_STICK_VER, SETTING1, L_TRIGGER)
    else:
        steer_target, speed_target, trim, thumb = (0,0,0,0)


    steer.track_target(steer_target*-2 + trim)
    propulsion.dc(speed_target)
    if thumb > 50:
        sound.beep(400,25)
        wait(20)