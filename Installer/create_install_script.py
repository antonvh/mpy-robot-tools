#!python3

# Run this on a Mac or Linux machine to create/update 'install_uartremote.py'
# Copy the contents of install_uartremote.py into an empty SPIKE Prime project
# And run to install

import binascii, mpy_cross, time
import hashlib
import os

LIB = '../mpy_robot_tools/'
MPY_LIB = 'mpy/'
INSTALLER = 'install_mpy_robot_tools.py'
BASE_SCRIPT = 'base_script.py'

files = [f for f in os.listdir(LIB) if f not in ['__pycache__']]
encoded = {}

for f in files:
    out_file = f.split(".")[0]+".mpy"
    out_file_loc = MPY_LIB+out_file
    mpy_cross.run('-march=armv6',LIB+f,'-o', out_file_loc)
    mpy_file=open(out_file_loc,'rb').read()
    encoded[out_file] = [
        binascii.b2a_base64(mpy_file).decode('utf-8'), 
        hashlib.sha256(mpy_file).hexdigest()
        ]


spike_code=open(BASE_SCRIPT,'r').read()

with open(INSTALLER,'w') as f:
     f.write(spike_code.format(repr(encoded)))
