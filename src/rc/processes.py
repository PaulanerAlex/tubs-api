from multiprocessing import Process, Pipe, Queue
from rc.controller_events import ControllerEvents
from tools.communication import Communication
from config.config import COMMUNICATION_KEY, HEADLESS_MODE
from rc.gui import GUI
from tools.commander import restart_program, run_shell_command

def start_com_process(mp_connect_sub, mp_connect_pub, glob_qu):
    """
    Start the communication process.
    """

    com = Communication(key=COMMUNICATION_KEY, mp_connect_sub=mp_connect_sub, mp_connect_pub=mp_connect_pub, glob_qu=glob_qu)

    com.pub_loop()

def start_proc():
    child_conn_pub, parent_conn_pub = Pipe()
    conn_sub = Queue()
    child_conn_gui, parent_conn_gui = Pipe()
    glob_qu = Queue()

    input = ControllerEvents(mp_connect_com=parent_conn_pub, mp_connect_gui=parent_conn_gui, glob_qu=glob_qu)

    if not HEADLESS_MODE:
        # gui process
        gui_proc = Process(target=GUI().gui_proc_loop_car, args=(child_conn_gui, conn_sub, glob_qu))
        gui_proc.start()

    # communication process
    com_proc = Process(target=start_com_process, args=(conn_sub, child_conn_pub, glob_qu))
    com_proc.start()

    # input process in main process until terminated by user in the gui
    input.event_loop()

    if not HEADLESS_MODE:
        gui_proc.join()  # Wait for GUI process to finish
    com_proc.join()  # Wait for communication process to finish

    new_conf = glob_qu.get(False).get('new_config', False) # TODO: implement in other process
    if new_conf:
        new_conf = [new_conf]
        restart_program(new_conf)
    
    run_shell_command('shutdown now') # Restart the service to apply new configuration

    