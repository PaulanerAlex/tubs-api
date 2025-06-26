import zenoh
from config.config import IS_RC, COMMUNICATION_KEY, IS_VEHICLE, DEBUG_MODE, HEADLESS_MODE, PING_SEND_INTERVAL, SUB_TIMEOUT
from tools.messenger import Messenger
from functools import partial
import time
from datetime import datetime
from tools.timers import Timer
from tools.logger import log_print
from tools.logger import Logger

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
    def __init__(self, key: str = '', mp_connect_sub = None, mp_connect_pub = None, listener_func=None, glob_qu=None):
        self.key = key
        self.session = zenoh.open(zenoh.Config())
        
        # declare pub and sub endings
        if IS_RC:
            pub_ending = 'to_veh'
            sub_ending = 'to_rc'
        else:
            pub_ending = 'to_rc'
            sub_ending = 'to_veh'

        if key == '':
            key = COMMUNICATION_KEY

        pub_topic = str(self.key) + f'/{pub_ending}'
        sub_topic = str(self.key) + f'/{sub_ending}'

        self.pub = self.session.declare_publisher(pub_topic)
        
        if IS_VEHICLE and DEBUG_MODE:
            self.sub = self.session.declare_subscriber(sub_topic, self.listener_callback_sim)
        elif IS_RC and DEBUG_MODE: # for debugging, incoming messages will be outgoing messages
            self.sub = None
        else:
            self.sub = self.session.declare_subscriber(sub_topic, partial(self.listener_callback, func=listener_func))
        
        self.msgr = Messenger(COMMUNICATION_KEY) # name will not be shown in the communication messages
        self.mp_connect_sub = mp_connect_sub
        self.mp_connect_pub = mp_connect_pub
        self.glob_qu = glob_qu
        self.tm = None
        self.log = Logger(__name__)

    @log_print
    def pub_loop(self):
        """
        Loop to keep the process alive and handle incoming messages. Use in own thread / process.
        """
        tm = Timer(start=True)
        pressed_time = None
        ems = False
        while True:

            # send ping if the last message was sent more than PING_SEND_INTERVAL seconds ago so constant upstream is ensured
            if time.time() - tm.last_interval_time > PING_SEND_INTERVAL:
                msg = self.msgr.ping_message()
                self.publish_com_msg(msg)
                if self.mp_connect_sub is not None and not HEADLESS_MODE: # send send frequency to gui
                    self.mp_connect_sub.put({'!gui_send_freq': tm.get_refresh_rate()})
                tm.interval()

            try:
                gui_msg = self.glob_qu.get(block=False)
                if gui_msg.get('terminate'):
                    self.glob_qu.put(gui_msg)
                    if DEBUG_MODE:
                        self.log.debug_plain(' Received termination signal from gui.')
                    self.session.close()
                    return
            except Exception: # if the queue is empty, just continue
                pass

            # check if there are messages in the pipe to send
            if not self.mp_connect_pub.poll():                    
                continue

            msg = self.mp_connect_pub.recv()

            pressed_time = msg.get('time')
            if pressed_time:
                msg = msg.pop('time') 

            msg = dict(msg) # unnessecary, but validate message, if not valid, it raises an error
            
            if msg.get('ems', 0) == 1: # emergency stop
                self.log.warning('Sending emergency stop.')
                ems = True
            elif ems == True:
                ems = False

            msg = self.msgr.format_message(-1, pressed_time if pressed_time is not None else datetime.now(), '', head=0, log=False, **msg)

            if DEBUG_MODE:
                self.log.debug_plain(f'[SENDING]{msg}')

                if self.mp_connect_sub: # for debugging, pipe the send messages to the incoming messages
                    self.mp_connect_sub.put({'msg': msg})

            if self.mp_connect_sub is not None and not HEADLESS_MODE: # send send frequency to gui
                self.mp_connect_sub.put({'!gui_send_freq': tm.get_refresh_rate()})
            
            status = self.publish_com_msg(msg)

            if ems and status:
                raise RuntimeError('Emergency stop sent but the vehicle can not be reached, terminating communication so that program has to be restarted.')

            tm.interval()

    def sub_loop_sim(self):
        '''
        Keeps process alive.
        Incoming messages are handled in the listener_callback function.
        '''
        if not self.tm:
            self.tm = Timer(start=True)
        while True:
            if self.tm is None:
                time.sleep(0.001)
                continue
            if time.time() - self.tm.last_interval_time > SUB_TIMEOUT:
                self.log.debug('No message received for a while, sending emergency stop.')
                self.mp_connect_sub.send({'ems':1}) # send emergency stop if no message was received for a while
                return
            time.sleep(0.1)

    def publish_com_msg(self, msg: str):
        """
        Publish a communication message to the specified key.
        """ 
        try:
            self.pub.put(msg)
            return True
        except Exception as e:
            self.log.error(f'Error while publishing message: {e}')
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
        if DEBUG_MODE:
            self.log.debug_plain(f'[RECEIVED]{sample.payload.to_string()}')
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
            commands = self.msgr.parse_commands_sim(kwargs)
            self.mp_connect_sub.send(commands)