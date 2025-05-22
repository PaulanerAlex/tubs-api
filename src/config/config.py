# defines every program-wide variable

import pathlib as pl
import os

ROOT_PATH = pl.Path(__file__).parent.parent
DEBUG_MODE = False
HEADLESS_MODE = False
IS_RC = os.path.exists(ROOT_PATH.joinpath('is_rc.txt'))
IS_VEHICLE = os.path.exists(ROOT_PATH.joinpath('is_vehicle.txt'))
SRC_PATH = ROOT_PATH.joinpath('rc') if IS_RC else ROOT_PATH.joinpath('vehicle')
COMMUNICATION_KEY = None # gets later declared
RUNTIME_VARS = {}

if IS_RC:
    CONF_JSON_PATH = ROOT_PATH.joinpath('config', 'conf.json')
if IS_VEHICLE:
    # cooses the alphabetically first config in src/config but can be changed in settings later
    files = os.listdir(ROOT_PATH.joinpath('config'))
    # remove conf.py from json config files
    conf_files = []
    for file in files:
        if file.__contains__('.json'):
            conf_files.append(file)
    conf_files = sorted(conf_files)

    if conf_files.__len__() == 0:
        raise FileNotFoundError('No config files found in config folder')

    CONF_JSON_PATH = ROOT_PATH.joinpath('config', conf_files[0])
