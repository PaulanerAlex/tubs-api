#! /bin/bash

REPO_LINK="https://github.com/PaulanerAlex/tubs-api.git"
REPO_FOLDER_NAME="tubs-api"
SERVICE_NAME="tubs-api.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"
USER=$(whoami)
PYTHON_VERSION_REQUIRED="3.10"

echo "This script will set up rc-remote on your System."

# prompt user for setup type
read -p "Setup for remote controller or vehicle? (Enter 'rc' or 've'): " SETUP_TYPE

# validate user input
if [[ "$SETUP_TYPE" != "rc" && "$SETUP_TYPE" != "ve" ]]; then
    echo "ERROR: Invalid input. Please enter 'rc' for remote controller or 've' for vehicle."
    exit 1
fi

if [[ "$SETUP_TYPE" == "rc" ]]; then
    echo "Setting up for remote controller..."
elif [[ "$SETUP_TYPE" == "ve" ]]; then
    echo "Unfortunately, setup for vehicle is not yet supported. Please clone and install manually according to your vehicle type."
    exit 0
fi

# keep-alive: update existing `sudo` time stamp until the script finishes
sudo -v
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# check if the system is Raspberry Pi OS 32-bit
if [[ "$(uname -m)" == "armv7l" && -f /etc/os-release && $(grep -q 'Raspbian' /etc/os-release && echo true) == "true" && "$SETUP_TYPE" == "rc" ]]; then
    echo "detected System is Raspberry Pi OS 32-bit."
else
    echo "ERROR: detected System is not Raspberry Pi OS 32-bit."
    exit 1
fi

# get latest os updates
sudo apt update && sudo apt upgrade

# check if python3 is installed and version > 3.10
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 is not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ "$(printf '%s\n' "$PYTHON_VERSION_REQUIRED" "$PYTHON_VERSION" | sort -V | head -n1)" == "$PYTHON_VERSION" && "$PYTHON_VERSION" != "$PYTHON_VERSION_REQUIRED" ]]; then
    echo "ERROR: Python version must be $PYTHON_VERSION_REQUIRED or higher. Found $PYTHON_VERSION."
    exit 1
fi

read -p "Should this script now install standard python and git versions? Choose no if they are already installed. (Enter 'y' or 'n' for yes or no): " INSTALL_STANDARD

if [[ "$INSTALL_STANDARD" == "y" ]]; then
    echo "Installing standard python and git versions..."
    
    # install python, pip, venv and git
    sudo apt install python3 python3-pip python3-venv
    sudo apt install libjpeg-dev # required for pillow

    sudo apt install git
else
    echo "Skipping installation of standard python and git versions. Ending script."
    exit 0
fi

# check if git is installed
if ! command -v git &> /dev/null; then
    echo "ERROR: git is not installed."
    exit 1
fi

# setup git repo
git clone $REPO_LINK
# check if the repo was cloned successfully
if [ $? -ne 0 ]; then
    echo "ERROR: failed to clone the repository."
    exit 1
fi
cd $REPO_FOLDER_NAME

# setup virtual environment
python3 -m venv env
source env/bin/activate

cd src

if [[ "$SETUP_TYPE" == "rc" ]]; then
    touch on_rc.txt
    pip install -r requirements_rc.txt
elif [[ "$SETUP_TYPE" == "ve" ]]; then
    touch on_vehicle.txt
    pip install -r requirements.txt
fi

read -p "Should this script now write a sample config file for the default hardware? Can be changed later by editing the json file in $REPO_FOLDER_NAME/src/config/ and restarting the service with sudo systemctl restart $SERVICE_NAME.  (Enter 'y' or 'n' for yes or no): " WRITE_CONFIG


if [[ "$WRITE_CONFIG" != "y" ]]; then
    echo "Skipping writing sample config file. \n WARNING: The service WILL FAIL TO START until a valid config file is created. See $REPO_FOLDER_NAME/src/config/README.md for more information."
else
    read -p "Type in the ssid of the wifi network you want the script to connect the system to (e. g. hotspot of vehicle or groundstation). Leave blank for the currently connected network : " WIFI_SSID
    if [[ -n "$WIFI_SSID" ]]; then
        read -p "Type in the password of the wifi network: " WIFI_PASSWORD
    else
        # get current ssid and password
        WIFI_SSID=$(iwgetid -r)
        WIFI_PASSWORD=$(sudo grep -r "^psk=" /etc/NetworkManager/system-connections/ | grep "$WIFI_SSID" | cut -d '=' -f2) # FIXME: debug this
    fi

    # write standard config
    cat >config/conf.json << EOL
{
    "vehicle" : {
        "type" : "car",
        "name" : "clara_simulator"
    },
    "program" : {
        "debug": true,
        "headless": false
    },
    "connection" : {
        "type" : "wifi",
        "interface" : "auto",
        "ssid" : "${WIFI_SSID}",
        "password" : "${WIFI_PASSWORD}"
    },
    "input" : {
        "lib" : "inputs"
    },
    "communication" : {
        "encoding" : {
            "ABS_RZ" : "acc",
            "ABS_Z" : "dcc",
            "ABS_X" : "str",
            "BTN_TR" : "ems"
        },
        "encoding_norm" : {
            "ABS_RZ" : 255,
            "ABS_Z" : 255,
            "ABS_X" : 65535
        }
    },
    "gui" : {
        "encoding" : {
            "BTN_START" : "gui_menu",
            "BTN_NORTH" : "gui_select",
            "BTN_SOUTH" : "gui_back",
            "ABS_HAT0Y" : "gui_du",
            "ABS_HAT0X" : "gui_rl"
        }
    }
}

EOL
    echo "Wrote file to $REPO_FOLDER_NAME/src/config/conf.json"
fi

# TODO: enable i2c driver https://luma-oled.readthedocs.io/en/latest/hardware.html#i2c
sudo usermod -a -G i2c $USER
sudo apt-get install i2c-tools

# go back to the beginning
cd ../..

# Create systemd service file for running the app as a daemon
cat <<EOF | sudo tee $SERVICE_PATH > /dev/null  
[Unit]
Description=Tubs API Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)/$REPO_FOLDER_NAME/src
ExecStart=$(pwd)/$REPO_FOLDER_NAME/env/bin/python3 $(pwd)/$REPO_FOLDER_NAME/src/run.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "Service $SERVICE_NAME has been created and started."
echo "Setup completed successfully. Rebooting the system..."

# Reboot the system
sudo reboot now

