# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

# This code is meant to run on a segment of the LEGO MINDSTORMS Robot Inventor Snake
# and waits for connection from the head. Update the Segment number!
# Building instructions for the snake:
# https://antonsmindstorms.com/product/robot-snake-with-multiple-51515-inventor-sets/


from hub import port, display
from projects.mpy_robot_tools.bt import UARTPeripheral
from projects.mpy_robot_tools.light import CONNECT_IMAGES, image_99
from projects.mpy_robot_tools.motor_sync import Mechanism, sine_wave

# Change the SEGMENT number before downloading !!
SEGMENT = 1
LOGO = image_99(50+SEGMENT) # 5 looks like an S.
CONNECT_ANIMATION = [LOGO + img for img in CONNECT_IMAGES]

# Create link to the snake head, and advertise self as snakesN where N is the segment number.
head_link = UARTPeripheral(name="snakes"+str(SEGMENT), additive_buffer=False)

motors = [
    port.C.motor,
    port.D.motor,
    port.E.motor,
    port.F.motor,
]

AMPLITUDE = 60
PERIOD = 2000
DELAY = PERIOD * 0.2
DAMPENING = 0.02
motorfuncs = [
    sine_wave(AMPLITUDE * (1- DAMPENING*(0 + SEGMENT*4)), PERIOD, DELAY * (0 + SEGMENT*4) ),
    sine_wave(AMPLITUDE * (1- DAMPENING*(1 + SEGMENT*4)), PERIOD, DELAY * (1 + SEGMENT*4) ),
    sine_wave(AMPLITUDE * (1- DAMPENING*(2 + SEGMENT*4)), PERIOD, DELAY * (2 + SEGMENT*4) ),
    sine_wave(AMPLITUDE * (1- DAMPENING*(3 + SEGMENT*4)), PERIOD, DELAY * (3 + SEGMENT*4) ),
]

snake_body = Mechanism(motors, motorfuncs)

head_time = 0
animation_showing = False
while 1:
    if head_link.is_connected():
        display.show(LOGO)
        animation_showing = False
        data = head_link.read()
        if data:
            head_time = eval(data)
        snake_body.update_motor_pwms(head_time)
    else:
        if not animation_showing:
            display.show(CONNECT_ANIMATION, delay=100, wait=False, loop=True)
            animation_showing = True
        snake_body.stop()
# seg_2_link.disconnect()

raise SystemExit