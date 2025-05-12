#! /bin/bash

REPO_LINK=""
REPO_FOLDER_NAME=""

# prompt user for setup type
read -p "Setup for remote controller or vehicle? (Enter 'rc' or 've'): " SETUP_TYPE

# validate user input
if [[ "$SETUP_TYPE" != "rc" && "$SETUP_TYPE" != "ve" ]]; then
    echo "ERROR: Invalid input. Please enter 'rc' for remote controller or 've' for vehicle."
    exit 1
fi

# keep-alive: update existing `sudo` time stamp until the script finishes
sudo -v
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# check if the system is Raspberry Pi OS 32-bit
if [[ "$(uname -m)" == "armv7l" && -f /etc/os-release && "$(grep 'Raspbian' /etc/os-release)" ]]; then
    echo "detected System is Raspberry Pi OS 32-bit."
else
    echo "ERROR: detected System is not Raspberry Pi OS 32-bit."
    exit 1
fi

# get latest os updates
sudo apt update && sudo apt upgrade

# install python, pip and venv
sudo apt install python3 python3-pip python3-venv

# setup git repo
sudo apt install git
git clone $REPO_LINK
# check if the repo was cloned successfully
if [ $? -ne 0 ]; then
    echo "ERROR: failed to clone the repository."
    exit 1
fi
cd $REPO_FOLDER_NAME/src

# setup virtual environment
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt # TODO: change to uv

if [[ "$SETUP_TYPE" == "rc" ]]; then
    touch src/on_rc.txt
elif [[ "$SETUP_TYPE" == "ve" ]]; then
    touch src/on_vehicle.txt
fi

# TODO: setup auto run on startup

# start entry point
python3 run.py
