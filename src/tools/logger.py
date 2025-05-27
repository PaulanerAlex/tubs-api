from config.config import LOG_FILE_PATH, DEBUG_MODE
from tools.messenger import Messenger
import logging as log
import os
import linecache

def print_log(func):
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

class Logger:
    def __init__(self, name, path=None):

        self.msgr = Messenger(name=name, log=True)
        self.path = LOG_FILE_PATH if not path else path

        fHandler.setFormatter(formatter)

        self.log.addHandler(stream)
        self.log.addHandler(fHandler)

        if DEBUG_MODE:
            self.log.setLevel(log.DEBUG)
        else:
            self.log.setLevell(log.INFO)

    def debug(self, msg):
        self.log.debug(msg)

    def info(self, msg):
        self.log.info(msg)

    def critical(self, msg):
        self.log.critical(msg)

    def warning(self, msg):
        self.log.warning(msg)
    
    def error(self, msg):
        self.log.error(msg)

    def view_log(self, lines_index):
        cursor = 0
        content =  ''
        with open(f'logs/{self.log.name}.log', 'r') as f:
            lines = f.readlines()
            cursor = lines.__len__() - lines_index
        with open(f'logs/{self.log.name}.log', 'r') as f:
            for count, line in enumerate(f):
                if count > cursor:
                    content += line
            return content

