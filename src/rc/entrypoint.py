from tools.network import network_init
from config.config import HEADLESS_MODE
import time


def init():
    if not HEADLESS_MODE:
        _init_standard()
    else:
        _init_headless()

def _init_headless():
    network_init() # TODO: add error handling

def _init_standard():
    from rc.gui import GUI
    gui = GUI()
    gui.display_image('assets/connecting_screen.png')
    try:
        network_init()
    except Exception as e:
        gui.display_text(f'Network init error:\n{e}')
        time.sleep(5)
        raise e

