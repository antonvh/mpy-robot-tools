#### HOW TO Use this script ####
# 1. REBOOT your hub first!
# 2. Paste this script in an empty Python project
# 3. Click the 'run/play' button.
# 4. WAIT FOR THE TEXT TO START SCROLLING IN THE CONSOLE!! The play button will stop spinning, but the script is running!
# 5. When there is no more text scrolling in the console, the installation is done.

# Works with the LEGO SPIKE app and the LEGO MINDSTORMS app

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
    print("Writing file ", file)
    target_loc = '/projects/mpy_robot_tools/' + file
    if code == "dir":
        try:
            mkdir(target_loc)
        except:
            pass
            # Directory probably exists

    else: 
        print('writing ' + file + ' to folder /projects/mpy_robot_tools')
        with open(target_loc, 'wb') as f:
            for chunk in code:
                f.write(a2b_base64(chunk))
        del code

        try:
            print('Finished writing ' + file + ', Checking hash.')
            result = open(target_loc, 'rb').read()
            hash_check = calc_hash(result)

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
