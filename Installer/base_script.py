#### HOW TO Use this script ####
# 1. REBOOT your hub first!
# 2. Paste this script in an empty Python project
# 3. Optional: Select the packages you need by editing INSTALL dictionary
# 4. Open the console: [>_] button at the bottom of the screen.
# 5. Click the 'run/play' button.
# 6. WAIT FOR THE TEXT TO START SCROLLING IN THE CONSOLE!! The play button will stop spinning, but the script is running!
# 7. When there is no more text scrolling in the console, the installation is done.

# Only Works with the LEGO SPIKE 2.0 LEGACY app and the LEGO MINDSTORMS app

VERBOSE = False

from ubinascii import hexlify, a2b_base64
from uhashlib import sha256
from os import mkdir
import gc

encoded = {}

error = False
try:
    mkdir('/projects/mpy_robot_tools')
except:
    pass

for file_name, code, hash_gen in encoded:
    package_name = file_name.split(".")[0].split("/")[0]

    target_loc = '/projects/mpy_robot_tools/' + file_name
    if code == "dir":
        try:
            mkdir(target_loc)
        except:
            pass
            # Directory probably exists

    else: 
        try:
            with open(target_loc, 'wb') as f:
                for chunk in code:
                    f.write(a2b_base64(chunk))
            del code
            gc.collect()
            print(target_loc + ' written ok.')
        except Exception as e:
            print(e, "While writing", file_name)
            error = True

        try:
            if VERBOSE:
                print('Finished writing ' + file_name + ', Checking hash.')
            result = open(target_loc, 'rb')
            m = sha256()
            while 1:
                chunk = result.read(256)
                if not chunk: break
                m.update(chunk)
            hash = m.digest()
            hash_check = hexlify(hash).decode()
            del(result)
            gc.collect()
        except Exception as e:
            print(e, "While opening file for hash check.")    

        if hash_check != hash_gen:
            print('Failed hash of ' + file_name + ': ' + hash_check)
            error = True
        else:
            if VERBOSE:
                print('Matching hash: ', hash_gen)
        
del(encoded)
gc.collect()

if not error:
    print('Library written successfully. Enjoy!')
else:
    print('Failure in writing library!')
