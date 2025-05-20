# defines every program-wide variable

import pathlib as pl
import os

DEBUG_MODE = False
HEADLESS_MODE = False
IS_RC = os.path.exists(pl.Path('is_rc.txt'))
IS_VEHICLE = os.path.exists(pl.Path('is_vehicle.txt'))
SRC_PATH = pl.Path('src', 'rc') if IS_RC else pl.Path('vehicle')
COMMUNICATION_KEY = None # gets later declared
RUNTIME_VARS = {}

if IS_RC:
    CONF_JSON_PATH = pl.Path('src', 'config', 'conf.json')
if IS_VEHICLE:
    # cooses the alphabetically first config in src/config but can be changed in settings later
    conf_files = os.listdir(pl.Path('src', 'config'))
    # remove conf.py from json config files
    for conf_file in conf_files:
        if conf_file[-3:] == '.py':
            conf_files.remove(conf_file)
    conf_files = sorted(conf_files)

    CONF_JSON_PATH = pl.Path('src', 'config', conf_files[0])

# TODO: get suffix for vehicle

status_msgs = {}

