from sen0539 import SEN0539
from serialtalk.auto import SerialTalk

st = SerialTalk()
voice = SEN0539()

def ok():
    voice.play_cmd_id(2)

ok()

def cmd():
    id = voice.get_cmd_id()
#    print(id)
    return id

x,y,pixels = 0,0,0
def get_blob():
#    global x,y,pixels
    return x,y,pixels

st.add_command(ok)
st.add_command(cmd, 'B')
st.add_command(get_blob, 'hhh')


# Single Color RGB565 Blob Tracking Example
#
# This example shows off single color RGB565 tracking using the OpenMV Cam.

import sensor, image, time, math, lcd

lcd.init()

threshold_index = 0 # 0 for red, 1 for green, 2 for blue

# Color Tracking Thresholds (L Min, L Max, A Min, A Max, B Min, B Max)
# The below thresholds track in general red/green/blue things. You may wish to tune them...
thresholds = [(20, 100, 15, 127, 15, 127), # generic_red_thresholds
              (30, 100, -64, -8, -32, 32), # generic_green_thresholds
              (0, 30, 0, 64, -128, 0)] # generic_blue_thresholds

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()

# Only blobs that with more pixels than "pixel_threshold" and more area than "area_threshold" are
# returned by "find_blobs" below. Change "pixels_threshold" and "area_threshold" if you change the
# camera resolution. "merge=True" merges all overlapping blobs in the image.

while(True):
    clock.tick()
    img = sensor.snapshot()
    blobs = img.find_blobs([thresholds[threshold_index]], pixels_threshold=200, area_threshold=200, merge=True)
#    print(blobs)
    pixels = 0
    largest_blob = {}
    for blob in blobs:
        if blob.pixels() > pixels:
            largest_blob = blob
            pixels = blob.pixels()
    if pixels > 0:
        img.draw_rectangle(largest_blob.rect(), thickness = 2)
        x = largest_blob.cx()
        y = largest_blob.cy()
        img.draw_cross(largest_blob.cx(), largest_blob.cy(), thickness=2)

    st.process_uart()
    
    # If you have the LCD shield:
    lcd.display(img.scale(x_scale=0.4, y_scale=0.4, copy=True))

    
