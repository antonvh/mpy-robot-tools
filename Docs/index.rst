#########################################
Mpy Robot Tools api library documentation
#########################################

About mpy_robot_tools
=====================

Mpy_robot_tools is the Swiss army knife for programming animated, interactive robots.
It has an installer for LEGO SPIKE Prime and LEGO MINDSTORMS.

The library works on esp32, SPIKE, and mindstorms EV3,  
or any robot microcontroller that has micropython.

Contributing
============

Please fork and help out this project by adding documentation. Could 
be docstrings, README, or tutorials.


Documentation of the mpy_robot_tools modules
============================================

mpy\_robot\_tools.bt module
-------------------------

.. code-block:: python

   from projects.mpy_robot_tools.bt import BLEHandler, UARTCentral
   from projects.mpy_robot_tools.rc import RCReceiver, R_STICK_VER, L_STICK_HOR, SETTING2

   ble = BLEHandler()
   seg_1_link = UARTCentral(ble_handler=ble)
   seg_2_link = UARTCentral(ble_handler=ble)
   rcv = RCReceiver(name="snake", ble_handler=ble)


.. automodule:: mpy_robot_tools.bt
   :members:
   :undoc-members:
   :show-inheritance:


mpy\_robot\_tools.sen0539 module
--------------------------------

This contains a python API to interface with the DFRobot Sen0539 Voice Recognition sensor. This module supports I2C only, so it won't run on an Inventor hub. Use LMS-ESP32 or OpenMV. The sensor is capable of UART, so theoretically this module could be expanded with UART support.

.. automodule:: mpy_robot_tools.sen0539
   :members:
   :undoc-members:
   :show-inheritance:


mpy\_robot\_tools.ctrl\_plus module
-----------------------------------

This module connects to a Technic smart hhub and is able to control connected devices, read the states of the IMU, and control connected motors.

.. automodule:: mpy_robot_tools.ctrl_plus
   :members:
   :undoc-members:
   :show-inheritance:


mpy\_robot\_tools.helpers module
--------------------------------

Helper modules for frequently used functions. Most of the helpers have moved to the Pybricks module.

.. automodule:: mpy_robot_tools.helpers
   :members:
   :undoc-members:
   :show-inheritance:


mpy\_robot\_tools.light module
------------------------------

Helper functions to control and animate LEDs on the 5x5 light matrix of the SPIKE Prime and Inventor hubs.

.. automodule:: mpy_robot_tools.light
   :members:
   :undoc-members:
   :show-inheritance:


mpy\_robot\_tools.motor\_sync module
------------------------------------

Synchronize motor movements with keyframed animations. Great for animating walker legs in spiders, at-at, tars, gelo etc...

.. automodule:: mpy_robot_tools.motor_sync
   :members:
   :undoc-members:
   :show-inheritance:

mpy\_robot\_tools.np\_animation module
--------------------------------------

Animate Neopixels (ws2812) RGB leds with this module. Great for police lights, inidicator lights, knight-rider animation and more.

.. automodule:: mpy_robot_tools.np_animation
   :members:
   :undoc-members:
   :show-inheritance:

mpy\_robot\_tools.pybricks module
---------------------------------

The Robot Inventor Python api for motors and sensors is not very comfortable. This Pybricks module allows you to use most of the Pybricks API as documented on https://docs.pybricks.com.

.. automodule:: mpy_robot_tools.pybricks
   :members:
   :undoc-members:
   :show-inheritance:

mpy\_robot\_tools.rc module
---------------------------

Legacy module for compatibility reasons. Don't use.

mpy\_robot\_tools.servo module
------------------------------

Simple module to control hobby servos on LMS-ESP32. Converts angles to 2000us PWM signals.

.. automodule:: mpy_robot_tools.servo
   :members:
   :undoc-members:
   :show-inheritance:

mpy\_robot\_tools.pyhuskylens module
------------------------------------

Module with Python API for a Huskylens. This uses the Huskylens serial protocol and get Image AI data.

.. automodule:: pyhuskylens
   :members:
   :undoc-members:
   :show-inheritance:

Stubs
=====

For programming convenience in VS Code I would love to collect stubs of
all LEGO hub libraries. I’ve been looking into micropython-stubber but
it didn’t work for me.

mpy\_robot\_tools.hub\_stub module
----------------------------------

.. automodule:: mpy_robot_tools.hub_stub
   :members:
   :undoc-members:
   :show-inheritance: