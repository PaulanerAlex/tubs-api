import os
from tools.commander import run_shell_command as cmd
from tools.timers import timer


def network_init():
    """
    Initialize the network.
    """
    # connect to wifi from config if not already connected to this network
    ssid, password, interface = ConfigHandler().get_wifi_config()
    net = NetworkHandler(ssid=ssid, password=password, interface=interface)
    current_ssid, current_interface = net.get_wifi_connection()
    if not current_ssid == ssid and current_interface == interface: 
        net.connect_to_network()

class NetworkHandler:
    def __init__(self, *args, **kwargs):
        self.password = kwargs['password']
        self.interface = kwargs['interface']
        self.ssid = kwargs['ssid']

    def get_available_networks(self):
        """
        Get the available networks (using iwlist command)
        Returns None if something goes wrong.
        """
        command = """sudo iwlist wlp2s0 scan | grep -ioE 'ssid:"(.*{}.*)'"""
        result = cmd(command.format(self.ssid))

        if not result:
            # TODO: change following to logger
            print("No networks found or error in command")
            return None

        if "Device or resource busy" in result:
            return None
        else:
            ssid_list = [item.lstrip('SSID:').strip('"\n') for item in result]
            print(f"Successfully get ssids {str(ssid_list)}")
    
    @timer
    def connect_to_network(self, ssid):
        """
        Connect to the given network.
        """
        command = f"nmcli d wifi connect {self.ssid} password {self.password} iface {self.interface}"
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
        
    def get_wifi_connection(self):
        command = "nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device"
        output = cmd(command)
        
        if not output:
            return None, None

        for line in output.split('\n'):
            parts = line.split(':')
            if len(parts) >= 4 and parts[1] == 'wifi' and parts[2] == 'connected':
                interface = parts[0]
                ssid = parts[3]
                return interface, ssid

        return None, None

