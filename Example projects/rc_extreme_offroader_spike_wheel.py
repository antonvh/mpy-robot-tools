# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

# This code is meant to run a steering wheel 
# and connects to the Extreme Offroader 42099 set
# FREE Building instructions for the steering wheel:
# https://antonsmindstorms.com/product/remote-control-steering-wheel-with-spike-prime/

from hub import port, motion, button
from projects.mpy_robot_tools.ctrl_plus import SmartHub
from projects.mpy_robot_tools.helpers import PBMotor

from utime import sleep_ms

thub = SmartHub()
thub.connect()

steer_trim = PBMotor("D")
thumb_trigger = PBMotor("C")
force_sensor = port.B.device
light_sensor = port.A.device
light_sensor.mode((2,0)) # Ambient, Return Pct (0-100)
# roll0=motion.yaw_pitch_roll()[2]

while thub.is_connected() and not(button.center.is_pressed()):
    trim = steer_trim.angle() * 4

    # check rotation of the steering wheel with gyro roll
    steer_angle = motion.yaw_pitch_roll()[2] * 1.0

    # Check flappy paddles
    # Returns about 0 if both are pressed or released
    # Returns a positive number if the force sensor is pressed
    speed = force_sensor.get()[0] * 12 - (light_sensor.get()[0] - 40)*2
    
    thub.run_target("C", int(steer_angle+trim))
    thub.dc(1, -speed)
    thub.dc(2, -speed)
    sleep_ms(10)

thub.dc(1, 0)
thub.dc(2, 0)
thub.disconnect()

raise SystemExit