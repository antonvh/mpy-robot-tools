### For testing and debugging purposes outside the robot ###
### run tests using pytest
### Also serves as examples of code usage ###

import mpy_robot_tools.hub_stub as hub

def test_hub():
    assert hub.Image("abc") == "abc"

def test_hub2():
    assert hub.display.show(hub.Image("abc")) == "abc"