# This script runs on an LMS-ESP32 and powers 24 RGB LEDs on the
# LEGO Technic Extreme Offroader set 42099
# Then connect with the LEGO MINDSTORMS Ble app (or a self-built LEGO remote control)
# to steer the car and power the lights.
# App: https://play.google.com/store/apps/details?id=com.antonsmindstorms.mindstormsrc&hl=en&gl=US
# Remote control: https://antonsmindstorms.com/product/remote-control-steering-wheel-with-spike-prime/

### Intallation:
# Solder the 24 leds (8 boards of 3) in a daisy chain
# Connect the LEDs to GND, 5V and Pin 21 for data.
# Connect the ESP to port D on the technic hub.
# Copy this script over to the main.py on the esp. I like to use Thonny for this.
# Also copy the folder with mpy_robot_tools over to the LMS-ESP32 with Thonny.

# Get your LMS-ESP32 board here:
# https://antonsmindstorms.com/product/wifi-python-esp32-board-for-mindstorms/
# Get your RGB LEDs here:
# https://antonsmindstorms.com/product/rgb-ws2812-neopixel-leds-10x6-for-mindstorms/

from machine import Pin
from time import sleep_ms

# Prepare a bluetooth handler so both the smarthub and
# the receiver can use the same handler
from mpy_robot_tools.bt import BLEHandler
from mpy_robot_tools.bt.ctrl_plus import SmartHub
from mpy_robot_tools.np_animation import *

ble=BLEHandler()

# Prepare remote control
from mpy_robot_tools.rc import RCReceiver, L_STICK_HOR, R_STICK_VER
rcv = RCReceiver(ble_handler=ble)


## Connect to a technic hub
# Let the hub think that the ESP board is a train motor
# by driving the Tx pin (ID2, lead 6) low
tx = Pin(18, Pin.OUT, value=0) 
# rx = Pin(19, Pin.OUT, Pin.PULL_UP, value=1) # optionally drive rx up.

offroader=SmartHub(ble_handler=ble)
offroader.connect()
# Get 8V dc in port 4 (D) to power the leds via the 5v buck
offroader.dc(4,100)

### Prepare the light animations

# Generates a knight rider red light scanner for 6 leds,
# going back and forth in 2000ms. 
kng = knight_rider_gen(period=2000, width=6)

# Timings and colors for floodlights
floodlight_animations = {
    0: [(0, [OFF]*6), (2000, [OFF]*6)], # All 6 leds off, all the time
    1: [(0, [WHITE]*6), (2000, [WHITE]*6)], # All 6 leds on, all the time.
    2: EMERGENCY_1, # Alternating red and blue flashes like US police.
    3: list(kng),
}

# Connect all animations to LED positions in the led chain.
funcs = [
    [ [0,1,2,3,4,5], hue_shift(period=5000) ], # Cabin lights on the first 6 leds.
    [ [6,7,8,11,10,9], keyframes_dict(floodlight_animations, name="floodlight_anim") ],
    [ [13,14,16,17], switch(on=WHITE, off=OFF, name="headlights_switch") ], # headlights
    [ [12,23], indicators(name="right_indicators") ], # indicators
    [ [15,20], indicators(name="left_indicators") ],
    [ [18,19,21,22], brake_lights()] # tail lights. They take a 'speed' variable to light accordingly
]

# Create a light animation object with all functions on pin 21.
la = NPAnimation(funcs, pin=21, n_leds=24)

# Start the tight loop for infinite control
while 1:
    if rcv.is_connected():
        # A remote controlle is connected. Let's get the data from it.
        speed, turn = rcv.controller_state(R_STICK_VER, L_STICK_HOR)
        if rcv.button_pressed(1):
            headlights = True
        if rcv.button_pressed(2):
            headlights = False
        if rcv.button_pressed(3):
            floodlights = 0
        if rcv.button_pressed(4):
            floodlights = 1
        if rcv.button_pressed(5):
            floodlights = 2
        if rcv.button_pressed(6):
            floodlights = 3
        if rcv.button_pressed(7):
            warning = True
        if rcv.button_pressed(8):
            warning = False   
    else:
        # Default values without remote controller
        headlights = True
        floodlights = 1
        speed = 0
        turn = 0
        warning=False

    # Make the motors on the offroader run, according the rc commands.
    offroader.dc(1,-speed)
    offroader.dc(2,-speed)
    offroader.run_target(3, int(turn))
    
    # Turn on warning lights if necesary
    if warning:
        left=True
        right=True
    else:
        left=False
        right=False

    # Turn on indicators according to steering value
    if turn < 0:
        left = True
    if turn > 0:
        right = True
    
    # Update LEDS 
    la.update_leds(speed=speed, 
                   right_indicators=right, 
                   left_indicators=left, 
                   headlights_switch=headlights, 
                   floodlight_anim=floodlights)

    # Slow down a bit to give bluetooth time.
    sleep_ms(20)
