# defines every program-wide variable

import pathlib as pl
import os
from tools.config_handler import ConfigHandler


ROOT_PATH = pl.Path(__file__).parent.parent
IS_RC = os.path.exists(ROOT_PATH.joinpath('on_rc.txt'))
IS_VEHICLE = os.path.exists(ROOT_PATH.joinpath('on_vehicle.txt'))
SRC_PATH = ROOT_PATH.joinpath('rc') if IS_RC else ROOT_PATH.joinpath('vehicle')
RUNTIME_VARS = {}
TERMINATE = False

if IS_RC:
    CONNECTING_SCREEN_PATH = ROOT_PATH.joinpath('assets', 'connecting_screen.png')

# cooses the alphabetically first config in src/config but can be changed in settings later
files = os.listdir(ROOT_PATH.joinpath('config'))
# remove every file apart from .json files
conf_files = []
for file in files:
    if file.__contains__('.json'):
        conf_files.append(file)
conf_files = sorted(conf_files)

CONF_JSON_PATH_LIST = conf_files

if conf_files.__len__() == 0:
    raise FileNotFoundError('No config files found in config folder')

CONF_JSON_PATH = ROOT_PATH.joinpath('config', conf_files[0])
CONF_MD_PATH = ROOT_PATH.joinpath('config', 'README.md')

VEH_TYPE, COMMUNICATION_KEY, DEBUG_MODE, HEADLESS_MODE = ConfigHandler.init_globals(CONF_JSON_PATH) # gets later declared

LOG_FILE_PATH = ROOT_PATH.joinpath('log', f"{COMMUNICATION_KEY.lower() if IS_VEHICLE else 'rc'}.log")
LOG_PATH = ROOT_PATH.joinpath('log')