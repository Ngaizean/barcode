"""Rendering code for EAN-13 barcode"""

from functools import reduce
from io import BytesIO

from PIL import Image, ImageFont, ImageDraw

from pystrich.fonts import get_font
# maps bar width against font size
font_sizes = {
    1: 8,
    2: 14,
    3: 18,
    4: 24
}


class EAN13Renderer:
    """Rendering class - given the code and corresponding
    bar encodings and guard bars,
    it will add edge zones and render to an image"""

    width = None
    height = None

    def __init__(self, code, left_bars, right_bars, guards):
        self.code = code
        self.left_bars = left_bars
        self.right_bars = right_bars
        self.guards = guards

    def get_pilimage(self, bar_width,fontSize=20,spacing=1.0):
        def sum_len(total, item):
            """add the length of a given item to the total"""
            return total + len(item)

        num_bars = (7 * 12) + reduce(sum_len, self.guards, 0)

        quiet_width = bar_width * 9
        image_width = (2 * quiet_width) + (num_bars * bar_width)
        image_height = image_width // 2

        img = Image.new('L', (image_width, image_height), 255)

        class BarWriter:
            """Class which moves across the image, writing out bars"""
            def __init__(self, img):
                self.img = img
                self.current_x = quiet_width
                self.symbol_top = quiet_width // 2

            def write_bar(self, value, full=False):
                """Draw a bar at the current position,
                if the value is 1, otherwise move on silently"""

                # only write anything to the image if bar value is 1
                bar_height = int(image_height * (full and 0.9 or 0.8))
                if value == 1:
                    for ypos in range(self.symbol_top, bar_height):
                        for xpos in range(self.current_x,
                                          self.current_x + bar_width):
                            img.putpixel((xpos, ypos), 0)
                self.current_x += bar_width

            def write_bars(self, bars, full=False):
                """write all bars to the image"""
                for bar in bars:
                    self.write_bar(int(bar), full)

        # Draw the bars
        writer = BarWriter(img)
        writer.write_bars(self.guards[0], full=True)
        writer.write_bars(self.left_bars)
        writer.write_bars(self.guards[1], full=True)
        writer.write_bars(self.right_bars)
        writer.write_bars(self.guards[2], full=True)

        # Draw the text
        font_size = font_sizes.get(bar_width, 24)

        # font = get_font("courR", font_size)
        font = ImageFont.truetype("arial.ttf", fontSize)
        draw = ImageDraw.Draw(img)

        # 第一个数字保持不变
        draw.text((1 * bar_width, int(image_height * 0.785)),
                  self.code[0], font=font)

        # 为第2-7位数字（中间组）设置间距
        digit_spacing = spacing  # 数字间距倍数，大于1会增加间距
        base_pos = 13 * bar_width
        for i in range(1, 7):
            # 计算每个数字的位置，加入额外间距
            pos_x = base_pos + (i-1) * font_size * digit_spacing
            draw.text((pos_x, int(image_height * 0.785)),
                      self.code[i], font=font)

        # 为第8-13位数字（右侧组）设置间距  
        base_pos = 59 * bar_width
        for i in range(7, 13):
            pos_x = base_pos + (i-7) * font_size * digit_spacing
            draw.text((pos_x, int(image_height * 0.785)),
                      self.code[i], font=font)

        self.width = image_width
        self.height = image_height
        return img

    def write_file(self, filename, bar_width, fontSize=20, spacing=1.0):
        """Write barcode data out to image file
        filename - the name of the image file
        bar_width - the desired width of each bar"""
        img = self.get_pilimage(bar_width, fontSize=fontSize, spacing=spacing)
        img.save(filename, "PNG")

    def get_imagedata(self, bar_width, fontSize=20, spacing=1.0):
        """Write the matrix out as PNG to a bytestream"""
        buffer = BytesIO()
        img = self.get_pilimage(bar_width, fontSize=fontSize, spacing=spacing)
        img.save(buffer, "PNG")
        return buffer.getvalue()
