from inputs import get_gamepad
from tools.config_handler import ConfigHandler
from multiprocessing import Pipe
from inputs import UnpluggedError

_TRIGGER_MAX = 2**8 - 1
_STICK_MAX = 2**16 - 1

class ControllerEvents:
    def __init__(self, mp_connect=None):
        self.mp_connect = mp_connect
        self.cnf = ConfigHandler()

    def loop_until_event(self, event_type=None):
        """
        Loop until an event is received from the controller.
        Should be called in an own process.
        Returns the status and the event dictionary.
        """
        while True:
            synced, ev_dict = self.get_controller_event()
            status = False
            if not synced:
                return status, ev_dict
            if not event_type:
                if ev_dict.get('unplugged'):
                    raise UnpluggedError
                status = True
                return status, ev_dict
            if event_type in ev_dict.keys():
                status = True
                return ev_dict

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
        except events.UnpluggedError:
            print("Controller unplugged")
            return False, {'unplugged': True}
        ev_dict = {}
        synced = True # TODO: check if this is reasonable
        for event in events:
            if event.ev_type == 'Sync':
                synced = True
                continue
            try:
                code, max_val = self.cnf.get_com_encoding(event.code)
                ev_dict[code] = event.state / max_val if max_val else event.state
                # TODO: add timestamp
            except KeyError:
                continue

        # TODO: add support for two state buttons
        return synced, ev_dict

    def event_loop(self, mp_connect):
        '''
        the event loop for controller events. Sends the events to the mp_connect pipe.
        '''
        while True:
            try:
                status, ev_dict = self.loop_until_event()
            except UnpluggedError:
                print("Controller unplugged") # TODO: handle unplugged event
                continue
            
            if not status:
                print("something went wrong") # TODO: handle other problems
                continue
            if ev_dict.__len__() > 0:
                print(ev_dict)
                mp_connect.send(ev_dict)
            else:
                print("No event received") # TODO: handle no event received

if __name__ == "__main__":
    ControllerEvents().loop_until_event()
