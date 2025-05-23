from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
from config.config import RUNTIME_VARS

def _screen_prep(func):
    """
    Prepare the screen for display.
    """
    def wrapper(*args, **kwargs):
        self = args[0]
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

    @_screen_prep
    def display_text(self, text, position=(0, 0), font=None):
        image = Image.new("1", (self.width, self.height))
        draw = ImageDraw.Draw(image)
        if font is None:
            font = ImageFont.load_default()
        draw.text(position, text, font=font, fill=255)
        return image

    @_screen_prep
    def display_menu(self, options, font=None, selected_index=0):
        image = Image.new("1", (self.width, self.height))
        draw = ImageDraw.Draw(image)
        
        if font is None:
            font = ImageFont.load_default()

        line_height = font.getsize("A")[1] + 2
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
    def display_homescreen(self):
        if RUNTIME_VARS['on_vehicle']:
            text = "Vehicle Mode"

if __name__ == "__main__":
    gui = GUI()
    gui.display_text('Test', (50, 50))
