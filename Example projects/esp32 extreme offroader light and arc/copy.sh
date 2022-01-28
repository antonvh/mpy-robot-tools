USB=$(ls /dev/tty* | grep usb)
rshell -p $USB "cp -r mpy_robot_tools /pyboard"
rshell -p $USB "cp main.py /pyboard"
