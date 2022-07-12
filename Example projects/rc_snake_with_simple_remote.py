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
found = remote_control.connect(name="robot")

if not found:
    print ("Scanning timed out")
    del(remote_control)
    raise SystemExit

print("Connected")

# This can probably be less. TODO.
sleep_ms(500)

steer = PBMotor("E")
throttle = PBMotor("C")

button_num = 2
while remote_control.is_connected():
    try: # In case you change the program and make exceptions
        # Check for button presses
        if button.left.was_pressed():
            button_num -=1
            if button_num < 2: button_num = 5
            remote_control.set_button(button_num, True)
            sleep_ms(50)
            remote_control.set_button(button_num, False)
        if button.right.was_pressed():
            button_num +=1
            if button_num > 5: button_num = 2
            remote_control.set_button(button_num, True)
            sleep_ms(50)
            remote_control.set_button(button_num, False)
        # Check motor positions

        # Track the 0 target and generate counter force if you
        # push the motors. Multiply so maximum movement generates
        # a number that is in the range -100,100
        # gain is how hard the motor pushes back
        steer.track_target(0)
        throttle.track_target(0)

        # check rotation of the steering wheel with gyro roll
        steer_angle = motion.yaw_pitch_roll()[2] * 1.5
        remote_control.set_stick(L_STICK_HOR, steer.angle() )

        # Check flappy paddles
        # Returns about 0 if both are pressed or released
        # Returns a positive number if the force sensor is pressed
        remote_control.set_stick(R_STICK_VER, throttle.angle() * 2)

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