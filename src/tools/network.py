import os
from src.tools.commander import run_shell_command as cmd

class NetworkHandler:
    def __init__(self, *args, **kwargs):
        self.server_name = kwargs['server_name']
        self.password = kwargs['password']
        self.interface_name = kwargs['interface']
        self.ssid = kwargs['ssid']
        self.main_dict = {}

    def get_available_networks(self):
        """
        Get the available networks (using iwlist command)
        Returns None if something goes wrong.
        """
        command = """sudo iwlist wlp2s0 scan | grep -ioE 'ssid:"(.*{}.*)'"""
        result = cmd(command.format(self.server_name))

        if not result:
            # TODO: change following to logger
            print("No networks found or error in command")
            return None

        if "Device or resource busy" in result:
            return None
        else:
            ssid_list = [item.lstrip('SSID:').strip('"\n') for item in result]
            print("Successfully get ssids {}".format(str(ssid_list)))

    def connect_to_network(self, ssid):
        """
        Connect to the given network.
        """
        command = f"nmcli d wifi connect {self.ssid} password {self.password} iface {self.interface_name}"
        self.ssid = ssid
        # FIXME: debug the following
        try:
            if cmd(command) != 0: # run the command and check connection
                raise Exception()
            # TODO: change following to logger
            print(f"Connected to ssid : {self.ssid}")
            return True
        except Exception as e:
            # TODO: change following to logger
            print(f"Couldn't connect to ssid : {self.ssid}. {e}")
            return False
