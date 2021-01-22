import utime


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
            

if __name__ == "__main__":
    # Run some tests and examples
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

    # Count down from 10 seconds
    mytimer.time = 10000
    mytimer.rate = -1000
    mytimer.acceleration = 0

    while mytimer.time >= 0:
        utime.sleep_ms(1000)
        print(mytimer.time)