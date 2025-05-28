import zenoh
from config.config import IS_RC, COMMUNICATION_KEY, IS_VEHICLE, DEBUG_MODE
from tools.messenger import Messenger
from multiprocessing import Pipe
from tools.config_handler import ConfigHandler
from functools import partial
import time
from tools.timers import Timer

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

        pub_topic = str(self.key) + f'/{pub_ending}'
        sub_topic = str(self.key) + f'/{sub_ending}'

        self.pub = self.session.declare_publisher(pub_topic)
        
        if IS_VEHICLE and DEBUG_MODE:
            self.sub = self.session.declare_subscriber(sub_topic, self.listener_callback_sim)
        elif IS_RC and DEBUG_MODE: # for debugging, incoming messages will be outgoing messages
            self.sub = None
        else:
            self.sub = self.session.declare_subscriber(sub_topic, partial(self.listener_callback, func=listener_func))

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
        tm = Timer(start=True)
        while True:
            if self.mp_connect_pub.poll(1):
                msg = self.mp_connect_pub.recv()

                time = msg.get('time')
                if time:
                    msg = msg.pop('time') 

                if msg.get('terminate'):
                    print('Communication process terminated.') # TODO: change to logger
                    self.session.close()
                    exit(0)

                msg = dict(msg) # unnessecary, but validate message, if not valid, it raises an error
                msg = self.msgr.format_message(0, -1, time, '', log=False, **msg)

                print(f'communication msg after formatting: {msg}') # TODO: change to logger but at a better place

                if DEBUG_MODE: # for debugging, pipe the send to the incoming messages
                    if self.mp_connect_sub:
                        self.mp_connect_sub.put(msg)
                    else:
                        print(f'communication message received: {msg}') # TODO: change to logger

                if self.mp_connect_sub is not None: # send send frequency to gui
                    tm.interval()
                    self.mp_connect_sub.put({'gui_send_freq': tm.get_refresh_rate()})
                
                self.publish_com_msg(msg)



    def sub_loop(self):
        '''
        Keeps process alive.
        Incoming messages are handled in the listener_callback function.
        '''
        while True:
            time.sleep(0.001) # TODO: find a better solution to keep the process alive

    def publish_com_msg(self, msg: str):
        """
        Publish a communication message to the specified key.
        """ 
        try:
            self.pub.put(msg)
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

        if self.mp_connect_sub:
            self.mp_connect_sub.put({
                'head': head,
                'status': status,
                'name': name,
                'timestamp': timestamp,
                'args': args,
                'kwargs': kwargs,
                'message_body': message_body,
                'encoded': msg
            })
            return True

        if func:
            func(head=head, status=status, name=name, timestamp=timestamp, args=args, kwargs=kwargs, message_body=message_body)
            return True

        raise NotImplementedError('No function or queue passed to listener_callback. Please pass a function or queue that handles the message or that messages can be send to.')

    def listener_callback_sim(self, sample: zenoh.Sample):
        '''
        Callback function for the subscriber. Parses the 'command' message and passes the arguments to the simulation pipe.
        '''
        print(f'communication message received: {sample.payload.to_string()}')
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