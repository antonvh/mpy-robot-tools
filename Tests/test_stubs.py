### For testing and debugging purposes outside the robot ###
### run tests using pytest
### Also serves as examples of code usage ###

import mpy_robot_tools.hub_stub as hub

def test_hub():
    assert hub.Image("abc") == "abc"

def test_hub2():
    assert hub.display.show(hub.Image("abc")) == "abc"

from neopixel import NeoPixel

def test_np():
    np = NeoPixel(21,24)
    np.fill((1,2,3))
    assert np.buf[-1] == 3
    assert np.buf[-2] == 1
    assert np.buf[-3] == 2
    
from machine import Timer
from time import sleep

var = 0

def inc_var(x):
    global var
    var += 1
    print(x)

def test_timer():
    global var
    t = Timer(0)
    t.init(mode=Timer.ONE_SHOT, period=500, callback=inc_var)
    assert var == 0
    sleep(1)
    assert var == 1