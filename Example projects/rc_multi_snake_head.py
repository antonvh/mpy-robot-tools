# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

# This code is meant to run a the head of a LEGO MINDSTORMS Robot Inventor Snake multisegmented
# and connects to the next two segments
# Building instructions for the snake:
# https://antonsmindstorms.com/product/robot-snake-with-multiple-51515-inventor-sets/

# Connect to it using a steering wheel or app:
# https://play.google.com/store/apps/details?id=com.antonsmindstorms.mindstormsrc&hl=nl&gl=US

# LEGO type:standard slot:3 autostart

from hub import port, button
import math
from projects.mpy_robot_tools.bt import BLEHandler, UARTCentral
from projects.mpy_robot_tools.rc import RCReceiver, R_STICK_VER, L_STICK_HOR, SETTING2
from projects.mpy_robot_tools.motor_sync import Mechanism, AMHTimer
from mindstorms import DistanceSensor
from mindstorms.control import wait_for_seconds

ble = BLEHandler()
ds = DistanceSensor('A')

seg_1_link = UARTCentral(ble_handler=ble)
seg_2_link = UARTCentral(ble_handler=ble)

motors = [
    port.C.motor,
    port.D.motor,
    port.E.motor,
    port.F.motor,
]

def sine_wave_w_params(amplitude=100, period=1000, offset_factor=0):
    def function(x, baseline = 0):
        return baseline + math.sin((x-offset_factor)/period*2*math.pi) * amplitude
    return function

AMPLITUDE = 60
PERIOD = 2000
DELAY = PERIOD*0.2
DAMPENING = 0.07
motorfuncs = [
    sine_wave_w_params(AMPLITUDE * (1-DAMPENING*0), PERIOD, DELAY*0),
    sine_wave_w_params(AMPLITUDE * (1-DAMPENING*1), PERIOD, DELAY*1),
    sine_wave_w_params(AMPLITUDE * (1-DAMPENING*2), PERIOD, DELAY*2),
    sine_wave_w_params(AMPLITUDE * (1-DAMPENING*3), PERIOD, DELAY*3),
]

snake_body = Mechanism(motors, motorfuncs)

seg_1_link.connect("snakes1")
seg_2_link.connect("snakes2")

rcv = RCReceiver(name="snake", ble_handler=ble)


eyes = 100
baseline = 0
timer = AMHTimer()
turn_timer = AMHTimer()
turn_timer.time = 5000
while True:
    if rcv.is_connected():
        speed, turn, delay_setting = rcv.controller_state(R_STICK_VER, L_STICK_HOR, SETTING2)
        if rcv.button_pressed(1):
            eyes = 100
        if rcv.button_pressed(2):
            eyes = 50
        if rcv.button_pressed(3):
            eyes = 0
        if rcv.button_pressed(7):
            break
        
        timer.rate = speed*20
        baseline = turn/2

    else:
        if turn_timer.time > 4000:
            dist = port.A.device.get()[0]
            print(dist)
            if dist:
                if dist < 25:
                    baseline = 30
                    turn_timer.reset()
            else:
                baseline = 0
        timer.rate = 1000

    ds.light_up_all(eyes)
    snake_body.update_motor_pwms(timer.time, baseline=baseline)
    seg_1_link.write(repr(timer.time))
    wait_for_seconds(0.020)
    seg_2_link.write(repr(timer.time))
    wait_for_seconds(0.020)
    if button.center.is_pressed():
        break

seg_1_link.disconnect()
seg_2_link.disconnect()

raise SystemExit