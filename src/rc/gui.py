from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
from config.config import VEH_TYPE, DEBUG_MODE, CONF_JSON_PATH_LIST, I2C_ADDRESS, I2C_PORT
from tools.commander import run_shell_command as cmd
import time
from tools.logger import log_print, Logger

def _screen_prep(func):
    """
    Prepare the screen for display.
    """
    def wrapper(*args, **kwargs):
        self = args[0]
        if self.redraw:
            self.display.clear()
        output = func(*args, **kwargs)
        self.display.display(output)
        return output
    return wrapper


class GUI:
    def __init__(self, i2c_port=I2C_PORT, i2c_address=I2C_ADDRESS):
        serial = i2c(port=i2c_port, address=i2c_address)
        self.display = ssd1306(serial)
        self.height = self.display.height
        self.text_height = self.height / 6
        self.width = self.display.width
        self.redraw = False
        self.menu_state = None
        self.homescreen = 'data_screen_car' if VEH_TYPE == 'car' else ''
        self.menu_options = {
            'recieving view' : self.display_com_msg_view,
            'change config file' : self.display_change_config_view,
            'shutdown' : self.display_shutdown_view,
            'toggle ssh' : self.display_toggle_ssh_view,
        }
        self.mp_connect = None
        self.mp_connect_com = None
        self.glob_qu = None
        self.terminate = False
        self.log = Logger(__name__)

    @log_print
    def gui_proc_loop_car(self, mp_connect, mp_connect_com, glob_qu):
        """
        main loop to refresh the screen.
        """
        self.mp_connect = mp_connect
        self.mp_connect_com = mp_connect_com
        self.glob_qu = glob_qu
        unplugged = False
        self.display.clear()
        acc = 0
        dcc = 0
        steer = 0
        freq = 0.0

        self.display_text('waiting for input...')

        while True:
            if not self.menu_state:
                self.menu_state = self.homescreen
            
            # Drain the queue to get the latest message
            latest_data = None
            
            while mp_connect.poll():
                latest_data = mp_connect.recv()


            # Drain the queue to get the latest message
            data_com = None
            while True:
                try:
                    item = mp_connect_com.get(block=False)
                    data_com = item
                except Exception:  # queue is empty
                    break

            if latest_data:
                data = latest_data
                if data.get('unplugged') == True:
                    self.display_text('Controller unplugged')
                    unplugged = True
                    continue
                elif data.get('gui_menu'):
                    self.menu_state = 'options_menu'
                    self.display_options_menu()
                    if self.terminate:
                        return
                elif unplugged:
                    self.display_text('Controller plugged in')
                    time.sleep(1)
                    unplugged = False
                acc = data.get('acc', acc)
                dcc = data.get('dcc', dcc)
                steer = data.get('str', steer)
            
            if unplugged:
                continue

            if data_com:
                freq = data_com.get('!gui_send_freq', freq)

            self.display_data_screen_car(0 + acc - dcc, steer, {'frq': f'{freq}Hz' if freq else 'N/A', 'acc': acc.__round__(1), 'dcc': dcc.__round__(1), 'str': steer.__round__(1)})

                    
    def display_options_menu(self):
        '''
        Displays the options available from the data view screen,
        name in the button encodings should be 'menu'
        '''

        selected_index = self.menu_loop(list(self.menu_options.keys()))
        
        if selected_index is None:
            return

        list(self.menu_options.values())[selected_index]() # call the function associated with the selected option 

    def display_com_msg_view(self):
        '''
        Displays the communication message view screen.
        '''
        if DEBUG_MODE:
            from tools.messenger import Messenger as msgr

        msgs = []
        while True:
            if self.mp_connect_com is None or self.mp_connect is None:
                raise NotImplementedError('Something went wrong, mp_connect_com or mp_connect is None')

            try:
                msg = self.mp_connect_com.get(block=False)
            except Exception:
                msg = None
            
            latest_data = None

            while self.mp_connect.poll():
                latest_data = self.mp_connect.recv()

            if latest_data and latest_data.get('gui_back'):
                return

            if not msg:
                self.display_text("No msg to display")
                continue
            
            if not DEBUG_MODE:
                msgs.append(msg['message_body'])
            else:
                if msg.get('msg'):
                    head, status, name, timestamp, args, kwargs, message_body = msgr(name='').parse_message(msg.get('msg'), log=False)
                    msgs.append(kwargs)

            self.display_msg_view(messages=msgs)
    
    def display_change_config_view(self):
        '''
        Change the config file, on which the system is parameterized.
        '''
        
        options = CONF_JSON_PATH_LIST

        selected_index = self.menu_loop(options)
        
        if selected_index is None:
            return

        # terminate all processes to restart whole program with the new config
        self.glob_qu.put({'terminate': True, 'new_config': options[selected_index]})  
        self.terminate = True

    def display_shutdown_view(self):
        '''
        Displays the shutdown view.
        '''

        self.display_text('Press select to shut down, then pls wait at least 10 seconds...')
        time.sleep(1)  # wait a bit to show the message

        # terminate all processes
        self.glob_qu.put({'terminate': True})
        self.terminate = True

    def display_toggle_ssh_view(self):
        '''
        Toggles the ssh server on or off.
        '''
        self.display_text('Toggling ssh server...')
        is_active = cmd('sudo systemctl is-active ssh', capture_exit_code_3=True)
        if is_active is None:
            self.display_text('Command failed, check the logs')
        elif is_active.strip() == 'active':
            command_result = cmd('sudo systemctl stop ssh')
            self.log.info(f'Stopped ssh server by user: {command_result}')
            self.display_text('SSH server turned off')
        else:
            command_result = cmd('sudo systemctl start ssh')
            self.log.info('Started ssh server by user')
            self.display_text('SSH server turned on')
        time.sleep(2)

    def menu_loop(self, options):
        '''
        Main loop for the menu, which allows to navigate through the menu options.
        Wraps the display_menu function and handles the input from the controller.
        '''
        selected_index = 0

        def __add_ind(ind):
            return ind - 1 if ind > 0 else len(options) - 1
        
        def __sub_ind(ind):
            return ind + 1 if ind < len(options) - 1 else 0
        
        while True:
            if self.mp_connect.poll():
                data = self.mp_connect.recv()
                for key, value in data.items():
                    
                    if key == 'gui_ud' and value > 0:
                        selected_index = __add_ind(selected_index)
                    elif key == 'gui_ud' and value < 0:
                        selected_index = __sub_ind(selected_index)
                    elif key == 'gui_du' and value > 0:
                        selected_index = __sub_ind(selected_index)
                    elif key == 'gui_du' and value < 0:
                        selected_index = __add_ind(selected_index)

                    if key == 'gui_select':
                        return selected_index

                    if key == 'gui_back':
                        self.menu_state = None
                        return None

            self.display_menu(options, selected=selected_index)

    @_screen_prep
    def display_text(self, text, position=None, font=None):
        """
        Display text on the screen. If position is None, center the text.
        Automatically wraps text if it exceeds the screen width.
        """
        image = Image.new("1", (self.width, self.height))
        draw = ImageDraw.Draw(image)
        if not font:
            font = ImageFont.load_default()

        lines = self.wrap_text(text, font, self.width)

        # Calculate line height
        bbox = font.getbbox("A")
        line_height = (bbox[3] - bbox[1]) + 2

        total_text_height = line_height * len(lines)
        if not position:
            y = (self.height - total_text_height) // 2
        else:
            y = position[1]

        for line in lines:
            bbox = font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            if not position:
                x = (self.width - text_width) // 2
            else:
                x = position[0]
            draw.text((x, y), line, font=font, fill=255)
            y += line_height

        return image


    def wrap_text(self, text, font, max_width):
        '''
        Split text into lines that fit the width of the screen.
        '''
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = font.getbbox(test_line)
            line_width = bbox[2] - bbox[0]
            if line_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    @_screen_prep
    def display_msg_view(self, messages=None, font=None):
        """
        Displays the message view screen. Shows the last messages at the bottom.
        """
        if messages is None:
            messages = []
            
        if font is None:
            font = ImageFont.load_default()

        image = Image.new("1", (self.width, self.height))
        draw = ImageDraw.Draw(image)

        # Calculate line height
        bbox = font.getbbox("A") 
        line_height = (bbox[3] - bbox[1]) + 2

        max_lines = self.height // line_height
        # Get the last max_lines messages
        visible_msgs = messages[-max_lines:]

        # Draw messages from bottom up
        for i, msg in enumerate(reversed(visible_msgs)):
            y = self.height - (i + 1) * line_height
            draw.text((2, y), str(msg), font=font, fill=255)

        return image

    @_screen_prep
    def display_menu(self, options, font=None, selected=0):
        """
        Display a menu on the screen.
        """
        if not font:
            font = ImageFont.load_default()
        image = Image.new("1", (self.width, self.height))
        bbox = font.getbbox("A")
        line_height = (bbox[3] - bbox[1]) + 2
        draw = ImageDraw.Draw(image)
        
        if font is None:
            font = ImageFont.load_default()

        max_lines = self.height // line_height
        start_index = max(0, selected - max_lines // 2)
        visible_options = options[start_index:start_index + max_lines]

        for i, option in enumerate(visible_options):
            y = i * line_height
            if start_index + i == selected:
                draw.rectangle((0, y, self.width, y + line_height), outline=255, fill=255)
                draw.text((2, y), option, font=font, fill=0)
            else:
                draw.text((2, y), option, font=font, fill=255)
        return image

    @_screen_prep
    def display_data_screen_car(self, accel: float, steer: float, vals: dict):
        '''
        Displays a widget with a circle and a dot representing the steering and acceleration values
        and some additional values.
        '''
        image = Image.new("1", (self.width, self.height), 0)
        draw = ImageDraw.Draw(image)

        # Circle properties
        radius = min(self.width, self.height) // 2 - 4
        center_x = self.width // 4
        center_y = self.height // 2

        # Draw circle
        draw.ellipse([
            (center_x - radius, center_y - radius),
            (center_x + radius, center_y + radius)
        ], outline=1)

        # Clamp steering and acceleration to [-1.0, 1.0]
        steering = max(-1.0, min(1.0, steer))
        acceleration = max(-1.0, min(1.0, accel))

        # Compute dot position
        dot_x = center_x + int(steering * radius)
        dot_y = center_y - int(acceleration * radius)  # y-axis is inverted

        # Draw dot
        dot_radius = 2
        draw.ellipse([
            (dot_x - dot_radius, dot_y - dot_radius),
            (dot_x + dot_radius, dot_y + dot_radius)
        ], fill=1)

        pos = 0
        for key, value in vals.items():
            draw.text((self.width * 0.55, pos), f"{str(key)}:{str(value)}", fill=1)
            pos += self.text_height
        return image

    @_screen_prep
    def display_image(self, path):
        """
        Display an image on the screen. Should be 1-bit and 128x64.
        """
        return Image.open(path).convert("1")

if __name__ == "__main__":
    gui = GUI()
    while True:
        in_1 = input('> ')
        in_2 = input('> ')
        gui.display_data_screen_car(float(in_1), float(in_2), {'bat': '3.2V', 'mod':'man', 'st':'ok'})