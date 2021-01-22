import math

def linear_interpolation(points, wrapping=True, invert_values=True):
    # Sort by timecodes
    points.sort(key = lambda point: point[0])

    # For the wrapping I use the modulo (%)
    # This works only if the first x == 0.
    # So first rebase the point list to 0
    
    # First Calculate the max range
    x_min = points[0][0]
    x_max = points[-1][0]
    x_range = x_max - x_min

    if invert_values:
        y_factor = -1
    else:
        y_factor = 1

    # Now rebase to 0 and invert values if needed
    points = [(x - x_min, y_factor * y) for (x, y) in points]

    
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

def linear(factor, time_delay = 0):
    offset = - time_delay * factor
    def function(x):
        return x * factor + offset
    
    return function

def sine_wave(amplitude=100, period=1000, offset=0):
    def function(x):
        return math.sin((x-offset)/period*2*math.pi) * amplitude

    return function


class Mechanism():
    def __init__(self, motors, motor_functions):
        # self.ticks = 0
        # Allow for both hub.port.X.motor and Motor objects:
        self.motors = [m._motor_wrapper if '_motor_wrapper' in dir(m) else m for m in motors]
        self.motor_functions = motor_functions
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
            motor.pwm( self.float_to_motorpower((target_position-current_position)*1.2) )

    def stop(self):
        for motor in self.motors:
            motor.pwm( 0 )


if __name__ == "__main__":
    points = [(-200, 100), (0, 100), (250, -100), (500, -100), (1000, 100)]
    li_function = linear_interpolation(points, wrapping = False)
    li_function_w = linear_interpolation(points)
    sine_function = sine_wave()
    for i in range(-1100, 2400, 10):
        print("{}\t{}\t{}".format(i, li_function(i), li_function_w(i)))