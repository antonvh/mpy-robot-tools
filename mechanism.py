import math, utime


### These methods return functions for use inside the mechanism class ###

def linear_interpolation(points, wrapping=True, scale_y = 1):
    """
    Returns a method that interpolates values between keyframes / key coordinates.

    Input: list of coordinates
    Returns: A method(!) that interpolates a value between given points

    Arguments:
    - scale_y: scale the y coordinates to enlarge movements or to invert them (scale_y=-1)
    - wrapping: True by default. If an x value is beyond the highest x value in the point list,
    wrapping will wrap the values and look back to the first coordinates.

    Example:
    my_function = linear_interpolation([(0,0), (1000,360), (2000,0)])
    my_function(500)  # returns 180.
    my_function(2500) # Also returns 180, because of wrapping.
    """
    # Sort by timecodes (x's), just to be sure.
    points.sort(key = lambda point: point[0])

    # For the wrapping I use the modulo (%)
    # This works only if the first x == 0.
    # So first rebase the point list to 0
    
    # First Calculate the max range
    x_min = points[0][0]
    x_max = points[-1][0]
    x_range = x_max - x_min

    # Now rebase to x's 0 and invert values if needed
    points = [(x - x_min, scale_y * y) for (x, y) in points]

    # Build our return function
    def function(x):
        # Correct input for the zero-rebased point list
        x -= x_min

        if not wrapping:
            # Extend the extremes to infinity and return
            if x <= points[0][0]:
                return points[0][1]
            elif x >= points[-1][0]:
                return points[-1][1]
        else:
            # Wrap around with the modulo function and continue
            x = x % x_range

        # Now we can safely look up the value in the list
        # Because it is between min_x and max_x 
        # Either because of the module or the truncation
        
        for i in range(len(points)):
            if x < points[i][0]:
                # Found our matching slot
                # Interpolate between two nearest values
                x1,y1 = points[i-1]
                x2,y2 = points[i]
                return y1 + (x - x1)/(x2 - x1)*(y2 - y1)
    return function


def linear(factor, time_delay = 0, offset = 0):
    """
    Returns a function that is a linear proportion to an input.
    """
    y0 = - time_delay * factor + offset
    def function(x):
        return x * factor + y0
    return function


def sine_wave(amplitude=100, period=1000, offset=0):
    def function(x):
        return math.sin((x-offset)/period*2*math.pi) * amplitude
    return function

### Advanced timer class to use together with the Mechanism class ###
class AMHTimer():
    """
    Configurable timer that you can start, reverse, stop and pause.
    By default it counts miliseconds, but you can speed it up,
    Slow it down or accelerate it!
    You can also set the time and reset it.
    You can even run it in reverse, so you can count down until 0.
    It always returns integers, even when you slow it way down.

    Author: Antons Mindstorms Hacks
    
    Usage
    my_timer = AMHTimer():
    my_timer.rate = 500 # set the rate to 500 ticks/s. That is half the normal rate
    my_timer.acceleration = 100 # Increase the rate by 100 ticks / second squared
    my_timer.reset()
    now = mytimer.time
    """
    def __init__(self, rate=1000, acceleration=0):
        self.running = True
        self.pause_time = 0
        self.reset_at_next_start = False
        self.__speed_factor = rate/1000
        self.__accel_factor = acceleration/1000000
        self.start_time = utime.ticks_ms()

    @property
    def time(self):
        if self.running:
            elapsed = utime.ticks_diff( utime.ticks_ms(), self.start_time )
            return int(
                self.__accel_factor * elapsed**2 +
                self.__speed_factor * elapsed +
                self.pause_time
                )
        else:
            return self.pause_time

    @time.setter
    def time(self, setting):
        self.pause_time = setting
        self.start_time = utime.ticks_ms()

    def pause(self):
        if self.running:
            self.pause_time = self.time
            self.running = False

    def stop(self):
        self.pause()

    def start(self):
        if not self.running:
            self.start_time = utime.ticks_ms()
            self.running = True

    def resume(self):
        self.start()

    def reset(self):
        self.time = 0

    def reverse(self):
        self.rate *= -1

    @property
    def rate(self):
        elapsed = utime.ticks_diff( utime.ticks_ms(), self.start_time )
        return (self.__accel_factor*elapsed + self.__speed_factor) * 1000

    @rate.setter
    def rate(self, setting):
        if self.__speed_factor != setting / 1000:
            if self.running:
                self.pause()
            self.__speed_factor = setting / 1000
            self.start()

    @property
    def acceleration(self, setting):
        return self.__accel_factor * 1000000

    @acceleration.setter
    def acceleration(self, setting):
        if self.__accel_factor != setting / 1000000:
            if self.running:
                self.pause()
            self.__speed_factor = self.rate / 1000
            self.__accel_factor = setting / 1000000
            self.start()
            

### This is the central mechanism class that animates the robot ###

class Mechanism():
    def __init__(self, motors, motor_functions, reset_zero=True, ramp_pwm=100, Kp=1.2):
        # Allow for both hub.port.X.motor and Motor objects:
        self.motors = [m._motor_wrapper.motor if '_motor_wrapper' in dir(m) else m for m in motors]
        self.motor_functions = motor_functions
        self.ramp_pwm = ramp_pwm
        self.Kp = Kp

        if reset_zero:
            # Set degrees counted of all motors according to absolute 0
            for motor in motors:
                absolute_position = motor.get()[2]
                if absolute_position > 180:
                    absolute_position -= 360
                motor.preset(absolute_position)

    @staticmethod
    def float_to_motorpower( f ):
        # Convert any floating point to number to
        # an integer between -100 and 100
        return min(max(int(f),-100),100)

    def update_motor_pwms(self, ticks):
        for motor, motor_function in zip(self.motors, self.motor_functions):
            target_position = motor_function(ticks)
            current_position = motor.get()[1]
            power = self.float_to_motorpower((target_position-current_position)* self.Kp)
            if self.ramp_pwm < 100:
                max_power = int(self.ramp_pwm*(abs(ticks)))
                if power < 0:
                    power = max(power, -max_power)
                else:
                    power = min( power, max_power)
            
            motor.pwm( power )    

    def stop(self):
        for motor in self.motors:
            motor.pwm( 0 )


### For testing and debugging purposes outside the robot ###
# Don't copy this into your spike script
if __name__ == "__main__":
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
    points = [(-200, 100), (0, 100), (250, -100), (500, -100), (1000, 100)]
    li_function = linear_interpolation(points, wrapping = False)
    li_function_w = linear_interpolation(points)
    sine_function = sine_wave()
    for i in range(-1100, 2400, 10):
        print("{}\t{}\t{}".format(i, li_function(i), li_function_w(i)))