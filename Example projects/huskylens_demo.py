# Prints the x and y location of a detected face.
# Click the [>_] icon to open the print output tray in the MINDSTORMS App
# Run on a SPIKE or MINDSORMS hub with Robot Inventor Firmware.
# Connect the huskylens through a SPIKE-OPENMV board on port A
# Put the huskylens in serial/9600 baud mode.
# Connection diagram on the SPIKE-OPENMV board.
#  Red   X      X    Green   X
#  Black X      X    Blue    X
# 
#          [Wire to hub]
#              ||||||


from projects.mpy_robot_tools.pyhuskylens import HuskyLens, ALGORITHM_FACE_RECOGNITION, clamp_int
from hub import button

hl = HuskyLens("A", baud=9600, power=True)
print(hl.mode)

# Get x/y loc of a face
print("Starting face recognition")
hl.set_alg(ALGORITHM_FACE_RECOGNITION)
while not button.right.is_pressed():
    blocks = hl.get_blocks()
    if len(blocks) > 0:
        face_x = blocks[0].x
        face_y = blocks[0].y
        print("Face at ", face_x, face_y)
        