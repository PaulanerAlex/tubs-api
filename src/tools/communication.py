import zenoh
from config.config import IS_RC, COMMUNICATION_KEY, IS_VEHICLE, DEBUG_MODE
from tools.messenger import Messenger
from multiprocessing import Pipe
from tools.config_handler import ConfigHandler
from functools import partial

class Communication:
    def __init__(self, key: str = '', mp_connect_sub = None, mp_connect_pub = None, listener_func=None):
        self.key = key
        self.session = zenoh.open(zenoh.Config())
        
        # declare pub and sub endings
        # TODO: change to global suffix for vehicle
        if IS_RC:
            pub_ending = 'to_veh'
            sub_ending = 'to_rc'
        else:
            pub_ending = 'to_rc'
            sub_ending = 'to_veh'

        global IS_VEHICLE, DEBUG_MODE

        self.pub = self.session.declare_publisher(str(self.key) + f'/{pub_ending}')
        if IS_VEHICLE and DEBUG_MODE:
            self.sub = self.session.declare_subscriber(str(self.key) + f'/{sub_ending}', self.listener_callback_sim)
        else:
            self.sub = self.session.declare_subscriber(str(self.key) + f'/{sub_ending}', partial(self.listener_callback, func=listener_func))

        global COMMUNICATION_KEY

        if not COMMUNICATION_KEY:
            type, COMMUNICATION_KEY = ConfigHandler().get_vehicle_config() # TODO: refactor, so that every config value gets imported at init and by ConfigHandler
        
        self.msgr = Messenger(COMMUNICATION_KEY) # name will not be shown in the communication messages
        self.mp_connect_sub = mp_connect_sub
        self.mp_connect_pub = mp_connect_pub

    def pub_loop(self):
        """
        Loop to keep the process alive and handle incoming messages. Use in own thread / process.
        """
        while True:
            if self.mp_connect_pub.poll(1):
                msg = self.mp_connect_pub.recv()

                print(f'communication message for sending befor formatting: {msg}')

                msg = dict(msg) # validate message, if not valid, it raises an error                    
                msg = self.msgr.format_message(0, -1, msg.get('time'), '', log=False, **msg.pop('time'))

                print(f'communication msg after formatting: {msg}')

                self.publish_com_msg(msg)

    def publish_com_msg(self, msg: str):
        """
        Publish a communication message to the specified key.
        """ 
        
        try:
            self.pub.put(msg)
            print('communication message sent.')
            return True
        except Exception as e:
            # TODO: log error
            return False
        
    def listener_callback(self, sample: zenoh.Sample, func=None):
        '''
        Callback function for the subscriber. Runs the function passed as argument
        '''
        msg = sample.payload.to_string()
        (
        head,
        status,
        name,
        timestamp,
        args,
        kwargs,
        message_body
        ) = self.msgr.parse_message(msg)

        if func:
            func(head=head, status=status, name=name, timestamp=timestamp, args=args, kwargs=kwargs, message_body=message_body)


    def listener_callback_sim(self, sample: zenoh.Sample):
        '''
        Callback function for the subscriber. Parses the 'command' message and passes the arguments to the simulation pipe.
        '''
        msg = sample.payload.to_string()
        (
        head,
        status,
        name,
        timestamp,
        args,
        kwargs,
        message_body
        ) = self.msgr.parse_message(msg)

        if self.mp_connect_sub is not None:
            # TODO: parse config
            # print(f'msg received: {msg}')
            commands = self.msgr.parse_commands_sim(kwargs)
            self.mp_connect_sub.send(commands)