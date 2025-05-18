from multiprocessing import Process, Pipe
from rc.controller_events import ControllerEvents

def start_proc():
    child_conn, parent_conn = Pipe()

    ControllerEvents(mp_connect=parent_conn)

    # TODO: start controller process
    # TODO: start communication process
    pass