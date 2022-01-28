from machine import Pin
from time import sleep_ms

# Prepare a bluetooth handler so both the smarthub and
# the receiver can use the same handler
from mpy_robot_tools.bt import BLEHandler
ble=BLEHandler()

# Prepare remote control
from mpy_robot_tools.rc import RCReceiver, L_STICK_HOR, R_STICK_VER
rcv = RCReceiver(ble_handler=ble)


## Connect to a technic hub
# Let the hub think that the ESP board is a train motor
# by driving the Tx pin (ID2, lead 6) low
tx = Pin(27, Pin.OUT, value=0) # was 19 or 18 on production board.
# rx = Pin(26, Pin.OUT, Pin.PULL_UP, value=1) # optionally drive rx up.

# Now let the hub think that we're a bluetooth remote control
from mpy_robot_tools.ctrl_plus import SmartHub
offroader=SmartHub(ble_handler=ble)
offroader.connect()
# Get 8V over DC to power the leds via the 5v buck
offroader.dc(4,100)

# Prepare the lights
from mpy_robot_tools.np_animation import *

kng = knight_rider_gen()

floodlight_animations = {
    0: [(0, [OFF]*6), (2000, [OFF]*6)],
    1: [(0, [WHITE]*6), (2000, [WHITE]*6)],
    2: EMERGENCY_1,
    3: list(kng),
}

funcs = [
    [ list(range(6)), hue_shift(period=5000) ], # Cabin
    [ [6,7,8,11,10,9], keyframes_dict(floodlight_animations, "floodlight_anim") ], # Emergency lights
    [ [13,14,16,17], switch() ], # headlights
    [ [12,23], indicators(name="right") ], # indicators
    [ [15,20], indicators(name="left") ],
    [ [18,19,21,22], brake_lights()] # tail lights
]
la = NPAnimation(funcs, pin=21, n_leds=24)

while 1:
    if rcv.is_connected():
        speed, turn = rcv.controller_state(R_STICK_VER, L_STICK_HOR)
        if rcv.button_pressed(1):
            headlights = True
        if rcv.button_pressed(2):
            headlights = False
        if rcv.button_pressed(3):
            floodlight_anim = 0
        if rcv.button_pressed(4):
            floodlight_anim = 1
        if rcv.button_pressed(5):
            floodlight_anim = 2
        if rcv.button_pressed(6):
            floodlight_anim = 3
        if rcv.button_pressed(7):
            warning = True
        if rcv.button_pressed(8):
            warning = False   
    else:
        headlights = True
        floodlight_anim = 1
        speed = 0
        turn = 0
        warning=False

    offroader.dc(1,-speed)
    offroader.dc(2,-speed)
    offroader.run_target(3, int(turn))
    
    if warning:
        left=True
        right=True
    else:
        left=False
        right=False

    if turn < 0:
        left = True
    if turn > 0:
        right = True
    

    la.update_leds(speed=speed, right=right, left=left, switch=headlights, floodlight_anim=floodlight_anim)

    # Slow down a bit to give bluetooth time.
    sleep_ms(20)