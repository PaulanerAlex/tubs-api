import zenoh
from config.config import IS_RC, COMMUNICATION_KEY, IS_VEHICLE, DEBUG_MODE, HEADLESS_MODE, PING_SEND_INTERVAL, SUB_TIMEOUT
from tools.messenger import Messenger
from multiprocessing import Pipe
from tools.config_handler import ConfigHandler
from functools import partial
import time
from tools.timers import Timer


def sub_savety_interval(func):
    def wrapper(*args, **kwargs):
        self = args[0]
        if self.tm is None:
            self.tm = Timer(start=True)
        self.tm.interval() # update the last interval time to the current time
        output = func(*args, **kwargs)
        return output
    return wrapper

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
        self.tm = None

    def pub_loop(self):
        """
        Loop to keep the process alive and handle incoming messages. Use in own thread / process.
        """
        tm = Timer(start=True)
        pressed_time = None
        while True:
            
            # send ping if the last message was sent more than PING_SEND_INTERVAL seconds ago so constant upstream is ensured
            if time.time() - tm.last_interval_time < time.timedelta(seconds=PING_SEND_INTERVAL):
                msg = self.msgr.ping_message(tm.last_interval_time)
                self.publish_com_msg(msg)

            # check if there are messages in the pipe to send
            if not self.mp_connect_pub.poll(1):                    
                continue

            msg = self.mp_connect_pub.recv()

            pressed_time = msg.get('time')
            if pressed_time:
                msg = msg.pop('time') 

            if msg.get('terminate'):
                print('Communication process terminated.') # TODO: change to logger
                self.session.close()
                exit(0)

            msg = dict(msg) # unnessecary, but validate message, if not valid, it raises an error
            msg = self.msgr.format_message(-1, pressed_time if pressed_time is not None else tm.last_interval_time, '', head=0, log=False, **msg)

            print(f'communication msg after formatting: {msg}') # TODO: change to logger but at a better place

            if DEBUG_MODE: # for debugging, pipe the send messages to the incoming messages
                if self.mp_connect_sub:
                    self.mp_connect_sub.put({'msg': msg})
                else:
                    print(f'communication message received: {msg}') # TODO: change to logger

            if self.mp_connect_sub is not None and not HEADLESS_MODE: # send send frequency to gui
                self.mp_connect_sub.put({'!gui_send_freq': tm.get_refresh_rate()})
            
            self.publish_com_msg(msg)
            tm.interval()

    def sub_loop(self):
        '''
        Keeps process alive.
        Incoming messages are handled in the listener_callback function.
        '''
        while True:
            # FIXME: check if this method works with the listener callbacks
            if self.tm is None:
                time.sleep(0.001)
                continue
            if self.tm.last_interval_time - time.time() > time.timedelta(seconds=PING_SEND_INTERVAL):
                self.mp_connect_sub.send({'ems':1}) # send emergency stop if no message was received for a while
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
    
    @sub_savety_interval
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

        # TODO: check if incoming time or timestamp is too old, if so, send emeregency stop. Maybe another place is better

        if func:
            func(head=head, status=status, name=name, timestamp=timestamp, args=args, kwargs=kwargs, message_body=message_body)
            return True

        raise NotImplementedError('No function or queue passed to listener_callback. Please pass a function or queue that handles the message or that messages can be send to.')

    @sub_savety_interval
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