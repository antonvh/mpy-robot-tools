# Stub for testing purposes 
try:
    from threading import Timer as ThreadTimer
except:
    pass

class Pin():
    def __init__(self,n):
        pass

class Timer():
    ONE_SHOT = 0
    def __init__(self, *args) -> None:
        self.id = 0
        if args:
            self.id=args[0]
        self.timer = ThreadTimer(0, print)
    
    def __repr__(self) -> str:
        return "Timer id" + str(self.id)

    def add_id_as_arg(self, func):
        def wrapper_func():
            func(self)
        return wrapper_func

    def init(self, mode=ONE_SHOT, period=500, callback=lambda x: print(x)):
        self.timer.cancel()
        self.timer = ThreadTimer(period/1000, self.add_id_as_arg(callback))
        self.timer.start()