### For testing and debugging purposes outside the robot ###
### run tests using pytest
### Also serves as examples of code usage ###

from mpy_robot_tools.motor_sync import AMHTimer, linear_interpolation, sine_wave, Mechanism
from mpy_robot_tools.helpers import PBMotor
from time import sleep

def test_linear_interpolation():
    print("Now run some linear interpolation tests")
    points = [(-200, 100), (0, 100), (250, -100), (500, -100), (1000, 200)]
    li_function_1 = linear_interpolation(points, smoothing=1.0)
    li_function_2 = linear_interpolation(points, smoothing=0.5)
    li_function_3 = linear_interpolation(points, accumulation=False, wrapping=False)
    sine_function = sine_wave()

    assert sine_function(0) == 0
    assert li_function_1(-700) == -200 # Wrapping and accumulation
    assert li_function_3(-200) == 100

    li1_out = [li_function_1(i) for i in range(-1100, 2400, 10)]
    li2_out = [li_function_2(i) for i in range(-1100, 2400, 10)]
    li3_out = [li_function_3(i) for i in range(-1100, 2400, 10)]
    sine_out = [sine_function(i) for i in range(-1100, 2400, 10)]

    assert min(sine_out) == -100
    assert max(sine_out) == 100
    assert min(li3_out) == -100
    assert max(li3_out) == 200

def test_mechanism():
    s1 = PBMotor('stub1')
    s2 = PBMotor('stub2')
    motors = [s1, s2]
    funcs = [sine_wave(amplitude=90), sine_wave(amplitude=-90)]
    m = Mechanism(motors, funcs)
    m.update_motor_pwms(1000)
    assert s1.angle() == 0
    assert s2.angle() == 0

    m.update_motor_pwms(500)
    assert s1.angle() == 0
    assert s2.angle() == 0

    m.update_motor_pwms(250)
    assert s1.angle() == 90
    assert s2.angle() == -90
    
def test_timer():
    print("Run some timer tests and examples")
    mytimer = AMHTimer()
    mytimer.rate = 500
    mytimer.reset()
    sleep(0.5)
    mytimer.pause()
    # At 500 ticks per second, sleeping 500ms should give us about 250 ticks.
    assert 250 <= mytimer.time <= 252

    # Now test counting backwards at full speed
    mytimer.rate = -1000
    mytimer.reset()
    mytimer.resume() # Resetting resets time to 0, but doesn't change pause/resume
    sleep(0.5)
    mytimer.pause()
    # Counting back from 0 for half a second at 1000 ticks should give us
    assert -505 <= mytimer.time <= -500

    mytimer.rate = 100
    mytimer.acceleration = 200 # ticks per second
    duration=2 #s
    mytimer.reset()
    mytimer.start()
    sleep(duration)
    mytimer.pause()
    end_time = duration*100 + duration**2*200
    end_rate = 100 + duration*200
    assert end_time <= mytimer.time <= end_time+5 
    assert end_rate <= mytimer.rate <= end_rate+5

    # Count down from 5 seconds
    mytimer.time = 5
    mytimer.rate = -1
    mytimer.acceleration = 0
    mytimer.resume()
    for i in range(5,0,-1):
        # Count down from five and wait a second in between to check timer.
        assert mytimer.time is i
        sleep(0.995)


    