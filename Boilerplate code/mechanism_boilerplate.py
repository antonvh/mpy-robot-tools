### Boilerplate code for animating robots
### Facilitates synchronzing different motor movements
### Author: Anton Mindstorms Hacks
### Source: https://antonsmindstorms.com/
### Tutorials: https://www.youtube.com/c/AntonsMindstormsHacks/

from projects.mpy_robot_tools.motor_sync import Mechanism, AMHTimer, sine_wave, linear_interpolation, linear, block_wave
from hub import port

# Setup
motors = [
    port.A.motor,
]
motor_functions = [
    sine_wave(),
]

my_mechanism = Mechanism(motors, motor_functions)
my_mechanism.shortest_path_reset()

# Start control loop
timer= AMHTimer()
while timer.time < 10000:
    my_mechanism.update_motor_pwms(timer.time)
my_mechanism.stop()

# Stop program
raise SystemExit