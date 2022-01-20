#!python3

# Run this on a Mac or Linux machine to create/update 'install_mpy_robot_tools.py'
# Copy the contents of install_mpy_robot_tools.py into an empty SPIKE/51515 project
# And run to install. The transfer and program run will take extra time.
# to restore to OEM, allow LEGO app to update your hub, tools will be rempved.
# Optionally if you clone https://github.com/antonvh/UartRemote and uartremote.py
# will be installed with mpy_robot_tools
#
# Open the console/Debug and watch for notice to unplug USB BEFORE you upload/run

import binascii, mpy_cross, time
import hashlib
import os
from functools import partial

LIB = '../mpy_robot_tools/'
LIB_UART = '../../LMS-uart-esp/Libraries/UartRemote/MicroPython/uartremote.py'
MPY_LIB = 'mpy/'
INSTALLER = 'install_mpy_robot_tools.py'
BASE_SCRIPT = 'base_script.py'
BAD_NAMES = ['__pycache__.py','REDME.md']

mpy_installer_files_encoded = []

def mpy_tools_compile(py_file_in, build_dir):
    global mpy_installer_files_encoded
    #in_dir = os.path.dirname(py_file_in)
    in_file = os.path.basename(py_file_in)

    if in_file in BAD_NAMES:
        #skip file
        return None

    out_file = in_file.split(".")[0]+".mpy"
    out_file_loc = build_dir+out_file
    mpy_cross.run('-march=armv6', py_file_in,'-o', out_file_loc)
    time.sleep(0.5)
    with open(out_file_loc,'rb') as mpy_file:
        file_hash = hashlib.sha256(mpy_file.read()).hexdigest()
    chunks = []
    with open(out_file_loc,'rb') as mpy_file:
        for chunk in iter(partial(mpy_file.read, 2**10), b''):
            chunks += [binascii.b2a_base64(chunk).decode('utf-8')]

    print(out_file,": ",len(chunks)," chunks of ",2**10)

    # string for final installer
    mpy_installer_files_encoded += [(
        out_file,
        tuple(chunks), 
        file_hash
    )]

    return mpy_installer_files_encoded

if os.path.exists(LIB_UART):
    print("found UART library")
    mpy_tools_compile(LIB_UART, MPY_LIB)

files = [f for f in os.listdir(LIB)]
for f in files:
    mpy_tools_compile(LIB+f, MPY_LIB)

# open base installer
spike_code=open(BASE_SCRIPT,'r').read()

# inject the encoded files as base64 for install in lego app
with open(INSTALLER,'w') as f:
     f.write(spike_code.format(repr(tuple(mpy_installer_files_encoded))))
