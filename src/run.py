from config.config import IS_RC, IS_VEHICLE
if IS_RC:
    from rc.entrypoint import init
    from rc.processes import start_proc
if IS_VEHICLE:
    from rc.entrypoint import init
    from vehicle.processes import start_proc

if __name__ == "__main__":
    # TODO: add initialization code for connection establishment etc
    init() # runs once
    start_proc() # runs continously

# TODO: check if on_vehicle or on_rc exists, and if not create the files (user did not use the setup script) before getting global vars from config.py

