from config.config import LOG_FILE_PATH, DEBUG_MODE
from tools.messenger import Messenger
import logging as log
import os
import linecache

def log_print(func):
    """
    Decorator to print the log message before and after the function call.
    """
    def wrapper(*args, **kwargs):
        logger = Logger(func.__name__)
        logger.info(f'Starting {func.__name__}')
        result = func(*args, **kwargs)
        logger.info(f'Finished {func.__name__}')
        return result
    return wrapper

def write_to_log(func):
    '''
    Decorator to write to log
    '''
    def wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
        try: 
            with open(LOG_FILE_PATH, 'a') as f:
                f.write(output)
        except FileNotFoundError:
            os.file.create()
        return output
    return wrapper

class Logger:
    def __init__(self, name, path=None):

        self.msgr = Messenger(name=name, log=True)
        self.path = LOG_FILE_PATH if not path else path

        if DEBUG_MODE:
            self.log.setLevel(log.DEBUG)
        else:
            self.log.setLevel(log.INFO)

    @write_to_log
    def debug(self, msg, time=None):
        return self.msgr.fromat_message(status = 1, message=msg, log=True)

    @write_to_log
    def info(self, msg, time=None):
        return self.msgr.fromat_message(status = 0, message=msg, log=True)

    @write_to_log
    def critical(self, msg, time=None):
        return self.msgr.fromat_message(status = 4, message=msg, log=True)

    @write_to_log
    def warning(self, msg, time=None):
        return self.msgr.fromat_message(status = 2, message=msg, log=True)
    
    @write_to_log
    def error(self, msg, time=None):
        return self.msgr.fromat_message(status = 3, message=msg, log=True)

    def view_log(self, lines_index):
        cursor = 0
        content =  ''
        with open(f'logs/{self.log.name}.log', 'r') as f:
            lines = f.readlines() # FIXME: debug
            cursor = lines.__len__() - lines_index
        with open(f'logs/{self.log.name}.log', 'r') as f:
            for count, line in enumerate(f):
                if count > cursor:
                    content += line
            return content

