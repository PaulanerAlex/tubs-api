from inputs import get_gamepad


TRIGGER_MAX = 2**8 - 1
STICK_MAX = 2**16 - 1

class ControllerEvents:

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
            elif event.ev_type == 'Absolute':
                if event.code in ['ABS_Z', 'ABS_RZ']: # TODO: get trigger names from config.json
                    ev_dict[event.code] = event.state / TRIGGER_MAX
                elif event.code in ['ABS_X', 'ABS_Y', 'ABS_RX', 'ABS_RY']: # TODO: get stick names from config.json
                    ev_dict[event.code] = event.state / STICK_MAX
                else:
                    ev_dict[event.code] = event.state
            elif event.ev_type == 'Key':
                ev_dict[event.code] = True if event.state == 1 else False
        return synced, ev_dict


if __name__ == "__main__":
    ControllerEvents().loop_until_event()
