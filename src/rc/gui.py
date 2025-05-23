from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont

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
    def __init__(self, i2c_port=1, i2c_address=0x3C): # TODO: add global var for i2c adress that is collected dynamically
        serial = i2c(port=i2c_port, address=i2c_address)
        self.display = ssd1306(serial)
        self.height = self.display.height
        self.width = self.display.width
        self.redraw = False
        
    def gui_proc_loop_car(self, mp_connect):
        """
        main loop to refresh the screen.
        """
        self.display.clear()
        acc = 0
        dcc = 0
        steer = 0
        while True:
            if mp_connect.poll():
                data = mp_connect.recv()
                acc = data.get('acc', acc)
                dcc = data.get('dcc', dcc)
                steer = data.get('str', steer)
                if data.get('unplugged') == True: # FIXME: this has to be implemented in the other process
                    self.display_text('Controller unplugged')
                else:
                    acc = data['acc']
                    self.display_data_screen_car(0 + acc - dcc, steer, {'bat': '3.2V', 'mod':'man', 'st':'ok'})
            else:
                self.display_text('Waiting for data...') # TODO: change this...

    @_screen_prep
    def display_text(self, text, position=None, font=None):
        """
        Display text on the screen. If position is None, center the text.
        """
        image = Image.new("1", (self.width, self.height))
        draw = ImageDraw.Draw(image)    
        if not font:
            font = ImageFont.load_default()
        if not position:
            # Use font.getbbox for Pillow >=8.0.0, fallback to getsize for older versions
            try:
                bbox = font.getbbox(text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except AttributeError:
                text_width, text_height = font.getsize(text)
            x = (self.width - text_width) // 2
            y = (self.height - text_height) // 2
            position = (x, y)
        draw.text(position, text, font=font, fill=255)
        return image

    @_screen_prep
    def display_menu(self, options, font=None, selected_index=0):
        """
        Display a menu on the screen.
        """
        image = Image.new("1", (self.width, self.height))
        try:
            bbox = font.getbbox("A")
            line_height = (bbox[3] - bbox[1]) + 2
        except AttributeError:
            line_height = font.getsize("A")[1] + 2
        draw = ImageDraw.Draw(image)
        
        if font is None:
            font = ImageFont.load_default()

        max_lines = self.height // line_height
        start_index = max(0, selected_index - max_lines // 2)
        visible_options = options[start_index:start_index + max_lines]

        for i, option in enumerate(visible_options):
            y = i * line_height
            if start_index + i == selected_index:
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
            pos += self.height / 6
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