### For testing and debugging purposes outside the robot ###
### run tests using pytest
### Also serves as examples of code usage ###

from mpy_robot_tools.light import image_99
from mpy_robot_tools.np_animation import to_grb, from_grb, hsl_to_rgb, rgb_to_hsl
from random import randint

def test_image99():
    print("image 99 test: create numbers.txt file")
    f = open("numbers.txt", 'w')
    for i in range(100):
        f.write(image_99(i)+"\n")
    assert image_99(5) == "00999:00900:00999:00009:00999"

def test_to_from_bgr():
    rgb = randint(0,255), randint(0,255), randint(0,255)
    assert rgb == from_grb(to_grb(rgb))

def test_to_from_hsl():
    rgb = randint(0,255), randint(0,255), randint(0,255)
    rgb2 = hsl_to_rgb(*rgb_to_hsl(*rgb))
    for c, c2 in zip(rgb,rgb2):
        # There is a loss of resolution by going to 100 from 255
        assert c-2 <= c2 <= c+2

def test_to_from_rgb():
    hsl = randint(0,360), randint(0,100), randint(0,100)
    hsl2 = rgb_to_hsl(*hsl_to_rgb(*hsl))
    for c, c2 in zip(hsl,hsl2):
        assert c-1 <= c2 <= c+1