
from mechanism import AMHTimer, linear_interpolation, sine_wave
from display_image99 import image_99
import utime

### For testing and debugging purposes outside the robot ###
### Also serves as examples of code usage ###

if __name__ == "__main__":
    f = open("numbers.txt", 'w')
    for i in range(100):
        f.write(image_99(i)+"\n")

    print("Run some timer tests and examples")
    mytimer = AMHTimer()
    mytimer.rate = 500
    mytimer.reset()
    utime.sleep_ms(500)

    mytimer.pause()
    print(mytimer.time)
    mytimer.rate = -1000

    mytimer.resume() 
    mytimer.reset()
    utime.sleep_ms(500)
    mytimer.pause()
    print(mytimer.time)

    mytimer.rate = 100
    mytimer.acceleration = 200
    mytimer.start()
    while mytimer.rate < 1000:
        utime.sleep_ms(100)
        print(mytimer.time, mytimer.rate)

    print("Count down from 10 seconds")
    mytimer.time = 10000
    mytimer.rate = -1000
    mytimer.acceleration = 0

    while mytimer.time >= 0:
        utime.sleep_ms(1000)
        print(mytimer.time)

    print("Now run some linear interpolation tests")
    points = [(-200, 100), (0, 100), (250, -100), (500, -100), (1000, 200)]
    li_function = linear_interpolation(points, wrapping = False)
    li_function_w = linear_interpolation(points, accumulation=False)
    li_function = linear_interpolation(points)
    sine_function = sine_wave()
    for i in range(-1100, 2400, 10):
        print("{0}\t{1:.2f}\t{2:.2f}".format(i, li_function(i), li_function_w(i)))