import zenoh
from config.config import IS_RC
from tools.messenger import Messenger

class Communication:
    def __init__(self, key: str):
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

        return head, status, name, timestamp, args, kwargs, message_body     

# TODO finish implementing