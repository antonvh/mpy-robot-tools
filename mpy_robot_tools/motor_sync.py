
import math, utime


### These meta-functions return functions for use inside the mechanism class ###
def linear_interpolation(points, wrapping=True, scale=1, accumulation=True, time_offset=0, smoothing=0.0):
    """
    Returns a method that interpolates values between keyframes / key coordinates.

    Input: list of coordinates
    Returns: A method(!) that interpolates a value between given points

    Arguments:
    - scale_y: scale the y coordinates to enlarge movements or to invert them (scale_y=-1)
    - wrapping: True by default. If an x value is beyond the highest x value in the point list,
    wrapping will wrap the values and look back to the first coordinates.
    - accumulation: Boolean. True, by default. After each wraparound, 
    adds the difference between the first and last keyframe.
    - time_offset: offset the first values in the keyframes by this number
    - smoothing: Increase up to 1.0 for maximum cosine smoothing. This is sometimes called 'easing'

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
    points = [(x - x_min, scale * y) for (x, y) in points]

    # Calculate accumulation with first and last keyframe
    accumulation_per_period = 0
    if accumulation:
        accumulation_per_period = points[-1][1] - points[0][1]    

    # Safety precautions around smoothing, clamp between 0.0 and 1.0
    smoothing = min(max(0.0, smoothing),1.0)

    # Build our return function
    def function(x):
        # Correct input for the zero-rebased point list
        x -= x_min + time_offset

        if not wrapping:
            # Extend the extremes to infinity and return
            if x <= points[0][0]:
                return points[0][1]
            elif x >= points[-1][0]:
                return points[-1][1]

        # Wrap around with the modulo function and continue
        x_phase = x % x_range
        x_periods = x // x_range

        # Now we can safely look up the value in the list
        # Because it is between min_x and max_x

        for i in range(len(points)):
            if x_phase < points[i][0]:
                # Found our matching slot
                # Interpolate between two nearest values
                x1,y1 = points[i-1]
                x2,y2 = points[i]
                gap = y2 - y1
                progress = (x_phase - x1)/(x2 - x1)
                if smoothing:
                    smooth_progress = (1-math.cos(math.pi*progress)) / 2
                else:
                    # Avoid unnecessary cosine calculations
                    smooth_progress = 0
                interpolated_y = y1 + smoothing*smooth_progress*gap + (1-smoothing)*progress*gap
                return x_periods*accumulation_per_period + interpolated_y
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

def block_wave(amplitude=100, period=1000, offset=0):
    def function(ticks):
        phase = ticks % period
        if offset < phase < offset + period//2:
            return amplitude
        else:
            return -amplitude
    return function


### Advanced timer class to use together with the Mechanism class ###
class AMHTimer():
    """
    A configurable timer which you can start, reverse, stop and pause.
    By default, it counts milliseconds, but you can speed it up,
    Slow it down or accelerate it!
    You can also set the time and reset it.
    You can even run it in reverse, so you can count down until 0.
    It always returns integers, even when you slow it way down.

    Author: 
        Anton's Mindstorms Hacks - https://antonsmindstorms.com

    Usage:
        my_timer = AMHTimer():
        my_timer.rate = 500  # set the rate to 500 ticks/s. That is half the normal rate
        my_timer.acceleration = 100  # Increase the rate by 100 ticks / second squared
        my_timer.reset()  # Reset to zero. Doesn't change running/paused state
        now = mytimer.time  # Read the time
        mytimer.time = 5000  #Set the time
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
    def acceleration(self):
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
    """
    The class helps to control multiple motors in a tight loop python program.

    Author:
        Anton's Mindstorms Hacks - https://antonsmindstorms.com

    Args:
        motors: list of motor objects. Can be hub.port.X.motor or Motor('X')
        motor_functions: list of functions that take one argument and calculate motor positions

    Optional Args:
        reset_zero: bolean, resets the 0 point of the relative encoder to the absolute encoder position
        ramp_pwm: int, a number to limit maximum pwm per tick when starting. 0.5 is a good value for a slow ramp.
        Kp: float, proportional feedback factor for motor power.

    Returns:
        None.

    Usage:
        my_mechanism = Mechanism([Motor('A'), Motor('B')], [func_a, func_b])
        timer = AMHTimer()
        while True:
            my_mechanism.update_motor_pwms(timer.time)
    """
    def __init__(self, motors, motor_functions, reset_zero=True, ramp_pwm=100, Kp=1.2):
        # Allow for both hub.port.X.motor and Motor('X') objects:
        self.motors = [m._motor_wrapper.motor if '_motor_wrapper' in dir(m) else m for m in motors]
        self.motor_functions = motor_functions
        self.ramp_pwm = ramp_pwm
        self.Kp = Kp
        if reset_zero:
            self.relative_position_reset()

    def relative_position_reset(self, motors_to_reset=[]):
        if not motors_to_reset:
            motors_to_reset = [1]*len(self.motors)
        # Set degrees counted of all motors according to absolute 0
        for motor, reset in zip(self.motors, motors_to_reset):
            if reset:
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
        # Proportional controller toward disered motor positions at ticks
        for motor, motor_function in zip(self.motors, self.motor_functions):
            target_position = motor_function(ticks)
            current_position = motor.get()[1]
            power = self.float_to_motorpower((target_position-current_position)* self.Kp)
            if self.ramp_pwm < 100:
                # Limit pwm for a smooth start
                max_power = int(self.ramp_pwm*(abs(ticks)))
                if power < 0:
                    power = max(power, -max_power)
                else:
                    power = min( power, max_power)

            motor.pwm( power )

    def shortest_path_reset(self, ticks=0, speed=20, motors_to_reset=[]):
        # Get motors in position smoothly before starting the control loop
        if not motors_to_reset:
            motors_to_reset = [1]*len(self.motors)

        # Reset internal tacho to range -180,180
        self.relative_position_reset(motors_to_reset)

        # Run all motors to a ticks position with shortest path
        for motor, motor_function, reset in zip(self.motors, self.motor_functions, motors_to_reset):
            if reset:
                target_position = int(motor_function(ticks))
                current_position = motor.get()[1]
                # Reset internal tacho so next move is shortest path
                if target_position - current_position > 180:
                    motor.preset(current_position + 360)
                if target_position - current_position < -180:
                    motor.preset(current_position - 360)
                # Start the manouver
                motor.run_to_position(target_position, speed)

        # Give the motors time to spin up
        utime.sleep_ms(50)
        # Check all motors pwms until all maneuvers have ended
        while True:
            pwms = []
            for motor in self.motors:
                pwms += [motor.get()[3]]
            if not any(pwms): break
        
    def stop(self):
        for motor in self.motors:
            motor.pwm(0)