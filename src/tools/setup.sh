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

# keep-alive: update existing `sudo` time stamp until the script finishes
sudo -v
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# check if the system is Raspberry Pi OS 32-bit
if [[ "$(uname -m)" == "armv7l" && -f /etc/os-release && "$(grep 'Raspbian' /etc/os-release)" && "$SETUP_TYPE" == "rc"]]; then
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
if [[ "$(printf '%s\n' "$PYTHON_VERSION_REQUIRED" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
    echo "ERROR: Python version must be greater than 3.10. Found $PYTHON_VERSION."
    exit 1
fi

# check if git is installed
if ! command -v git &> /dev/null; then
    echo "ERROR: git is not installed."
    exit 1
fi

read -p "Should this script now install standart python and git versions and try to work with them? (Enter 'y' or 'n' for yes or no): " INSTALL_STANDARD

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
    touch src/on_rc.txt
    pip install -r requirements_rc.txt # TODO: change to uv, pip crashes on rpi zero 2w most certainly because of the low memory
elif [[ "$SETUP_TYPE" == "ve" ]]; then
    touch src/on_vehicle.txt
    pip install -r requirements.txt # TODO: change to uv, pip crashes on rpi zero 2w most certainly because of the low memory
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


