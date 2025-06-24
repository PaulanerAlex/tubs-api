from tools.network import network_init
from config.config import HEADLESS_MODE, CONNECTING_SCREEN_PATH, DEBUG_MODE
import time
import datetime
from tools.logger import Logger

log = Logger(__name__)

def init():
    if not HEADLESS_MODE:
        _init_standard()
    else:
        _init_headless()
    
    log.info('Initialization complete.')

def _init_headless():
    network_init() # TODO: add error handling

def _init_standard():
    from rc.gui import GUI
    gui = GUI()
    gui.display_image(CONNECTING_SCREEN_PATH)
    now = datetime.datetime.now()
    try:
        network_init()
    except Exception as e:
        gui.display_text(f'Network init error:\n{e}')
        time.sleep(5)
        raise e

    # display the screen at least 2 seconds
    while datetime.datetime.now() - now < datetime.timedelta(seconds=2):
        time.sleep(0.3)
