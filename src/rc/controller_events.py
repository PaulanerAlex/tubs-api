from inputs import get_gamepad
from tools.config_handler import ConfigHandler
from multiprocessing import Pipe
from inputs import UnpluggedError
from config.config import HEADLESS_MODE, DEBUG_MODE
from tools.logger import Logger, log_print

class ControllerEvents:
    def __init__(self, mp_connect_com=None, mp_connect_gui=None, glob_qu=None):
        self.mp_connect_com = mp_connect_com
        self.mp_connect_gui = mp_connect_gui
        self.glob_qu = glob_qu
        self.cnf = ConfigHandler(communication=True)
        self.log = Logger(__name__)

    def loop_until_event(self): # TODO: remove unnessary function
        """
        Loop until an event is received from the controller.
        Should be called in an own process.
        Returns the status and the event dictionary.
        """
        while True:
            synced, ev_dict, ev_dict_gui = self.get_controller_event()
            return synced, ev_dict, ev_dict_gui

    def get_controller_event(self):
        '''
        Get the controller event and return the event type and state.
        The event type is one of the following:
        - 'Sync': The event is a sync event.
        - 'Absolute': The event is a pressed continous state trigger / a moved joystick.
        - 'Key': The event is a pressed two state button.
        The state is the state of the event.
        '''
        try:
            events = get_gamepad()
        except UnpluggedError:
            return False, {'unplugged': True}, {'unplugged': True}
        ev_dict = {}
        ev_dict_gui = {}
        for event in events:
            try:
                code, max_val = self.cnf.get_com_encoding(event.code)
                ev_dict[code] = event.state / max_val if max_val else event.state
                # TODO: add timestamp
            except KeyError:
                pass
            
            if not HEADLESS_MODE:
                try:
                    code_gui = self.cnf.get_gui_encoding(event.code)
                    ev_dict_gui[code_gui] = event.state
                except KeyError:
                    continue

        # replace gui updates with the local ones from controller if debugging without Vehicle
        if DEBUG_MODE and not HEADLESS_MODE:
            ev_dict_gui.update(ev_dict)

        return True, ev_dict, ev_dict_gui

    @log_print
    def event_loop(self):
        '''
        the event loop for controller events. Sends the events to the mp_connect pipe.
        '''

        while True:

            status, ev_dict, ev_dict_gui = self.loop_until_event()

            # check if the process should be terminated
            try:
                gui_msg = self.glob_qu.get(block=False)
                if DEBUG_MODE:
                    self.log.debug_plain(f' Received message from gui: {gui_msg}')
                if gui_msg.get('terminate', False):
                    self.glob_qu.put(gui_msg)
                    return
            except Exception: # if the queue is empty, just continue
                pass

            # display unplugged message if unplugged
            if not status and ev_dict.get('unplugged', False) == True:
                self.log.warning('Controller unplugged')                
                if not HEADLESS_MODE:
                    self.mp_connect_gui.send(ev_dict_gui)

                while True:
                    status, ev_dict, ev_dict_gui = self.loop_until_event()
                    if ev_dict.get('unplugged', False) == False:
                        break
                
                self.log.info('Controller plugged in')

            if ev_dict.__len__() > 0:
                self.mp_connect_com.send(ev_dict)

            if ev_dict_gui.__len__() > 0 and not HEADLESS_MODE:
                self.mp_connect_gui.send(ev_dict_gui)

if __name__ == "__main__":
    ControllerEvents().loop_until_event()
