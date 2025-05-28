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
        self.last_intervals = [] # time since last interval
        self.interval_resolution = interval_resolution # time intervals stored
        self.start_interval = None # time since start
        if start:
            self.start()

    def start(self):
        """Start the timer."""
        self.start_time = time.time()

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
        self.last_intervals.append(time.time() - self.start_time - self.start_interval)
        if len(self.last_intervals) > self.interval_resolution:
            self.last_intervals.pop(0)
        return self.last_intervals[-1]
    
    def get_refresh_rate(self):
        """Return the average refresh rate based on the last intervals."""
        if not self.last_intervals:
            return 0
        return sum(self.last_intervals[-self.interval_resolution:]) / len(self.last_intervals[-self.interval_resolution:])