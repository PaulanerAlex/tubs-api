

class Messenger:

    def __init__(self, name: str):
        self.name = name
        self.status_def = ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL']

    def format_message(self, status: int, message: str, *args, **kwargs):
        """
        Format the message in format: [status][name][arg1]...[argN][key1=value1]...[keyN=valueN] message
        parses every argument and adds it to the header.
        the status can be one of the following:
        - -1: TELEMETRY
        - 0: INFO
        - 1: DEBUG
        - 2: WARNING
        - 3: ERROR
        - 4: CRITICAL
        """

        # TODO: find schema for telemetry message

        if '[' in message or ']' in message:
            raise ValueError("Message should not contain '[' or ']'")

        header = f'[{self.status_def[status]}][{str(self.name).upper()}]'
        for arg in args:
            header.__add__(f'[{str(arg).upper()}]')

        if kwargs:
            for key, value in kwargs.items():
                header.__add__(f'[{str(key).upper()}={str(value)}]')
        
        message = f'{header} {message}'

        return message
    
    def parse_message(self, message: str):
        """
        Parse the message.
        """
        message = message.split(']')
        message = message[-1][1:]  # get the message, remove the leading whitespace
        args = []
        kwargs = {}
        header_formatted = []

        header_fields = message[:-1]

        for field in header_fields:
            header_formatted.append(field[1:])  # [1:] removes the leading '['
        
        status = header_formatted[0] 
        name = header_formatted[1]
        
        for i in range(2, len(header_formatted)):
            if '=' in header_formatted[i]:
                key, value = header_formatted[i].split('=')
                kwargs[key] = value
            else:
                args.append(header_formatted[i])
        
        for item in message[1:]:
            if '=' in item:
                key, value = item.split('=')
                kwargs[key] = value
            else:
                args.append(item)
        
        return status, name, args, kwargs, message