# Based on OpenMV line follower example
# Run this code on an OpenMV H7 plus camera. It probably works on the RT1060 too..

import sensor
import time
import math


# Set up comms to pybricks on the ev3 hub
# Be sure to copy the 'serialtalk' (lowercase) folder with all .py to the
# openmv USB drive.

from serialtalk.auto import SerialTalk

st = SerialTalk()

cam_data = [0,0] # turnrate & speed
def cam():
    # global cam_data
    return cam_data

st.add_command(cam, "repr")

# Tracks a black line. Use [(128, 255)] for a tracking a white line.
GRAYSCALE_THRESHOLD = [(0, 64)]

# Each region of interest is (x, y, w, h).
# The line detection algorithm will try to find the
# centroid of the largest blob in each roi. The x position of the centroids
# will then be averaged with different weights where the most weight is assigned
# to the roi near the bottom of the image and less to the next roi and so on.
# Image size is QQVGA, 160x120

WROIS = [  # (ROI x,y,w,h, weight, angle weight) Weighted Regions Of Interest
    (0, 90, 160, 30,    15),  # Bottom area
    (20, 60, 120, 30,    10),  # Middle area
    (0, 35,     35, 60, 7), # Left of middle
    (80+45, 35, 35, 60, 7), # Right of middle
    (30, 25, 100, 30,   1), # Top area
]
N = len(WROIS)


# Camera setup...
sensor.reset()  # Initialize the camera sensor.
sensor.set_pixformat(sensor.GRAYSCALE)  # use grayscale.
sensor.set_framesize(sensor.QQVGA)  # use QQVGA for speed. w=160,h=120

# Rotate image 180 degrees
sensor.set_vflip(True)
sensor.set_hmirror(True)

sensor.skip_frames(time=500)  # Let new settings take affect.
clock = time.clock()  # Tracks FPS.

while True:
    clock.tick()  # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot()  # Take a picture and return the image.

    centroids = [0] * N
    pixels = [0] * N
    weights = [0] * N
    angles = [0] * N

    for i in range(N):
        blobs = img.find_blobs(
            GRAYSCALE_THRESHOLD, roi=WROIS[i][0:4], merge=True, pixels_threshold=45
        )  # roi[0:4] is roi rectangle.
        #img.draw_rectangle(roi[:4], 0)
        if blobs:
            # Find the blob with the most pixels.
            largest_blob = max(blobs, key=lambda b: b.pixels())

            # Draw relevant blob information
            img.draw_line(largest_blob.major_axis_line(), 60, 3)
            img.draw_cross(largest_blob.cx(), largest_blob.cy())
            img.draw_string(
                            *WROIS[i][:2],
                            f"{largest_blob.pixels()}px\n{largest_blob.rotation_deg()}*" ,
                            255, scale=1, x_spacing=-3)

            centroids[i] = (largest_blob.cx() * WROIS[i][4])
            pixels[i] = largest_blob.pixels()
            weights[i] = WROIS[i][4] # roi[4] is the roi weight
            angles[i] = largest_blob.rotation_deg()-90

    if all(pixels[2:4]):
        # Compare side regions, if both have pixels in them
        # Only go to the side with most pixels
        if pixels[3] > pixels[2]:
            weights[2]=0
            centroids[2]=0
        else:
            weights[3]=0
            centroids[3]=0

    speed = 100

    if any(pixels[2:4]):
        # Pixels at the very edge. Better drive carefully.
        speed = 80

    if centroids:
        # Determine weighted steering target
        center_pos = sum(centroids)/(sum(weights)+0.001)
        turn_rate = round( (center_pos - 80))
    else:
        # No line seen.
        turn_rate = 0 # Just drive straight.
        speed = 80 # Slowly

    # Visualize calculated steering amount. Twice, for thickness.
    img.draw_arrow(80, 5, 80+turn_rate, 5, 255, 10)
    img.draw_arrow(80, 6, 80+turn_rate, 6, 255, 10)

    # Draw all rois
    for r in WROIS:
        img.draw_rectangle(r[:4], 0)

    # Draw speed and turn rate
    img.draw_string(0, 65,
                    f"spd:{speed}\ntrn:{turn_rate}",
                    255, scale=1, x_spacing=-3)

    # Send the computed driving instructions to the EV3 hub
    cam_data = [turn_rate, speed]
    print(cam())
    st.process()
