from multiprocessing import Process, Pipe
from rc.controller_events import ControllerEvents
from tools.communication import Communication
from config.config import COMMUNICATION_KEY, HEADLESS_MODE
import time
from rc.gui import GUI

def start_com_process(mp_connect_sub, mp_connect_pub):
    """
    Start the communication process.
    """

    print("Starting communication process...")

    com = Communication(key=COMMUNICATION_KEY, mp_connect_sub=mp_connect_sub, mp_connect_pub=mp_connect_pub)

    com.pub_loop()

def start_proc():
    child_conn_pub, parent_conn_pub = Pipe()
    child_conn_sub, parent_conn_sub = Pipe()
    child_conn_gui, parent_conn_gui = Pipe()

    input = ControllerEvents(mp_connect_com=parent_conn_pub, mp_connect_gui=parent_conn_gui)

    if not HEADLESS_MODE:
        # gui process
        gui_proc = Process(target=GUI().gui_proc_loop_car, args=(child_conn_gui,))
        gui_proc.start()

    # communication process
    com_proc = Process(target=start_com_process, args=(child_conn_sub, child_conn_pub))
    com_proc.start()

    # input process in main process
    input.event_loop()

    # TODO: start gui process
    # TODO: check if the pipe buffer will never be full, so the child process is faster