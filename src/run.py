from config.config import IS_RC, IS_VEHICLE, CONF_JSON_PATH, ROOT_PATH, CONF_MD_PATH

import sys
import traceback
from tools.logger import Logger
from luma.core.error import DeviceNotFoundError

args = sys.argv[1:]
for arg in args:
    if arg.__contains__('conf'):
        CONF_JSON_PATH = ROOT_PATH.joinpath('config', arg)

if IS_RC:
    from rc.entrypoint import init
    from rc.processes import start_proc
if IS_VEHICLE:
    from vehicle.entrypoint import init
    from vehicle.processes import start_proc

if __name__ == "__main__":
    log = Logger(__name__)
    exc = None
    tb = None
    try:
        init() # runs once
        start_proc() # runs continously
    except FileNotFoundError as e:
        # print the error and its likely cause for users that run the program the first time
        print(f'FILE NOT FOUND: {e}')
        missing_conf_file_msg = '---> THIS IS MOST LIKELY CAUSED BY A MISSING CONFIG FILE. PLEASE CHECK ' + str(CONF_MD_PATH) + ' FOR MORE INFORMATION.'
        print(missing_conf_file_msg)
        exc = str(e) + ' ' + missing_conf_file_msg
        tb = traceback.format_exc() + f'\n{missing_conf_file_msg}'
    except DeviceNotFoundError as e: # should not trigger if HEADLESS_MODE is True
        print('DISPLAY NOT FOUND: Please check if the display is connected and powered on.')
        display_not_found_error_msg = '---> THIS IS CAUSED BY MISSING DISPLAY. PLEASE CHECK YOUR DISPLAY CONNECTION.'
        exc = str(e) + ' ' + display_not_found_error_msg
        tb = traceback.format_exc() + f'\n{display_not_found_error_msg}'
    except Exception as e:
        exc = str(e)
        tb = traceback.format_exc()
    finally:
        if exc is not None or tb is not None:
            log.error(str(exc))
            log.traceback(tb)       
            sys.exit(1) # exit with error code if no exception occurred
        sys.exit(0)  # exit with success code if no exception occurred
