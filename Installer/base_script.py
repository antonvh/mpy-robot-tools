import ubinascii, os, machine,uhashlib
from ubinascii import hexlify
from utime import sleep_ms

encoded={}

def calc_hash(b):
    return hexlify(uhashlib.sha256(b).digest()).decode()

error=False
try:
    os.mkdir('/projects/mpy_robot_tools')
except:
    pass

for file, code, hash_gen in encoded:
    print("Writing file ", file)
    # hash_gen=code[1]
    target_loc = '/projects/mpy_robot_tools/'+file
    
    print('writing '+file+' to folder /projects/mpy_robot_tools')
    with open(target_loc,'wb') as f:
        for chunk in code:
            f.write(ubinascii.a2b_base64(chunk))
    del code

    try:
        print('Finished writing '+file+', Checking hash.')
        result=open(target_loc,'rb').read()
        hash_check=calc_hash(result)

        print('Hash generated: ',hash_gen)

        if hash_check != hash_gen:
            print('Failed hash of .mpy on SPIKE: '+hash_check)
            error=True
    except Exception as e:
        print(e)


if not error:
    print('Library written succesfully. UNPLUG USB now!')
    sleep_ms(7000)
    print("Resetting....")
    machine.reset()
else:
    print('Failure in writing library!')