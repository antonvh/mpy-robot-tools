# Boilerplate code for animating the display of the hub in sync with a timer
# (c) 2021 Anton's Mindstorms Hacks

from mpy_robot_tools.light_matrix import codelines, LMAnimation
from mpy_robot_tools.motor_sync import AMHTimer

# ASCII art lightness
B = 9
W = 8
O = 7
o = 6
x = 5
z = 4
l = 3
_ = 0

# Some framed animations
frames = [
    [
        [B,B,_,B,B],
        [B,B,_,B,B],
        [_,_,_,_,_],
        [B,_,_,_,B],
        [_,B,B,B,_]],
    [
        [B,B,_,_,_],
        [B,B,_,B,B],
        [_,_,_,_,_],
        [B,_,_,_,B],
        [_,B,B,B,_]],
]

timed_frames = [
    (1000, 
    [
        [B,B,_,B,B],
        [B,B,_,B,B],
        [_,_,_,_,_],
        [B,_,_,_,B],
        [_,B,B,B,_]
    ]),
    (300,
    [
        [B,B,_,_,_],
        [B,B,_,o,o],
        [_,_,_,_,_],
        [B,_,_,_,B],
        [_,B,B,B,_]
    ]),
]


codelines_frames = codelines()
animation = LMAnimation(codelines_frames)
animation2 = LMAnimation(timed_frames)
animation3 = LMAnimation(frames)

for i in range(1000):
    animation.update_display()

my_timer = AMHTimer()
while my_timer.time < 1000:
    animation2.update_display(my_timer.time)