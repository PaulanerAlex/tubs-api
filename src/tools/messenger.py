from datetime import datetime
from config.config import DEBUG_MODE

class Messenger:

    def __init__(self, name: str):
        self.name = name
        self.status_def = ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL']
        self.head_def = ['DO', 'SET', 'GET', 'LOG', 'PING']

    def format_message(self, status: int, time: datetime, message: str, head: int = None, log: bool = False, *args, **kwargs):
        '''
        Format the message in format:
        `[status][name][time][arg1]...[argN][key1=value1]...[keyN=valueN] body` for log or
        `[head][time][arg1]...[argN][key1=value1]...[keyN=valueN]` for commands.
        The message has has a header and a body.
        Parses every argument and adds it to the header.
        The message should not contain any brackets, as they are used for formatting.
        If the keyword argument log=True is passed, the message returned won't contain the 'head' and 'name' of the header.
        The message contains the time header argument, which is encoded in the ISO 8601 format.
        the head can be one of the following.
        
        This should not be shown in the log database, for that, use
        - 0: `DO` (for commands)
        - 1: `SET` (for setting configuration parameters)
        - 2: `GET` (for getting messages)
        - 3: `LOG` (for logging)
        - 4: `PING` (for ping messages)
        
        the status can be one of the following:
        - -1: `NONE`
        - 0: `INFO`
        - 1: `DEBUG`
        - 2: `WARNING`
        - 3: `ERROR`
        - 4: `CRITICAL`
        '''

        # TODO: find schema for telemetry message

        if '[' in message or ']' in message:
            raise ValueError("Message should not contain '[' or ']'")

        # add head to header # FIXME: there cold be a boolian error here
        if not log:
            head = f'[{self.head_def[head]}]'
            name = ''
            status = ''
        else:
            head = ''
            name = f'[{str(self.name).upper()}]' 
            status = f'[{self.status_def[status]}]'

        # TODO: add timestamp before sending to be as exact as possible
        # TODO: add micro-, milliseconds to timestamp, remove year, month, day
        if time and isinstance(time, datetime):
            timestamp = f'[{time.strftime("%dT%H%M%S%f")}]'
        elif time and isinstance(time, float):
            timestamp = f'[{datetime.fromtimestamp(time).strftime("%dT%H%M%S%f")}]'
        elif time and isinstance(time, str):
            try:
                timestamp = f'[{datetime.strptime(time, "%dT%H%M%S%f").strftime("%dT%H%M%S%f")}]'
            except ValueError:
                timestamp = f'[{datetime.now().strftime("%dT%H%M%S%f")}]'
        else:
            timestamp = f'[{datetime.now().strftime("%dT%H%M%S%f")}]'

        # construct header
        header = f'{head}{status}{name}{timestamp}'
        for arg in args:
            if any(str(arg) in s for s in ['[', ']', '=']):
                raise ValueError('Argument should not contain \'=\'')
            header = header.__add__(f'[{str(arg).upper()}]')

        for key, value in kwargs.items():
            if any(str(key) in s for s in ['[', ']', '=']) or any(str(value) in s for s in ['[', ']', '=']):
                raise ValueError('Keyword argument should not contain \'=\'')
            header = header.__add__(f'[{str(key).upper()}={str(value)}]')
        
        message = ' ' + message if message else ''

        message = f'{header}{message}'

        if log and status == 1 and DEBUG_MODE:
            print(message)

        return message
    
    def ping_message(self, time: datetime = None):
        '''
        Returns a ping message in the format:
        `[head][time]`
        The head is always `PING`.
        '''
        return self.format_message(-1, datetime.now() if time is None else time, '', head=4, log=False)

    def parse_message(self, message: str, log: bool = False):
        '''
        Parses the message and gives every argument in the header and the message as seperate values.
        '''

        message = message.split(']')
        args = []
        kwargs = {}
        header_formatted = []

        if not message[-1:][0].startswith('['): # check if there is a trailing message
            message_body = message[-1][1:]  # get the message, remove the leading whitespace
            header_fields = message[:-1] # removes last field, which is the message
        else:
            message_body = ''
            header_fields = message

        for field in header_fields:
            header_formatted.append(field[1:])  # [1:] removes the leading '['
        
        # TODO: move the next part into the main header_formatted parsing loop because this is just garbage programming
        i = 0
        if not log:
            head = header_formatted[i]
            i += 1
            status = ''
            name = ''
        else:
            head = ''
            status = header_formatted[i]
            i += 1 
            name = header_formatted[i]
            i += 1

        timestamp = datetime.strptime(header_formatted[i], "%dT%H%M%S%f")
        
        for ii in range(0, i):
            header_formatted.pop(ii) # remove the header fields except the args and kwargs

        for i in range(0, len(header_formatted)): # parse args and kwargs
            if '=' in header_formatted[i]:
                key, value = header_formatted[i].split('=')
                kwargs[key] = value
            else:
                args.append(header_formatted[i])
        
        for char in message_body[1:]: # parse the message
            if '=' in char:
                key, value = char.split('=')
                kwargs[key] = value
            else:
                args.append(char)
        
        return head, status, name, timestamp, args, kwargs, message_body

    def parse_log_message(self, message: str):
        # TODO: implement
        pass

    def parse_commands_sim(self, kwargs):
        
        command_dict = {}
        
        if 'ACC' in kwargs.keys():
            amount = float(kwargs['ACC'])
            command_dict['accelerate'] = amount / 30
        if 'DCC' in kwargs.keys():
            amount = float(kwargs['DCC'])
            command_dict['brake'] = amount / 15
        if 'STR' in kwargs.keys():
            amount = float(kwargs['STR'])
            if amount < 0:
                command_dict['steer_left'] = amount * 10
            elif amount > 0:
                command_dict['steer_right'] = amount * 10

        # TODO: add support for buttons
        # TODO: make ems work
        # TODO: send back heartbeat message (evtl. in reply to the ping message) 

        return command_dict    