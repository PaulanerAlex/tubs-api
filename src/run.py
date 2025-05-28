from config.config import IS_RC, IS_VEHICLE, CONF_JSON_PATH, ROOT_PATH 

import sys

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
    init() # runs once
    start_proc() # runs continously
