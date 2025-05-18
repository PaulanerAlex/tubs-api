import multiprocessing as mp
from vehicle.processes import start_proc


if __name__ == "__main__":
    start_proc()

# TODO: check if on_vehicle or on_rc exists, and if not create the files (user did not use the setup script) before getting global vars from config.py

