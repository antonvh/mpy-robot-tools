import ubinascii, os, machine,uhashlib
from ubinascii import hexlify

encoded={'pyhuskylens.mpy': ['TQUCHyCLfOwQUgAHQi4uL21weV9yb2JvdF90b29scy9weWh1c2t5bGVucy5weTkoMDkjVHRlJUWAHR8fHytmJCQkJCQkJCREJCRkIIsUixKLrgCAEBBzbGVlcF9tcxAQdGlja3NfbXMqAhsIdGltZRwFFgEcBRYBWYBRGwxzdHJ1Y3QWAYAQAEgqARsAcxwASBYASFmAEAphdGFuMhAOZGVncmVlcyoCGwhtYXRoHAUWARwFFgFZSBMAgBAIcG9ydCoBGwZodWIcAxYBWUoVAFmAEBRVQVJURGV2aWNlKgEbJHB5YnJpY2tzLmlvZGV2aWNlcxwDFgFZSgEAXTICFghieXRlIwAWDEhFQURFUiMBFgxGQUlMRUQyAxEAfKAiPjQCNAEwHhYOUkVRVUVTVBYcUkVRVUVTVF9CTE9DS1MWHFJFUVVFU1RfQVJST1dTFh5SRVFVRVNUX0xFQVJORUQWLFJFUVVFU1RfQkxPQ0tTX0xFQVJORUQWLFJFUVVFU1RfQVJST1dTX0xFQVJORUQWGlJFUVVFU1RfQllfSUQWKFJFUVVFU1RfQkxPQ0tTX0JZX0lEFihSRVFVRVNUX0FSUk9XU19CWV9JRBYWUkVUVVJOX0lORk8WGFJFVFVSTl9CTE9DSxYYUkVUVVJOX0FSUk9XFhpSRVFVRVNUX0tOT0NLFiJSRVFVRVNUX0FMR09SSVRITRYSUkVUVVJOX09LFiZSRVFVRVNUX0NVU1RPTU5BTUVTFhpSRVFVRVNUX1BIT1RPFiRSRVFVRVNUX1NFTkRfUEhPVE8WLlJFUVVFU1RfU0VORF9LTk9XTEVER0VTFjRSRVFVRVNUX1JFQ0VJVkVfS05PV0xFREdFUxYmUkVRVUVTVF9DVVNUT01fVEVYVBYkUkVRVUVTVF9DTEVBUl9URVhUFhpSRVFVRVNUX0xFQVJOFhxSRVFVRVNUX0ZPUkdFVBYuUkVRVUVTVF9TRU5EX1NDUkVFTlNIT1QWLlJFUVVFU1RfU0FWRV9TQ1JFRU5TSE9UFjxSRVFVRVNUX0xPQURfQUlfRlJBTUVfRlJPTV9VU0IWHFJFUVVFU1RfSVNfUFJPFjBSRVFVRVNUX0ZJUk1XQVJFX1ZFUlNJT04WFlJFVFVSTl9CVVNZEQUWGlJFVFVSTl9JU19QUk+AFjRBTEdPUklUSE1fRkFDRV9S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'], '__init__.mpy': ['TQUCHyAkAAoABzwuLi9tcHlfcm9ib3RfdG9vbHMvX19pbml0X18ucHkAUWMAAA==\n', 'bd0eb1ec00392c81347ab95950ebc33661aa1cb23009054638ed4cbea66fcc3e'], 'bt.mpy': ['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\n', 'c9eedf7eb921a12644a3d36526283f185fb3debffb03f77be6a610fa9767b2c5'], 'light_matrix.mpy': ['TQUCHyCnXDiYBAAHRC4uL21weV9yb2JvdF90b29scy9saWdodF9tYXRyaXgucHk5KFAkJCREIiAoKCgoTCAoKCgoTCAoKCgoTCAoKCgoTCAoKCgoTCAoKCgoTCAoKCgoTCAoKCgoTCAoKCgoTCAoKCgobyAiICsrKytPICsrKytPICsrKytPICsrKytPICsrKytPICsrKytPICsrKytPICsrKytPICsrKytPICsrKytyIIUWhSkAgBAOZGlzcGxheRAKSW1hZ2UqAhsGaHViHAUWARwFFgFZgFEbCnV0aW1lFgGAEBJyYW5kcmFuZ2UqARsMcmFuZG9tHAMWAVmAFgAIiBYCT4YWAniJFgJCLAoRAAgRAAgrAhEACBEACCsCEQAIEQAIKwIRAAgRAAgrAhEACBEACCsCKwWAYhEACBEFKwIRAREBKwIRAAgRASsCEQAIEQErAhEACBEBKwIrBYFiEQERASsCEQAIEQErAhEBEQErAhEBEQAIKwIRAREBKwIrBYJiEQERASsCEQAIEQErAhEBEQErAhEACBEBKwIRAREBKwIrBYNiEQERAAgrAhEBEQAIKwIRAREBKwIRAAgRASsCEQAIEQErAisFhGIRAREBKwIRAREACCsCEQERASsCEQAIEQErAhEBEQErAisFhWIRAREACCsCEQERAAgrAhEBEQErAhEBEQErAhEBEQErAisFhmIRAREBKwIRAAgRASsCEQERAAgrAhEBEQAIKwIRAREACCsCKwWHYhEBEQErAhEBEQErAhEFEQErAhEDEQErAhEBEQErAisFiGIRAREBKwIRAREBKwIRAREBKwIRAAgRASsCEQERASsCKwWJYhYOdGVuc19weCwKEQcRAREBKwMRAREACBEBKwMRAREACBEBKwMRAREACBEBKwMRAREBEQErAysFgGIRAAgRAREACCsDEQERAREACCsDEQAIEQERAAgrAxEACBEBEQAIKwMRAREBEQErAysFgWIRAREBEQErAxEACBEACBEBKwMRAREBEQErAxEBEQAIEQAIKwMRAREBEQErAysFgmIRAREBEQErAxEACBEACBEBKwMRAREBEQErAxEACBEACBEBKwMRAREBEQErAysFg2IRAREACBEBKwMRAREACBEBKwMRAREBEQErAxEACBEACBEBKwMRAAgRAAgRASsDKwWEYhEBEQERASsDEQERAAgRAAgrAxEBEQERASsDEQAIEQAIEQErAxEBEQERASsDKwWFYhEBEQERASsDEQERAAgRAAgrAxEBEQERASsDEQERAAgRASsDEQERAREBKwMrBYZiEQERAREBKwMRAAgRAAgRASsDEQAIEQERAAgrAxEACBEBEQAIKwMRAAgRAREACCsDKwWHYhEBEQERASsDEQERAAgRASsDEQERAREBKwMRAREACBEBKwMRAREBEQErAysFiGIRAREBEQErAxEBEQAIEQErAxEBEQERASsDEQAIEQAIEQErAxEBEQERASsDKwWJYhYQdW5pdHNfcHgyABYQaW1hZ2VfOTkyARYSY29kZWxpbmVzVDICEBZMTUFuaW1hdGlvbjQCFgFRYwADhChdJgUdgJwoI1RmRickRCMmfS4AEhkjATQBwUgZAICwV1vaRgeAIoBj2kICgFpZQwKAsWNKBwBZsWNKAQBdEgBesDQBwLCK+MKwivbDKwDEgEIYgFfFtBIPs1W1VRINslW1VfIrAeXEgeVXhddD4n9ZEAI6FABoMgK0NAE2AcYSB7Y0AWMBAQxudW1iZXJzHTAwMDAwOjA5MDkwOjAwOTAwOjA5MDkwOjAwMDAwgRBRDhQ8bGlzdGNvbXA+DYCuACsAsF9LEwDBEAABFABoMgGxNAE2AS8UQup/YwABAAV0QQ4DA4CuACsAsF9LDADBEgCXsTQBLxRC8X9jAAAABYcQ8EBEEwOAsmBgHydDIiBDJycmQyZtJiYmQyZMSiIjKCwqIwCAgICAgCsFgICAgIArBYCAgICAKwWAgICAgCsFgICAgIArBSsFwLBnWYDBQlWAEhuGNAHCsoBCFoBXw4awsVWzVrBnWYmwsVWzVrBnWYHlWFrXQ+R/WVmyhddEIYCAQhaAV8SJsLFVslawZ1mAsLFVslawZ1mB5VeG10Pkf1mxgeXBsYXXQ6V/gcVCKICwFAB4gDYBWbCAgICAgCsFKwHlwLGA2EQEgLGB5sGwZ1kSAYI0AcW1Q9R/Qm5/UWMAAIE0CBYVBYzbgBSJBwARABcWABYQAxYAGowqAVMzABYAEVEqAVMzARYcdXBkYXRlX2Rpc3BsYXlRYwACgWSrARYAEQWA8CUuLCUAsbAYDGZyYW1lcxIAXiKHaLL3NAGwGBBpbnRlcnZhbBIlFBB0aWNrc19tczYAsBgUc3RhcnRfdGltZYCwGB5uZXh0X2ZyYW1lX3RpbWWAsBgaY3VycmVudF9mcmFtZVFjAAAAiQ0GZnBziFzaAS4TE4D3JDUpH0cwKlEwKlEsNSsxRQCxQxWAEhEUFHRpY2tzX2RpZmYSAxQTNgCwExM2AsGxsBMT20TZgICAgICAKwWAgICAgCsFgICAgIArBYCAgICAKwWAgICAgCsFKwXCEAAZEgBMsBMRNAHdRBuAEgB0sBMBNAHCsFcTA7ATFeVaGANCbYASAGuwEwWAVTQBgthEG4CwEwGwExVVwrBXEwWwEwflWhgDQiGAsBMHsBMHVYFVwrBXEwWwEwWwEwVVgFXlWhgFsFcTA4HlWhgBsBMBEgBrsBMFNAHbRAWAgLAYAxIzFAhzaG93EiUQJxQAaDICsjQBNgE0ATYBWVFjAAEAiQh0aW1lgRBRDicdkAoAKwCwX0sTAMEQAAEUAGgyAbE0ATYBLxRC6n9jAAEABXRBDgMDkAoAKwCwX0sMAMESAJexNAEvFELxf2MAAAAF\n', '840f1af2a2068017d08d8f3315a3eab73db21021a79a571463fb49236e801974'], 'helpers.mpy': ['TQUCHyCBbBAWAAc6Li4vbXB5X3JvYm90X3Rvb2xzL2hlbHBlcnMucHkgbosIJEQAIv8cIoBkKgJTMwEWEmNsYW1wX2ludIAjACoCUzMCFhh0cmFja190YXJnZXSAFg5fX01TSFVCgRYUX19QWUJSSUNLU1QyAxAOUEJNb3RvcjQCFgFRYwEDZgMxLjV0s4ABDAkLQAASBm1heBIGbWluEgBesDQBsjQCsTQCYwAAAm4KZmxvb3IOY2VpbGluZ4Esw4ABFBUNYEApJE4AsBQAVjYAgVXDsBQGcHdtEhGzsfOy0fQ0ATYBWbNjAAAKbW90b3IMdGFyZ2V0CGdhaW6BFAAWGQ2MEGBghQ8AEQAXFgAWEAMWABoyABYAETIBFgRkY1FjAAKDOCIiABEFgBcnJysqKCUqKCVKABIATLE0AcIjArLdRBWAsRMcX21vdG9yX3dyYXBwZXITDbAYARIhsBgAnkI2gBAAVrLdRA+AsbAYAxIDsBgAnkIfgBAScnVuX2FuZ2xlst1ED4CxsBgFEiOwGACeQgiAEgB7IwM0AVlRYwIAAIkDcw5fbW90b3Jfd3JhcHBlcnMSVW5rbm93biBtb3RvciB0eXBlghQqFA0NgCYrMysAsBMAnhIL2UQTgLATBxQXEhexNAE2AVlCGYCwEwCeEg3ZRA6AsBMHFA2xNgFZQgCAUWMAAACJCGR1dHk=\n', '05c470f29abff8b8a3b723d0428ffac58f49b7690ca5f4dfb89b32c26c9d7d49'], 'motor_sync.mpy': ['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']}

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