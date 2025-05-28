from inputs import get_gamepad
from tools.config_handler import ConfigHandler
from multiprocessing import Pipe
from inputs import UnpluggedError
from config.config import HEADLESS_MODE, TERMINATE

_TRIGGER_MAX = 2**8 - 1
_STICK_MAX = 2**16 - 1

class ControllerEvents:
    def __init__(self, mp_connect_com=None, mp_connect_gui=None):
        self.mp_connect_com = mp_connect_com
        self.mp_connect_gui = mp_connect_gui
        self.cnf = ConfigHandler(communication=True)

    def loop_until_event(self):
        """
        Loop until an event is received from the controller.
        Should be called in an own process.
        Returns the status and the event dictionary.
        """
        while True:
            synced, ev_dict, ev_dict_gui = self.get_controller_event()
            if ev_dict.get('unplugged'):
                raise UnpluggedError
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
            return False, {'unplugged': True}, {}
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

        if not HEADLESS_MODE:
            ev_dict_gui.update(ev_dict)    

        return True, ev_dict, ev_dict_gui

    def event_loop(self):
        '''
        the event loop for controller events. Sends the events to the mp_connect pipe.
        '''
        unplugged = False
        while True:
            if TERMINATE:
                return

            status, ev_dict, ev_dict_gui = self.loop_until_event()
            
            # display unplugged message if unplugged
            if not status:
                if ev_dict.get('unplugged') == True and not unplugged: # to display only once
                    # TODO: log this
                    print('controller unplugged')
                    self.mp_connect_com.send(ev_dict)
                    if not HEADLESS_MODE:
                        self.mp_connect_gui.send(ev_dict_gui)
                    unplugged = True
                    continue

                if unplugged:
                    continue
                
                print('something went wrong') # TODO: change to logger

            if unplugged and status:
                print(f"controller plugged in")
                unplugged = False

            if ev_dict.__len__() > 0:
                self.mp_connect_com.send(ev_dict)

            if ev_dict_gui.__len__() > 0 and not HEADLESS_MODE:
                self.mp_connect_gui.send(ev_dict_gui)

if __name__ == "__main__":
    ControllerEvents().loop_until_event()
