import zenoh
from config.config import IS_RC, COMMUNICATION_KEY
from tools.messenger import Messenger
from multiprocessing import Pipe
import threading

def start_com_process(conn):
    """
    Start the communication process.
    """

    Communication(key=COMMUNICATION_KEY, mp_connect=conn)

    # Keep the process alive by waiting for the connection to close
    # This will block until the other end of the Pipe is closed
    try:
        while True:
            if conn.poll(1):
                msg = conn.recv()
                # TODO: check if this is efficient like this
                # Optionally handle messages from the main process here
            else:
                # Sleep briefly to avoid busy waiting
                threading.Event().wait(0.1)
    except (EOFError, KeyboardInterrupt):
        pass

class Communication:
    def __init__(self, key: str = '', mp_connect = None):
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

        self.pub = self.session.declare_publisher(str(self.key) + f'/{pub_ending}')
        self.sub = self.session.declare_subscriber(str(self.key) + f'/{sub_ending}', self.listener_callback)
        self.msgr = Messenger('com') # name will not be shown in the communication messages
        self.mp_connect = mp_connect

    def publish_com_msg(self, msg: str):
        """
        Publish a communication message to the specified key.
        """ 
        
        msg = self.msgr.format_message(msg)
        try:
            self.pub.put(msg)
            return True
        except Exception as e:
            # TODO: log error
            return False
        
    def listener_callback(self, sample: zenoh.Sample):
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

        if self.mp_connect is not None:
            # TODO: parse config
            print('msg received')
            self.mp_connect.send({'accelerate' : 0.1 / 100})
        
        return head, status, name, timestamp, args, kwargs, message_body


# TODO finish implementing