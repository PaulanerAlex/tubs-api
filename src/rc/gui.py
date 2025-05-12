from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont



class GUI:
    def __init__(self, i2c_port=1, i2c_address=0x3C):
        serial = i2c(port=i2c_port, address=i2c_address)
        self.display = ssd1306(serial)
        self.heigth = self.display.height
        self.width = self.display.width

    def display_text(self, text, position=(0, 0), font=None):
        self.display.clear()
        width = self.display.width
        height = self.display.height
        image = Image.new("1", (width, height))
        draw = ImageDraw.Draw(image)
        if font is None:
            font = ImageFont.load_default()
        draw.text(position, text, font=font, fill=255)
        self.display.display(image)

        def display_menu(self, options, font=None, selected_index=0):
            image = Image.new("1", (self.width, self.height))
            draw = ImageDraw.Draw(image)
            
            if font is None:
                font = ImageFont.load_default()

            line_height = font.getsize("A")[1] + 2
            max_lines = height // line_height
            start_index = max(0, selected_index - max_lines // 2)
            visible_options = options[start_index:start_index + max_lines]

            for i, option in enumerate(visible_options):
                y = i * line_height
                if start_index + i == selected_index:
                    draw.rectangle((0, y, width, y + line_height), outline=255, fill=255)
                    draw.text((2, y), option, font=font, fill=0)
                else:
                    draw.text((2, y), option, font=font, fill=255)

            self.display.display(image)
