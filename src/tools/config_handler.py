import json
import config.config as cnf

def init_globals(path):
    pass # TODO: implement

class ConfigHandler:
    
    def __init__(self, path=None, communication:bool=False):
        '''
        uses path from config, if path not provided
        '''
        if not path:
            self.path = cnf.CONF_JSON_PATH
        else:
            self.path = path

        if communication:
            self.com_map = self._get_content['communication']['encoding']
            self.com_norm_map = self._get_content['communication']['encoding_norm']
   
    @property
    def _get_content(self):
        with open(self.path) as file:
            return(json.load(file))

    def get_com_encoding(self, input_key):
        '''
        returns the controller specific communication encoding for a given input key
        '''
        
        com_map = self._get_content['communication']['encoding'] if not self.com_map else self.com_map
        com_norm_map = self._get_content['communication']['encoding_norm'] if not self.com_norm_map else self.com_norm_map

        # TODO: add support for buttons
        if input_key in com_map.keys():
            norm_val = com_norm_map[input_key] if input_key in com_norm_map.keys() else None
            return com_map[input_key], norm_val 
        else:
            raise KeyError(f'Key {input_key} not found in communication encoding dictionary')        

    def get_wifi_config(self):
        '''
        returns the wifi config parameters
        '''
        try:
            conf_map = self._get_content['connection']
        except KeyError:
            raise KeyError('No connection config found in config file')

        if conf_map['type'] == 'wifi':
            ssid = conf_map['ssid']
            password = conf_map['password']
            interface = conf_map['interface']
            return ssid, password, interface
        else:
            raise ValueError('No wifi config found in config file')
        
    def get_vehicle_config(self): # TODO: write wrapper for all functions
        '''
        returns the vehicle config parameters
        '''
        try:
            conf_map = self._get_content['vehicle']
        except KeyError:
            raise KeyError('No vehicle config found in config file')
        
        vehicle_type = conf_map['vehicle_type']
        name = conf_map['name']
        return vehicle_type, name

    # TODO: write function to change config
        
            
            