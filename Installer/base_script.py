#### HOW TO Use this script ####
# 1. REBOOT your hub first!
# 2. Paste this script in an empty Python project
# 3. Optional: Select the packages you need by editing INSTALL dictionary
# 4. Open the console: [>_] button at the bottom of the screen.
# 5. Click the 'run/play' button.
# 6. WAIT FOR THE TEXT TO START SCROLLING IN THE CONSOLE!! The play button will stop spinning, but the script is running!
# 7. When there is no more text scrolling in the console, the installation is done.

# Works with the LEGO SPIKE app and the LEGO MINDSTORMS app

{}

VERBOSE = False

from ubinascii import hexlify, a2b_base64
from uhashlib import sha256
from os import mkdir

encoded = {}


def calc_hash(b):
    return hexlify(sha256(b).digest()).decode()


error = False
try:
    mkdir('/projects/mpy_robot_tools')
except:
    pass

for file, code, hash_gen in encoded:
    package_name = file.split(".")[0].split("/")[0]
    if package_name in INSTALL:
        if not INSTALL[package_name]:
            continue

    target_loc = '/projects/mpy_robot_tools/' + file
    if code == "dir":
        try:
            mkdir(target_loc)
        except:
            pass
            # Directory probably exists

    else: 
        print('Writing ' + target_loc)
        with open(target_loc, 'wb') as f:
            for chunk in code:
                f.write(a2b_base64(chunk))
        del code

        try:
            if VERBOSE:
                print('Finished writing ' + file + ', Checking hash.')
            result = open(target_loc, 'rb').read()
            hash_check = calc_hash(result)
            if VERBOSE:
                print('Hash generated: ', hash_gen)

            if hash_check != hash_gen:
                print('Failed hash of .mpy on the robot: ' + hash_check)
                error = True
        except Exception as e:
            print(e)

del(encoded)

if not error:
    print('Library written successfully. Enjoy!')
else:
    print('Failure in writing library!')
