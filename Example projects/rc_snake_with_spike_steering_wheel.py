# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

# This code is meant to run a steering wheel 
# and connects to the LEGO MINDSTORMS Robot Inventor Snake
# The script running on the snake is either rc_snake.py (single segment)
# or rc_multi_snake_head.py (multisegment)
# FREE Building instructions for the steering wheel:
# https://antonsmindstorms.com/product/remote-control-steering-wheel-with-spike-prime/
# Building instructions for the snake:
# https://antonsmindstorms.com/product/robot-snake-with-multiple-51515-inventor-sets/

from hub import button, port, motion
from projects.mpy_robot_tools.rc import (
    RCTransmitter, L_STICK_HOR, L_STICK_VER, R_STICK_HOR,
    R_STICK_VER, L_TRIGGER, R_TRIGGER, SETTING1, SETTING2)
from projects.mpy_robot_tools.helpers import PBMotor
from utime import sleep_ms

# Initialize
print("starting BLE")
remote_control = RCTransmitter()

print("Scanning & connecting")
found = remote_control.connect(name="snake")

if not found:
    print ("Scanning timed out")
    del(remote_control)
    raise SystemExit

print("Connected")

# This can probably be less. TODO.
sleep_ms(500)

steer_trim = PBMotor("D")
thumb_trigger = PBMotor("C")
force_sensor = port.B.device
light_sensor = port.A.device
light_sensor.mode((2,0)) # Ambient, Return Pct (0-100)
# roll0=motion.yaw_pitch_roll()[2]


while remote_control.is_connected():
    try: # In case you change the program and make exceptions
        # Check for button presses
        remote_control.set_button(1, button.left.was_pressed())
        remote_control.set_button(2, button.right.was_pressed())
        # Check motor positions

        # Track the 0 target and generate counter force if you
        # push the motors. Multiply so maximum movement generates
        # a number that is in the range -100,100
        # gain is how hard the motor pushes back
        thumb_trigger.track_target(0)
        remote_control.set_trigger(L_TRIGGER, thumb_trigger.angle() * -2)

        # Just reading the position will make the motor act like
        # a pot meter.
        remote_control.set_setting(SETTING2, steer_trim.angle() * 5 )

        # check rotation of the steering wheel with gyro roll
        steer_angle = motion.yaw_pitch_roll()[2] * 1.5
        remote_control.set_stick(L_STICK_HOR, steer_angle )

        # Check flappy paddles
        # Returns about 0 if both are pressed or released
        # Returns a positive number if the force sensor is pressed
        forward = force_sensor.get()[0] * 12 - (light_sensor.get()[0] - 40)*2
        remote_control.set_stick(R_STICK_VER, forward)

        # Pack and transmit all remote control values
        remote_control.transmit()

        # Make sure to clean up when user stops program with center button
        if button.center.is_pressed():
            break

        # Limit the sending rate of control packets to about 30/s
        sleep_ms(30)
    except Exception as e:
        print(e)
        break

# Clean up
remote_control.disconnect()
del(remote_control)
print("Disconnected")
raise SystemExit