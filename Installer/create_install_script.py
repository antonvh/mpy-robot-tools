#!python3

# Run this on a Mac or Linux machine to create/update 'install_mpy_robot_tools.py'
# Copy the contents of install_mpy_robot_tools.py into an empty SPIKE Prime/LEGO MINDSTORMS project
# And run to install

import binascii
import hashlib
import mpy_cross
import os
import time
from functools import partial

SCRIPT_DIR = os.path.dirname(__file__)
LIB = os.path.dirname(SCRIPT_DIR)+'/mpy_robot_tools/'
MPY_LIB = SCRIPT_DIR+'/mpy/'
INSTALLER = SCRIPT_DIR+'/install_mpy_robot_tools.py'
BASE_SCRIPT = SCRIPT_DIR+'/base_script.py'
SKIP_FILES = ['__pycache__', 'servo.py', 'hub_stub.py', 'np_animation.py','sen0539.py']
CHUNK_SIZE = 2 ** 8

files = [f for f in os.listdir(LIB) if f not in SKIP_FILES]
encoded = []

def compile(f):
    global encoded
    out_file = f.split(".")[0] + ".mpy"
    out_file_loc = MPY_LIB + out_file
    mpy_cross.run('-march=armv6','-O3', LIB + f, '-o', out_file_loc)
    time.sleep(0.5)
    with open(out_file_loc, 'rb') as mpy_file:
        file_hash = hashlib.sha256(mpy_file.read()).hexdigest()
    chunks = []
    with open(out_file_loc, 'rb') as mpy_file:
        for chunk in iter(partial(mpy_file.read, CHUNK_SIZE), b''):
            chunks += [binascii.b2a_base64(chunk).decode('utf-8')]
    print(out_file, ": ", len(chunks), " chunks of ", CHUNK_SIZE)
    encoded += [(
        out_file,
        tuple(chunks),
        file_hash
    )]


for f in files:
    abspath = os.path.join(LIB, f)
    # t = os.path.isdir(j)
    if os.path.isdir(abspath):
        try:
            os.mkdir(os.path.join(MPY_LIB,f))
        except:
            pass
            # Dir probably already exists
            
        encoded += [(
            f,
            "dir",
            ""
        )]
        subfiles = [f for f in os.listdir(abspath) if f not in SKIP_FILES]
        for sf in subfiles:
            compile(os.path.join(f, sf))
    else:
        compile(f)
        

spike_code = open(BASE_SCRIPT, 'r').read()

with open(INSTALLER, 'w') as f:
    f.write(spike_code.format(repr(tuple(encoded))))
