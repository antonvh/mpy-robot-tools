import ubinascii, os, machine,uhashlib
from ubinascii import hexlify

encoded={}

def calc_hash(b):
    return hexlify(uhashlib.sha256(b).digest()).decode()

error=False
for file, code in encoded.items():
    content=ubinascii.a2b_base64(code[0])
    hash_initial=calc_hash(code[0])
    hash_gen=code[1]
    target_loc = '/projects/mpy_robot_tools/'+file
    try:
        os.mkdir('/projects/mpy_robot_tools')
    except:
        pass
    print('writing '+file+' to folder /projects/mpy_robot_tools')
    with open(target_loc,'wb') as f:
        f.write(content)
    print('Finished writing '+file+', Checking hash.')
    result=open(target_loc,'rb').read()
    hash_check=calc_hash(result)

    print('Hash generated: ',hash_gen)

    if hash_initial != hash_gen:
        print('Failed hash of base64 input : '+hash_initial)
        error=True
    if hash_check != hash_gen:
        print('Failed hash of .mpy on SPIKE: '+hash_check)
        error=True

if not error:
    print('Library written succesfully. Resetting....')
    machine.reset()
else:
    print('Failure in writing library!')