import ubinascii, os, machine,uhashlib, time
from ubinascii import hexlify

mpy_installer_files_encoded={}

def calc_hash(b):
    return hexlify(uhashlib.sha256(b).digest()).decode()

error=False
exception=''

try:
    os.mkdir('/projects/mpy_robot_tools')
except:
    pass

for file, code, hash_gen in mpy_installer_files_encoded:
    target_loc = '/projects/mpy_robot_tools/'+file

    # hash_gen=code[1]
    try:
        print('writing '+file+' to Hub /projects/mpy_robot_tools')
        with open(target_loc,'wb') as f:
            for chunk in code:
                f.write(ubinascii.a2b_base64(chunk))
        del code
    except Exception as e:
        error=True
        exception += ('writing:' +file+ ',')
        print(e)

    try:
        print('Finished writing '+file+', Checking hash.')
        result=open(target_loc,'rb').read()
        time.sleep(1)
        hash_check=calc_hash(result)

        if hash_check != hash_gen:
            error=True
            exception += (file+ ' hash_expected:' +hash_check+ ' returned_hash:' +hash_gen+ ',')
        else:
            print('Good Hash: ',file, hash_gen)

    except Exception as e:
        error=True
        exception += (file+ ' hash_expected:' +hash_check+ ' returned_hash:' +hash_gen+ ',')
        print(e)

if not error:
    print('Library written succesfully, rebooting. UNPLUG USB now!')
    time.sleep(0.5)
    print("Resetting....")
    machine.reset()
else:
    print('Errors:', exception)
