from multiprocessing import Process, Pipe
from tools.debug_sim import CarSimulation
from tools.communication import Communication
from rc.controller_events import ControllerEvents
from config.config import COMMUNICATION_KEY
import time


def start_com_process(mp_connect_sub, mp_connect_pub):
    """
    Start the communication process.
    """

    com = Communication(key=COMMUNICATION_KEY, mp_connect_sub=mp_connect_sub, mp_connect_pub=mp_connect_pub)
    com.sub_loop()

def debug_control_process(conn): # for controlling without wireless connection
    
    time.sleep(1)  # Let simulation start
    
    controller = ControllerEvents()
    steer = 0
    acc = 0
    dec = 0
    while True:
        status, ev_dict = controller.loop_until_event() # FIXME: this call should not be blocking the loop when no button was changed but some are still pressed. should be no problem when implemented telemetry which is different process
        if not status:
            pass # TODO: handle unplugged event
        if 'ABS_Z' in ev_dict.keys():
            dec = ev_dict['ABS_Z']
        if 'ABS_RZ' in ev_dict.keys():
            acc = ev_dict['ABS_RZ']
        if 'ABS_X' in ev_dict.keys():
            steer = ev_dict['ABS_X']

        if dec != 0:
            conn.send({'brake' : dec / 100})
        if acc != 0:
            conn.send({'accelerate' : acc / 100})
        if steer > 0:
            conn.send({'steer_left' : steer / 10})
        elif steer < 0:
            conn.send({'steer_right' : steer})
    
    # conn.send('exit')

def start_proc():
    # Create Pipes for communication between processes
    parent_conn_sub, child_conn_sub = Pipe()
    parent_conn_pub, child_conn_pub = Pipe()

    # Start communication process
    p = Process(target=start_com_process, args=(parent_conn_sub, child_conn_pub))
    p.start()

    # Start simulation in main process # TODO: eventually implement log publisher for simulation
    sim = CarSimulation(pipe_conn=child_conn_sub, acceleration=0.2, steering_angle_deg=10)
    sim.run()

    p.join()  # Wait for control process to finish