import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        output = func(*args, **kwargs)
        total = time.time() - start
        print(f'[TIMER] {func} TIME TAKEN: ', total)
        return output
    return wrapper

class Timer:
    """
    A simple timer class to measure the execution time
    """

    def __init__(self, start=False, interval_resolution=7):
        self.start_time = None
        self.last_intervals = [] # list of intervals
        self.last_interval_time = time.time() if start else None # end time of the last interval / start time of the current interval
        self.interval_resolution = interval_resolution # time intervals stored
        self.start_interval = None # time since start
        if start:
            self.start()
            self.last_interval_time = self.start_time

    def start(self):
        """Start the timer."""
        self.start_time = time.time()
        self.last_interval_time = self.last_interval_time if self.last_interval_time is not None else time.time()

    def stop(self):
        """Stop the timer and return the elapsed time."""
        if self.start_time is None:
            raise ValueError("Timer has not been started.")
        elapsed_time = time.time() - self.start_time
        self.start_time = None
        return elapsed_time
    
    def elapsed(self):
        """Return the elapsed time without stopping the timer."""
        if self.start_time is None:
            raise ValueError("Timer has not been started.")
        self.start_interval = time.time() - self.start_time
        return self.start_interval
    
    def interval(self):
        """Return the time since the last interval."""
        before_last_interval = self.last_interval_time # copy last interval time
        self.last_interval_time = time.time() # set new last interval time
        delta = self.last_interval_time - before_last_interval
        self.last_intervals.append(delta)
        if len(self.last_intervals) > self.interval_resolution:
            self.last_intervals.pop(0)
        return delta
    
    def get_refresh_rate(self):
        """Return the average refresh rate based on the last intervals, in Hz."""
        if not self.last_intervals:
            return 0
        return (1 / (sum(self.last_intervals) / len(self.last_intervals))).__round__(1)