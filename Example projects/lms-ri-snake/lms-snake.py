from hub import port
from utime import sleep_ms
import math
from projects.mpy_robot_tools.bt import RCAppReceiver, RIGHT_STICK_VERTICAL, LEFT_STICK_HORIZONTAL
from projects.mpy_robot_tools.motor_sync import Mechanism, AMHTimer

rcv = RCAppReceiver(name="snake")
# TODO: Find out how to host both a central and peripheral in the first segment of the snake.
# Maybe pass on the ble object? Hope their irq's don't clash?

motors = [
    port.A.motor,
    port.B.motor,
    port.C.motor,
    port.D.motor,
]

baseline = 0
def sine_wave_global_baseline(amplitude=100, period=1000, offset=0):
    def function(x):
        # global baseline
        return baseline + math.sin((x-offset)/period*2*math.pi) * amplitude
    return function

AMPLITUDE = 55
PERIOD = 2000
DELAY = 90
motorfuncs = [
    sine_wave_global_baseline(AMPLITUDE, PERIOD, DELAY*0),
    sine_wave_global_baseline(AMPLITUDE, PERIOD, DELAY*1),
    sine_wave_global_baseline(AMPLITUDE, PERIOD, DELAY*2),
    sine_wave_global_baseline(AMPLITUDE, PERIOD, DELAY*3),
]

snake_body = Mechanism(motors, motorfuncs)

while not rcv.is_connected():
    print("Waiting for connection...")
    sleep_ms(300)

timer = AMHTimer()
while True:
    speed, turn = [rcv.controller[control] for control in [RIGHT_STICK_VERTICAL, LEFT_STICK_HORIZONTAL]]
    timer.rate = speed
    baseline = turn/2
    snake_body.update_motor_pwms(timer.time)