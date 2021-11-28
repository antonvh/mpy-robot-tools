### For testing and debugging purposes outside the robot ###
### run tests using pytest
### Also serves as examples of code usage ###

from mpy_robot_tools.light_matrix import image_99

def test_image99():
    print("image 99 test: create numbers.txt file")
    f = open("numbers.txt", 'w')
    for i in range(100):
        f.write(image_99(i)+"\n")
    assert image_99(5) == "00999:00900:00999:00009:00999"