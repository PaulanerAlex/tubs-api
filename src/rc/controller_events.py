from inputs import get_gamepad
from tools.config_handler import ConfigHandler
from multiprocessing import Pipe

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
                status = True
                return status, ev_dict
            if event_type in ev_dict.keys():
                status = True
                return ev_dict
            if event_type == 'unplugged':
                return status, ev_dict

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
            except KeyError:
                continue

        # TODO: add support for buttons
        return synced, ev_dict


if __name__ == "__main__":
    ControllerEvents().loop_until_event()
