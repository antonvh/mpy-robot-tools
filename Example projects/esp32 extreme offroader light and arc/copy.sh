# Copy library and main.py to esp on Macos.
# On linux you can simply connect to /dev/ttyAMA0

USB=$(ls /dev/tty* | grep usb)
rshell -p $USB "cp -r ../projects/mpy_robot_tools /pyboard"
rshell -p $USB "cp main.py /pyboard"
