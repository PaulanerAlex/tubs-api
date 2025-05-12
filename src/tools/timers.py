import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        output = func(*args, **kwargs)
        total = time.time() - start
        print(f'[TIMER] {func} TIME TAKEN: ', total)
        return output
    return wrapper

