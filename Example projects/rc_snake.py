# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

# This code is meant to run on a LEGO MINDSTORMS Robot Inventor Snake
# Connect to it using a steering wheel or app:
# https://play.google.com/store/apps/details?id=com.antonsmindstorms.mindstormsrc&hl=nl&gl=US
# Building instructions for the snake:
# https://antonsmindstorms.com/product/robot-snake-with-multiple-51515-inventor-sets/


from hub import port
from time import sleep_ms
import math
from projects.mpy_robot_tools.rc import RCReceiver, R_STICK_VER, L_STICK_HOR, SETTING2
from projects.mpy_robot_tools.motor_sync import Mechanism, AMHTimer
from mindstorms import DistanceSensor

ds = DistanceSensor('A')
rcv = RCReceiver(name="snake")

motors = [
    port.C.motor,
    port.D.motor,
    port.E.motor,
    port.F.motor,
]

def sine_wave_w_params(amplitude=100, period=1000, offset_factor=0):
    def function(x, delay_setting = 0, baseline = 0):
        # global baseline, delay_setting
        return baseline + math.sin((x-delay_setting*offset_factor)/period*2*math.pi) * amplitude
    return function

AMPLITUDE = 60
PERIOD = 2000
DELAY_FACTOR = 2 # ticks, not degrees
DAMPENING = 0.07
motorfuncs = [
    sine_wave_w_params(AMPLITUDE * (1-DAMPENING*0), PERIOD, DELAY_FACTOR*0),
    sine_wave_w_params(AMPLITUDE * (1-DAMPENING*1), PERIOD, DELAY_FACTOR*1),
    sine_wave_w_params(AMPLITUDE * (1-DAMPENING*2), PERIOD, DELAY_FACTOR*2),
    sine_wave_w_params(AMPLITUDE * (1-DAMPENING*3), PERIOD, DELAY_FACTOR*3),
]

snake_body = Mechanism(motors, motorfuncs)

while not rcv.is_connected():
    print("Waiting for connection...")
    sleep_ms(300)

eyes = 100
timer = AMHTimer()
while rcv.is_connected():
    speed, turn, delay_setting = rcv.controller_state(R_STICK_VER, L_STICK_HOR, SETTING2)
    if rcv.button_pressed(1):
        eyes = 100
    if rcv.button_pressed(2):
        eyes = 50
    if rcv.button_pressed(3):
        eyes = 0
    ds.light_up_all(eyes)
    timer.rate = speed*20
    baseline = turn/2
    snake_body.update_motor_pwms(timer.time, delay_setting=delay_setting, baseline=baseline)

raise SystemExit