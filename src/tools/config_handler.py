import json
import pathlib as pl
import config.config as cnf
import os

class ConfigHandler:
    
    def __init__(self, path=None):
        '''
        uses path from config, if path not provided
        '''
        if not path:
            path = cnf.CONF_JSON_PATH
        else:
            self.path = path
        
    def get_content(self):
        with open(self.path) as file:
            return(json.loads(file))
    
    def get_com_encoding(self):
        '''
        returns the controller specific communication encoding dictionary
        '''
        # TODO: implement
        pass

    def get_wifi_config(self):
        '''
        returns the wifi config dictionary
        '''
        # TODO: implement
        pass


    # TODO: write function to change config
        
            
            